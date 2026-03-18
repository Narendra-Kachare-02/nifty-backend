from __future__ import annotations

from ..exceptions import NiftySnapshotNotFound
from ..models import OptionChainSnapshot


def getLatestOptionChainSnapshot(symbol: str = "NIFTY", expiryDate: str | None = None) -> OptionChainSnapshot:
    """
    Single responsibility: fetch latest option-chain snapshot (optional expiry filter).
    """
    qs = OptionChainSnapshot.objects.filter(symbol=symbol).order_by("-captured_at")
    if expiryDate:
        qs = qs.filter(expiryDate=expiryDate)

    snapshot = qs.first()
    if not snapshot:
        raise NiftySnapshotNotFound("No option chain snapshot found.")
    return snapshot

