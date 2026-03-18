import logging

from celery import shared_task

from .services import fetchNiftyPayload, saveNiftySnapshot
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

