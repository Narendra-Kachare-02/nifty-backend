from __future__ import annotations

from typing import Any

import requests

from ..config import (
    NSE_BASE_URL,
    NSE_DEFAULT_HEADERS,
    NSE_INDEX_NAME,
    NSE_INDEX_TRACKER_FUNCTION_CHART,
    NSE_INDEX_TRACKER_PATH,
)
from ..exceptions import NseFetchException, NseParseException


def fetchNiftyChartPayload(flag: str, timeout_seconds: int = 10) -> dict[str, Any]:
    """
    Single responsibility: fetch Chart API payload (getIndexChart) for NIFTY 50 + flag.
    """
    session = requests.Session()

    try:
        session.get(NSE_BASE_URL, headers=NSE_DEFAULT_HEADERS, timeout=timeout_seconds)

        url = f"{NSE_BASE_URL}{NSE_INDEX_TRACKER_PATH}"
        params = {"functionName": NSE_INDEX_TRACKER_FUNCTION_CHART, "index": NSE_INDEX_NAME, "flag": flag}
        response = session.get(url, headers=NSE_DEFAULT_HEADERS, params=params, timeout=timeout_seconds)
        if response.status_code != 200:
            raise NseFetchException(f"NSE returned status {response.status_code}")

        try:
            payload = response.json()
        except Exception as e:  # noqa: BLE001
            raise NseParseException("Failed to parse NSE chart JSON") from e

        if not isinstance(payload, dict):
            raise NseParseException("Chart payload is not an object")

        data = payload.get("data")
        if not isinstance(data, dict) or "grapthData" not in data:
            raise NseParseException("Chart payload missing data.grapthData")

        return payload
    except (NseFetchException, NseParseException):
        raise
    except Exception as e:  # noqa: BLE001
        raise NseFetchException(str(e)) from e

