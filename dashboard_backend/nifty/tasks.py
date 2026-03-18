import logging

from celery import shared_task

from .services import fetchNiftyPayload, fetchOptionChainPayload, saveNiftySnapshot, saveOptionChainSnapshot
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
    market_status = (payload.get("marketStatus") or {}).get("marketStatus")
    logger.info(
        "Saved Nifty snapshot captured_at=%s marketStatus=%s",
        snapshot.captured_at.isoformat(),
        market_status,
    )


@shared_task(name="nifty.fetchOptionChain", ignore_result=True)
def fetchOptionChain():
    """
    Scheduled task: fetch NSE option-chain payload and persist a snapshot.
    Guarded by market hours to avoid NSE calls after close.
    """
    if not isMarketOpenNow():
        return

    payload = fetchOptionChainPayload()
    snapshot = saveOptionChainSnapshot(payload, symbol="NIFTY")

    logger.info(
        "Saved OptionChain snapshot captured_at=%s symbol=%s expiryDate=%s",
        snapshot.captured_at.isoformat(),
        snapshot.symbol,
        snapshot.expiryDate,
    )

