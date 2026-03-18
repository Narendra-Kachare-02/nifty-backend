from __future__ import annotations

from typing import Any

import requests

from ..config import NSE_BASE_URL, NSE_DEFAULT_HEADERS, NSE_OPTION_CHAIN_NIFTY_URL
from ..exceptions import NseFetchException, NseParseException


def fetchOptionChainPayload(timeout_seconds: int = 10) -> dict[str, Any]:
    """
    Single responsibility: fetch NSE option chain payload for NIFTY (indices) and return parsed JSON.
    """
    session = requests.Session()

    try:
        session.get(NSE_BASE_URL, headers=NSE_DEFAULT_HEADERS, timeout=timeout_seconds)

        response = session.get(NSE_OPTION_CHAIN_NIFTY_URL, headers=NSE_DEFAULT_HEADERS, timeout=timeout_seconds)
        if response.status_code != 200:
            raise NseFetchException(f"NSE returned status {response.status_code}")

        try:
            payload = response.json()
        except Exception as e:  # noqa: BLE001
            raise NseParseException("Failed to parse NSE option chain JSON") from e

        if not isinstance(payload, dict):
            raise NseParseException("NSE option chain payload is not an object")

        records = payload.get("records")
        if not isinstance(records, dict):
            raise NseParseException("Missing records in option chain payload")

        expiry_dates = records.get("expiryDates")
        data = records.get("data")
        if not isinstance(expiry_dates, list) or not isinstance(data, list):
            raise NseParseException("Missing expiryDates/data in option chain payload")

        return payload
    except (NseFetchException, NseParseException):
        raise
    except Exception as e:  # noqa: BLE001
        raise NseFetchException(str(e)) from e

