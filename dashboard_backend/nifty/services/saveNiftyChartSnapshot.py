from __future__ import annotations

from django.utils import timezone

from ..config import NSE_INDEX_NAME
from ..models import NiftyChartSnapshot


def saveNiftyChartSnapshot(payload: dict, flag: str) -> NiftyChartSnapshot:
    """
    Single responsibility: persist a chart payload as a snapshot.
    """
    return NiftyChartSnapshot.objects.create(
        captured_at=timezone.now(),
        indexName=NSE_INDEX_NAME,
        flag=flag,
        payload=payload,
    )

