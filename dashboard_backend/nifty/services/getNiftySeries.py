from __future__ import annotations

from typing import Any

from ..config import NSE_CHART_FLAGS
from ..exceptions import NseParseException
from .getLatestNiftyChartSnapshot import getLatestNiftyChartSnapshot


def getNiftySeries(range_key: str = "1D") -> dict[str, Any]:
    """
    Single responsibility: convert latest stored chart snapshot into series points.
    Reads from DB only (polling API).
    """
    flag = range_key.upper()
    if flag not in NSE_CHART_FLAGS:
        raise NseParseException(f"Unsupported chart flag: {flag}")

    snap = getLatestNiftyChartSnapshot(flag=flag)
    payload = snap.payload or {}

    data = payload.get("data") if isinstance(payload, dict) else None
    graph = data.get("grapthData") if isinstance(data, dict) else None
    close_price = data.get("closePrice") if isinstance(data, dict) else None

    series = []
    if isinstance(graph, list):
        for row in graph:
            if isinstance(row, list) and len(row) >= 2:
                ts_ms = row[0]
                price = row[1]
                try:
                    series.append({"time": int(int(ts_ms) / 1000), "value": float(price)})
                except Exception:  # noqa: BLE001
                    continue

    return {"range": flag, "series": series, "closePrice": close_price}

