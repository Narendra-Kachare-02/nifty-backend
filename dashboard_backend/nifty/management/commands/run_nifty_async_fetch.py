import asyncio
import logging
import time
from typing import Final

from django.core.management.base import BaseCommand

from dashboard_backend.nifty.tasks import fetchNifty, fetchOptionChain
from dashboard_backend.nifty.utils import isMarketOpenNow

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Run async NIFTY fetch loop (replaces Celery beat)"

    def add_arguments(self, parser) -> None:
        parser.add_argument(
            "--interval-seconds",
            type=int,
            default=60,
            help="How often to attempt fetches (seconds). Default: 60",
        )

    def handle(self, *args, **options) -> None:
        interval_seconds: int = options["interval_seconds"]
        asyncio.run(self._run_forever(interval_seconds=interval_seconds))

    async def _run_forever(self, interval_seconds: int) -> None:
        logger.info("Starting async NIFTY fetch loop interval_seconds=%s", interval_seconds)

        while True:
            tick_start = time.time()
            try:
                # Guard here so we only start work during market hours.
                if isMarketOpenNow():
                    await asyncio.gather(fetchNifty(), fetchOptionChain())
            except Exception:
                logger.exception("Async NIFTY tick failed")

            # Align sleep to the interval boundary to avoid drift.
            elapsed = time.time() - tick_start
            sleep_for = max(0.0, interval_seconds - elapsed)
            # Still keep the loop periodic.
            await asyncio.sleep(sleep_for)

