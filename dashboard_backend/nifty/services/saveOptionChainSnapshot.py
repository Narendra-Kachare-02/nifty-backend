from __future__ import annotations

from typing import Any

from django.utils import timezone

from ..models import OptionChainSnapshot


def _get_nearest_expiry(payload: dict[str, Any]) -> str | None:
    records = payload.get("records") or {}
    expiry_dates = records.get("expiryDates")
    if isinstance(expiry_dates, list) and expiry_dates:
        first = expiry_dates[0]
        return first if isinstance(first, str) else None
    return None


def saveOptionChainSnapshot(payload: dict[str, Any], symbol: str = "NIFTY", expiryDate: str | None = None) -> OptionChainSnapshot:
    """
    Single responsibility: persist option-chain payload as a snapshot.
    """
    expiry = expiryDate or _get_nearest_expiry(payload)

    snapshot = OptionChainSnapshot.objects.create(
        captured_at=timezone.now(),
        symbol=symbol,
        expiryDate=expiry,
        payload=payload,
    )
    return snapshot

