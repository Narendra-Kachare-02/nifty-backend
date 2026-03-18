from __future__ import annotations

from typing import Any

import requests

from ..config import NSE_BASE_URL, NSE_DEFAULT_HEADERS, NSE_NIFTY_50_URL
from ..exceptions import NseFetchException, NseParseException


def fetchNiftyPayload(timeout_seconds: int = 10) -> dict[str, Any]:
    """
    Single responsibility: fetch NSE payload for NIFTY 50 and return parsed JSON.
    """
    session = requests.Session()

    try:
        # Step 1: warm up cookies
        session.get(NSE_BASE_URL, headers=NSE_DEFAULT_HEADERS, timeout=timeout_seconds)

        # Step 2: fetch JSON
        response = session.get(NSE_NIFTY_50_URL, headers=NSE_DEFAULT_HEADERS, timeout=timeout_seconds)
        if response.status_code != 200:
            raise NseFetchException(f"NSE returned status {response.status_code}")

        try:
            payload = response.json()
        except Exception as e:  # noqa: BLE001
            raise NseParseException("Failed to parse NSE JSON") from e

        if not isinstance(payload, dict):
            raise NseParseException("NSE payload is not an object")

        # Minimal shape validation (keep keys same as demo.json)
        if "marketStatus" not in payload or "metadata" not in payload or "data" not in payload:
            raise NseParseException("Missing required keys in NSE payload")

        return payload
    except (NseFetchException, NseParseException):
        raise
    except Exception as e:  # noqa: BLE001
        raise NseFetchException(str(e)) from e

