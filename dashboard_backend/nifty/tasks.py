import logging

from celery import shared_task

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


@shared_task(name="nifty.fetchNifty", ignore_result=True)
def fetchNifty():
    """
    Scheduled task: fetch NSE payload and persist a snapshot.
    Guarded by market hours to avoid NSE calls after close.
    """
    if not isMarketOpenNow():
        return

    payload = fetchNiftyPayload()
    snapshot = saveNiftySnapshot(payload)

    # One high-signal log line only.
    idx = payload.get("data")[0] if isinstance(payload.get("data"), list) and payload.get("data") else {}
    market_status = "Open" if idx else "Unknown"
    logger.info(
        "Saved Nifty snapshot captured_at=%s marketStatus=%s",
        snapshot.captured_at.isoformat(),
        market_status,
    )

    # Also capture default chart (1D) for the UI.
    chart_payload = fetchNiftyChartPayload(flag="1D")
    saveNiftyChartSnapshot(chart_payload, flag="1D")


@shared_task(name="nifty.fetchOptionChain", ignore_result=True)
def fetchOptionChain():
    """
    Scheduled task: fetch NSE option-chain payload and persist a snapshot.
    Guarded by market hours to avoid NSE calls after close.
    """
    if not isMarketOpenNow():
        return

    contract = fetchOptionChainContractInfo()
    expiry_dates = contract.get("expiryDates") if isinstance(contract, dict) else None
    expiry = expiry_dates[0] if isinstance(expiry_dates, list) and expiry_dates else None
    if not expiry:
        return

    payload = fetchOptionChainPayload(expiry=expiry)
    snapshot = saveOptionChainSnapshot(payload, symbol="NIFTY", expiryDate=expiry)

    logger.info(
        "Saved OptionChain snapshot captured_at=%s symbol=%s expiryDate=%s",
        snapshot.captured_at.isoformat(),
        snapshot.symbol,
        snapshot.expiryDate,
    )

