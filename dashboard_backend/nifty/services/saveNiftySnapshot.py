from __future__ import annotations

from typing import Any

from django.utils import timezone

from ..models import NiftySnapshot


def saveNiftySnapshot(payload: dict[str, Any]) -> NiftySnapshot:
    """
    Single responsibility: persist a payload as a new snapshot.
    """
    data = payload.get("data") or []
    source_last_update_time = None

    # Prefer the index row's lastUpdateTime when present.
    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
        source_last_update_time = data[0].get("lastUpdateTime") or data[0].get("timestamp")

    snapshot = NiftySnapshot.objects.create(
        captured_at=timezone.now(),
        source_lastUpdateTime=source_last_update_time,
        name=payload.get("name"),
        advance=payload.get("advance") or {},
        timestamp=payload.get("timestamp"),
        marketStatus=payload.get("marketStatus") or {},
        metadata=payload.get("metadata") or {},
        data=data,
    )
    return snapshot

