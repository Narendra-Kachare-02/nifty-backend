from __future__ import annotations

from datetime import datetime, time

import pytz

from ..constants import MARKET_CLOSE_IST, MARKET_OPEN_IST


IST = pytz.timezone("Asia/Kolkata")


def isMarketOpenNow(now_utc: datetime | None = None) -> bool:
    """
    Single responsibility: determine if we're within normal market hours in IST.
    Holidays are intentionally not handled here (can be added later).
    """
    now = now_utc or datetime.utcnow()
    now_ist = now.replace(tzinfo=pytz.UTC).astimezone(IST)

    # Mon–Fri only
    if now_ist.weekday() >= 5:
        return False

    t: time = now_ist.time()
    return MARKET_OPEN_IST <= t <= MARKET_CLOSE_IST

