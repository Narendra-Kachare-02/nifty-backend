import asyncio
import logging
from typing import Any, Callable

from django.db import close_old_connections

from .services import (
    fetchNiftyPayload,
    fetchNiftyChartPayload,
    fetchOptionChainContractInfo,
    fetchOptionChainPayload,
    saveNiftyChartSnapshot,
    saveNiftySnapshot,
    saveOptionChainSnapshot,
)
from .utils import isMarketOpenNow


logger = logging.getLogger(__name__)

def _run_sync_in_thread(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """
    Run a synchronous function inside a worker thread.

    Ensures Django DB connections are fresh in the thread.
    """
    close_old_connections()
    return fn(*args, **kwargs)


async def fetchNifty() -> None:
    """
    Fetch NSE payload and persist snapshots (async wrapper).
    """
    if not isMarketOpenNow():
        return

    payload = await asyncio.to_thread(_run_sync_in_thread, fetchNiftyPayload)
    snapshot = await asyncio.to_thread(_run_sync_in_thread, saveNiftySnapshot, payload)

    # One high-signal log line only.
    idx = payload.get("data")[0] if isinstance(payload.get("data"), list) and payload.get("data") else {}
    market_status = "Open" if idx else "Unknown"
    logger.info(
        "Saved Nifty snapshot captured_at=%s marketStatus=%s",
        snapshot.captured_at.isoformat(),
        market_status,
    )

    # Also capture default chart (1D) for the UI.
    chart_payload = await asyncio.to_thread(
        _run_sync_in_thread, fetchNiftyChartPayload, flag="1D"
    )
    await asyncio.to_thread(
        _run_sync_in_thread, saveNiftyChartSnapshot, chart_payload, flag="1D"
    )


async def fetchOptionChain() -> None:
    """
    Fetch NSE option-chain payload and persist a snapshot (async wrapper).
    """
    if not isMarketOpenNow():
        return

    contract = await asyncio.to_thread(
        _run_sync_in_thread, fetchOptionChainContractInfo
    )
    expiry_dates = contract.get("expiryDates") if isinstance(contract, dict) else None
    expiry = expiry_dates[0] if isinstance(expiry_dates, list) and expiry_dates else None
    if not expiry:
        return

    payload = await asyncio.to_thread(
        _run_sync_in_thread, fetchOptionChainPayload, expiry=expiry
    )
    snapshot = await asyncio.to_thread(
        _run_sync_in_thread,
        saveOptionChainSnapshot,
        payload,
        symbol="NIFTY",
        expiryDate=expiry,
    )

    logger.info(
        "Saved OptionChain snapshot captured_at=%s symbol=%s expiryDate=%s",
        snapshot.captured_at.isoformat(),
        snapshot.symbol,
        snapshot.expiryDate,
    )

