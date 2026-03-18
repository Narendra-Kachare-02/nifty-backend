from __future__ import annotations

from ..exceptions import NiftySnapshotNotFound
from ..models import NiftyChartSnapshot


def getLatestNiftyChartSnapshot(flag: str) -> NiftyChartSnapshot:
    snap = (
        NiftyChartSnapshot.objects.filter(flag=flag)
        .order_by("-captured_at")
        .first()
    )
    if not snap:
        raise NiftySnapshotNotFound("No chart snapshot found.")
    return snap

