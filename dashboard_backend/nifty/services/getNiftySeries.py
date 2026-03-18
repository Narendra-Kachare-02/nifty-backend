from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from ..models import NiftySnapshot


RANGE_TO_MINUTES = {
    "15M": 15,
    "30M": 30,
    "1H": 60,
    "1D": 24 * 60,
}


def _extract_last_price(snapshot: NiftySnapshot) -> float | None:
    meta_last = snapshot.metadata.get("last") if isinstance(snapshot.metadata, dict) else None
    if meta_last is not None:
        try:
            return float(meta_last)
        except Exception:  # noqa: BLE001
            pass

    # Fallback to index row inside data list
    if isinstance(snapshot.data, list) and snapshot.data:
        row0 = snapshot.data[0]
        if isinstance(row0, dict) and row0.get("lastPrice") is not None:
            try:
                return float(row0["lastPrice"])
            except Exception:  # noqa: BLE001
                return None
    return None


def getNiftySeries(range_key: str = "1D") -> list[dict[str, float | int]]:
    """
    Single responsibility: return chart-friendly series points for a time window.
    """
    minutes = RANGE_TO_MINUTES.get(range_key.upper(), RANGE_TO_MINUTES["1D"])
    since = timezone.now() - timedelta(minutes=minutes)

    qs = NiftySnapshot.objects.filter(captured_at__gte=since).order_by("captured_at")

    series: list[dict[str, float | int]] = []
    for snap in qs:
        value = _extract_last_price(snap)
        if value is None:
            continue
        series.append({"time": int(snap.captured_at.timestamp()), "value": value})

    return series

