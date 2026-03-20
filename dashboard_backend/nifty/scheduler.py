import asyncio
import fcntl
import logging
import os
import threading
import time
from pathlib import Path

import schedule

from .tasks import fetchNifty, fetchOptionChain
from .utils import isMarketOpenNow

logger = logging.getLogger(__name__)

_LOCK_PATH = Path("/tmp/nifty_scheduler.lock")
_STARTED = False
_START_LOCK = threading.Lock()


def _try_acquire_lock():
    """
    Prevent the scheduler from running multiple times inside the same instance
    (e.g., Gunicorn with multiple workers).
    """
    _LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    f = _LOCK_PATH.open("w")
    try:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        return f  # keep file handle open to hold the lock
    except BlockingIOError:
        f.close()
        return None


def _run_tick() -> None:
    """
    schedule library job (sync). It triggers async work for both fetches.
    """
    if not isMarketOpenNow():
        return

    try:
        async def _main() -> None:
            await asyncio.gather(fetchNifty(), fetchOptionChain())

        asyncio.run(_main())
    except Exception:
        logger.exception("Nifty async fetch tick failed")


def _scheduler_loop(interval_seconds: int) -> None:
    schedule.every(interval_seconds).seconds.do(_run_tick)

    while True:
        try:
            schedule.run_pending()
        except Exception:
            logger.exception("Nifty scheduler run_pending failed")
        time.sleep(1)


def start_nifty_scheduler(interval_seconds: int = 60) -> None:
    """
    Starts the schedule-based scheduler inside the Django web process.

    Gating:
    - Only starts when running behind Render (PORT env var set).
    - File lock ensures only one process runs the scheduler.
    """
    global _STARTED

    # When Django starts during build/migrations, PORT is typically unset.
    if not os.environ.get("PORT"):
        return

    with _START_LOCK:
        if _STARTED:
            return

        lock_handle = _try_acquire_lock()
        if lock_handle is None:
            # Another worker acquired the lock.
            return

        _STARTED = True
        logger.info("Nifty schedule scheduler started interval_seconds=%s", interval_seconds)

        t = threading.Thread(
            target=_scheduler_loop,
            args=(interval_seconds,),
            daemon=True,
            name="nifty-schedule-loop",
        )
        t.start()

