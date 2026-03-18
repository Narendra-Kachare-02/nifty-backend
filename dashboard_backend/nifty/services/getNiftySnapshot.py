from __future__ import annotations

from ..exceptions import NiftySnapshotNotFound
from ..models import NiftySnapshot


def getLatestNiftySnapshot() -> NiftySnapshot:
    """
    Single responsibility: fetch latest snapshot row.
    """
    snapshot = NiftySnapshot.objects.order_by("-captured_at").first()
    if not snapshot:
        raise NiftySnapshotNotFound()
    return snapshot

