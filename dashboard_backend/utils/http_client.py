import logging
import time
from typing import Any, Optional, Union

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_RETRY_COUNT = 2


class UpstreamServiceError(Exception):
    """Raised when a remote HTTP service returns an error."""


class HttpClient:
    """
    Minimal async HTTP client.

    - Constructor stores reusable fields: `base_url`, `timeout_seconds`, `headers`, `retry_count`.
    - All request logic (retry, timing/logging, JSON/raw parsing) lives in `_request()`.
    - Public API exposes only `get()` and `post()`.
    """

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        headers: Optional[dict[str, str]] = None,
        retry_count: int = DEFAULT_RETRY_COUNT,
    ):
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._headers = headers or {}
        self._retry_count = retry_count
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "HttpClient":
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout_seconds,
            headers=self._headers,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client is not None:
            await self._client.aclose()

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            raise RuntimeError("Client not initialized. Use 'async with'.")
        return self._client

    def _build_endpoint(self, endpoint: str) -> str:
        return endpoint if endpoint.startswith("/") else f"/{endpoint}"

    def _build_url_for_log(self, endpoint: str) -> str:
        # Used only for logging and error messages.
        return f"{self._base_url}{self._build_endpoint(endpoint)}"

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        raw: bool = False,
        **request_options: Any,
    ) -> Union[dict[str, Any], bytes]:
        client = self._get_client()
        endpoint_path = self._build_endpoint(endpoint)
        url_for_log = self._build_url_for_log(endpoint)

        for attempt in range(self._retry_count + 1):
            start_time = time.perf_counter()
            try:
                response = await client.request(method, endpoint_path, **request_options)
                duration = time.perf_counter() - start_time

                logger.info(
                    "HTTP %s %s -> %s (%.2fs)",
                    method,
                    url_for_log,
                    response.status_code,
                    duration,
                )

                response.raise_for_status()
                return response.content if raw else response.json()
            except httpx.HTTPError as exc:
                if attempt >= self._retry_count:
                    raise UpstreamServiceError(
                        f"{method} {url_for_log} failed after {attempt + 1} attempts: {exc}"
                    ) from exc

                logger.warning(
                    "HTTP %s %s failed attempt %s/%s: %s",
                    method,
                    url_for_log,
                    attempt + 1,
                    self._retry_count + 1,
                    exc,
                )

        raise UpstreamServiceError(f"{method} {url_for_log} failed after retries")

    async def get(
        self,
        endpoint: str,
        *,
        raw: bool = False,
        **request_options: Any,
    ) -> Union[dict[str, Any], bytes]:
        return await self._request("GET", endpoint, raw=raw, **request_options)

    async def post(
        self,
        endpoint: str,
        payload: Any = None,
        *,
        raw: bool = False,
        **request_options: Any,
    ) -> Union[dict[str, Any], bytes]:
        options = dict(request_options)
        if payload is not None:
            options["json"] = payload
        return await self._request("POST", endpoint, raw=raw, **options)
