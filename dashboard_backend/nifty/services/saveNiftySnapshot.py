from __future__ import annotations

from typing import Any

from django.utils import timezone

from ..models import NiftySnapshot


def saveNiftySnapshot(payload: dict[str, Any]) -> NiftySnapshot:
    """
    Single responsibility: persist a payload as a new snapshot.
    """
    data_list = payload.get("data") or []
    index_row = data_list[0] if isinstance(data_list, list) and data_list and isinstance(data_list[0], dict) else {}

    # Index API uses timeVal on the row.
    source_last_update_time = index_row.get("timeVal")

    snapshot = NiftySnapshot.objects.create(
        captured_at=timezone.now(),
        source_lastUpdateTime=source_last_update_time,
        name=index_row.get("indexName"),
        advance={},  # not provided by this API
        timestamp=index_row.get("timeVal"),
        marketStatus={},  # not provided by this API
        metadata=index_row,  # keep keys as-is from index payload
        data=[],  # constituents not provided here
    )
    return snapshot

