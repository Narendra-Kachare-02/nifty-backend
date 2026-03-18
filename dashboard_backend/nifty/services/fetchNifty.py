from __future__ import annotations

from typing import Any

import requests

from ..config import (
    NSE_BASE_URL,
    NSE_DEFAULT_HEADERS,
    NSE_INDEX_NAME,
    NSE_INDEX_TRACKER_FUNCTION_INDEX,
    NSE_INDEX_TRACKER_PATH,
)
from ..exceptions import NseFetchException, NseParseException


def fetchNiftyPayload(timeout_seconds: int = 10) -> dict[str, Any]:
    """
    Single responsibility: fetch Index API payload (getIndexData) for NIFTY 50.
    """
    session = requests.Session()

    try:
        # Step 1: warm up cookies
        session.get(NSE_BASE_URL, headers=NSE_DEFAULT_HEADERS, timeout=timeout_seconds)

        # Step 2: fetch JSON
        url = f"{NSE_BASE_URL}{NSE_INDEX_TRACKER_PATH}"
        params = {"functionName": NSE_INDEX_TRACKER_FUNCTION_INDEX, "index": NSE_INDEX_NAME}
        response = session.get(url, headers=NSE_DEFAULT_HEADERS, params=params, timeout=timeout_seconds)
        if response.status_code != 200:
            raise NseFetchException(f"NSE returned status {response.status_code}")

        try:
            payload = response.json()
        except Exception as e:  # noqa: BLE001
            raise NseParseException("Failed to parse NSE JSON") from e

        if not isinstance(payload, dict):
            raise NseParseException("NSE payload is not an object")

        # Minimal shape validation (based on docs/indexapi.json)
        data = payload.get("data")
        if not isinstance(data, list) or not data or not isinstance(data[0], dict):
            raise NseParseException("Missing data[0] in index payload")
        if "last" not in data[0] or "previousClose" not in data[0]:
            raise NseParseException("Index payload missing last/previousClose")

        return payload
    except (NseFetchException, NseParseException):
        raise
    except Exception as e:  # noqa: BLE001
        raise NseFetchException(str(e)) from e

