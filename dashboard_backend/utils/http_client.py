import logging
import time
from typing import Any, Callable, Awaitable, Optional, Union

import httpx

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT_SECONDS = 30.0
DEFAULT_RETRY_COUNT = 2


class UpstreamServiceError(Exception):
    """Raised when a remote HTTP service returns an error."""


class RequestExecutor:
    """
    Responsible for executing HTTP requests
    with retry, logging, and validation.
    """

    def __init__(self, retry_count: int = DEFAULT_RETRY_COUNT):
        self._retry_count = retry_count

    async def execute_async(
        self,
        operation: Callable[[], Awaitable[httpx.Response]],
        method: str,
        url: str,
        raw: bool = False,
    ) -> Union[dict[str, Any], bytes]:
        for attempt in range(self._retry_count + 1):
            start_time = time.perf_counter()
            try:
                response = await operation()
                if raw:
                    return self._validate_response_raw(response, method, url, start_time)
                return self._validate_response(response, method, url, start_time)
            except httpx.HTTPError as exc:
                if attempt >= self._retry_count:
                    raise UpstreamServiceError(str(exc)) from exc

    def execute(
        self,
        operation: Callable[[], httpx.Response],
        method: str,
        url: str,
        raw: bool = False,
    ) -> Union[dict[str, Any], bytes]:
        for attempt in range(self._retry_count + 1):
            start_time = time.perf_counter()
            try:
                response = operation()
                if raw:
                    return self._validate_response_raw(response, method, url, start_time)
                return self._validate_response(response, method, url, start_time)
            except httpx.HTTPError as exc:
                if attempt >= self._retry_count:
                    raise UpstreamServiceError(str(exc)) from exc

    def _validate_response(
        self,
        response: httpx.Response,
        method: str,
        url: str,
        start_time: float,
    ) -> dict[str, Any]:
        duration = time.perf_counter() - start_time

        logger.info(
            "HTTP %s %s -> %s (%.2fs)",
            method,
            url,
            response.status_code,
            duration,
        )

        response.raise_for_status()
        return response.json()

    def _validate_response_raw(
        self,
        response: httpx.Response,
        method: str,
        url: str,
        start_time: float,
    ) -> bytes:
        duration = time.perf_counter() - start_time

        logger.info(
            "HTTP %s %s -> %s (%.2fs)",
            method,
            url,
            response.status_code,
            duration,
        )

        response.raise_for_status()
        return response.content


class AsyncHttpClient:
    """
    Async HTTP client for ASGI applications.
    """

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        headers: Optional[dict[str, str]] = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._headers = headers or {}
        self._client: Optional[httpx.AsyncClient] = None
        self._executor = RequestExecutor()

    async def __aenter__(self) -> "AsyncHttpClient":
        self._client = httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout_seconds,
            headers=self._headers,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()

    def _get_client(self) -> httpx.AsyncClient:
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'async with'.")
        return self._client

    async def send(
        self,
        method: str,
        endpoint: str,
        raw: bool = False,
        **request_options: Any,
    ) -> Union[dict[str, Any], bytes]:
        client = self._get_client()
        endpoint = self._build_endpoint(endpoint)
        url = f"{self._base_url}{endpoint}"

        return await self._executor.execute_async(
            lambda: client.request(method, endpoint, **request_options),
            method,
            url,
            raw=raw,
        )

    async def post(
        self,
        endpoint: str,
        payload: Any,
        **request_options: Any,
    ) -> dict[str, Any]:
        return await self.send(
            "POST",
            endpoint,
            json=payload,
            **request_options,
        )

    async def post_raw(
        self,
        endpoint: str,
        payload: Any,
        **request_options: Any,
    ) -> bytes:
        return await self.send(
            "POST",
            endpoint,
            json=payload,
            raw=True,
            **request_options,
        )

    def _build_endpoint(self, endpoint: str) -> str:
        return endpoint if endpoint.startswith("/") else f"/{endpoint}"


class HttpClient:
    """
    Sync HTTP client for worker processes or sync frameworks.
    """

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        headers: Optional[dict[str, str]] = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._headers = headers or {}
        self._client: Optional[httpx.Client] = None
        self._executor = RequestExecutor()

    def __enter__(self) -> "HttpClient":
        self._client = httpx.Client(
            base_url=self._base_url,
            timeout=self._timeout_seconds,
            headers=self._headers,
        )
        return self

    def __exit__(self, *args: Any) -> None:
        if self._client:
            self._client.close()

    def _get_client(self) -> httpx.Client:
        if not self._client:
            raise RuntimeError("Client not initialized. Use 'with'.")
        return self._client

    def send(
        self,
        method: str,
        endpoint: str,
        raw: bool = False,
        **request_options: Any,
    ) -> Union[dict[str, Any], bytes]:
        client = self._get_client()
        endpoint = self._build_endpoint(endpoint)
        url = f"{self._base_url}{endpoint}"

        return self._executor.execute(
            lambda: client.request(method, endpoint, **request_options),
            method,
            url,
            raw=raw,
        )

    def post(
        self,
        endpoint: str,
        payload: Any,
        **request_options: Any,
    ) -> dict[str, Any]:
        return self.send(
            "POST",
            endpoint,
            json=payload,
            **request_options,
        )

    def post_raw(
        self,
        endpoint: str,
        payload: Any,
        **request_options: Any,
    ) -> bytes:
        return self.send(
            "POST",
            endpoint,
            json=payload,
            raw=True,
            **request_options,
        )

    def _build_endpoint(self, endpoint: str) -> str:
        return endpoint if endpoint.startswith("/") else f"/{endpoint}"