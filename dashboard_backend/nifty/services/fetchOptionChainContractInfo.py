from __future__ import annotations

from typing import Any

import requests

from ..config import (
    NSE_BASE_URL,
    NSE_DEFAULT_HEADERS,
    NSE_OPTION_CHAIN_CONTRACT_INFO_PATH,
    NSE_OPTION_CHAIN_SYMBOL,
)
from ..exceptions import NseFetchException, NseParseException


def fetchOptionChainContractInfo(timeout_seconds: int = 10) -> dict[str, Any]:
    """
    Single responsibility: fetch contract info (expiry dates) for option chain.
    """
    session = requests.Session()

    try:
        session.get(NSE_BASE_URL, headers=NSE_DEFAULT_HEADERS, timeout=timeout_seconds)

        url = f"{NSE_BASE_URL}{NSE_OPTION_CHAIN_CONTRACT_INFO_PATH}"
        params = {"symbol": NSE_OPTION_CHAIN_SYMBOL}
        response = session.get(url, headers=NSE_DEFAULT_HEADERS, params=params, timeout=timeout_seconds)
        if response.status_code != 200:
            raise NseFetchException(f"NSE returned status {response.status_code}")

        try:
            payload = response.json()
        except Exception as e:  # noqa: BLE001
            raise NseParseException("Failed to parse NSE contract-info JSON") from e

        if not isinstance(payload, dict):
            raise NseParseException("Contract-info payload is not an object")

        expiry_dates = payload.get("expiryDates")
        if not isinstance(expiry_dates, list) or not expiry_dates:
            raise NseParseException("Contract-info missing expiryDates")

        return payload
    except (NseFetchException, NseParseException):
        raise
    except Exception as e:  # noqa: BLE001
        raise NseFetchException(str(e)) from e

