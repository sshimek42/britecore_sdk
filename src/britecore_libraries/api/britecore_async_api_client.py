"""Async facade for the synchronous BriteCore API client."""

from __future__ import annotations

import asyncio
from typing import Any, Optional

from urllib3 import BaseHTTPResponse
from urllib3.util import Retry, Timeout

from britecore_libraries.api.britecore_api_client import BritecoreAPIClient
from britecore_libraries.api.request_cache import RequestCache, build_cache_key


class AsyncBritecoreAPIClient:
    """Async wrapper around ``BritecoreAPIClient`` with in-memory response caching."""

    def __init__(
        self,
        target_site: Optional[str] = None,
        client: Optional[BritecoreAPIClient] = None,
        cache: Optional[RequestCache] = None,
        default_cache_ttl_seconds: int = 60,
    ) -> None:
        self.target_site = target_site or getattr(client, "target_site", None)
        self._client = client
        self._cache = cache or RequestCache()
        self._default_cache_ttl_seconds = default_cache_ttl_seconds
        self._client_init_lock = asyncio.Lock()
        self._inflight_lock = asyncio.Lock()
        self._inflight_requests: dict[str, asyncio.Task[Any]] = {}

    async def aget_client(self) -> BritecoreAPIClient:
        """Return the configured sync client, initializing it lazily if necessary."""
        if self._client is not None:
            return self._client

        async with self._client_init_lock:
            if self._client is None:
                client = BritecoreAPIClient(self.target_site)
                await asyncio.to_thread(client.init_client)
                self._client = client

        return self._client

    def clear_cache(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()

    def invalidate_cache_namespaces(self, namespaces: list[str] | tuple[str, ...]) -> int:
        """Invalidate cached responses for the given namespaces."""
        return self._cache.invalidate_namespaces(namespaces)

    async def aprocess_result(self, response: BaseHTTPResponse, logs: bool = False) -> Any:
        """Process a sync HTTP response in the same way as ``BritecoreAPIClient``."""
        client = await self.aget_client()
        return client.process_result(response, logs=logs)

    async def _perform_request(
        self,
        *,
        path: str,
        json: Optional[dict[str, Any]],
        request_timeout: Optional[Timeout],
        request_retries: Optional[Retry],
        request_headers: Optional[dict[str, Any]],
        method: str,
    ) -> BaseHTTPResponse | None:
        """Execute the sync request in a worker thread."""
        client = await self.aget_client()
        return await asyncio.to_thread(
            client.do_request,
            path,
            json,
            request_timeout,
            request_retries,
            request_headers,
            method,
        )

    def _build_request_cache_key(
        self,
        *,
        path: str,
        json: Optional[dict[str, Any]],
        request_headers: Optional[dict[str, Any]],
        method: str,
        cache_namespace: Optional[str],
        cache_key_parts: list[str] | tuple[str, ...] | None,
    ) -> str:
        """Build a stable cache key for the request."""
        target_site = self.target_site or getattr(self._client, "target_site", None)
        return build_cache_key(
            target_site=target_site,
            method=method,
            path=path,
            json_payload=json,
            request_headers=request_headers,
            cache_namespace=cache_namespace,
            cache_key_parts=cache_key_parts,
        )

    @staticmethod
    def _is_success_response(
        response: BaseHTTPResponse | None,
    ) -> bool:
        """Return True when the HTTP response is cacheable as a success."""
        return response is not None and getattr(response, "status", None) == 200

    async def ado_request(
        self,
        path: str,
        json: Optional[dict[str, Any]] = None,
        request_timeout: Optional[Timeout] = None,
        request_retries: Optional[Retry] = None,
        request_headers: Optional[dict[str, Any]] = None,
        method: Optional[str] = "POST",
        cache_enabled: bool = False,
        cache_ttl_seconds: Optional[int] = None,
        cache_namespace: Optional[str] = None,
        cache_key_parts: list[str] | tuple[str, ...] | None = None,
        cache_bypass: bool = False,
        cache_invalidate_on_success: list[str] | tuple[str, ...] | None = None,
        dedupe_in_flight: bool = True,
    ) -> BaseHTTPResponse | None:
        """Execute a request asynchronously with optional response caching."""
        normalized_method = (method or "POST").upper()
        should_build_key = cache_enabled or dedupe_in_flight
        cache_key = ""

        if should_build_key:
            cache_key = self._build_request_cache_key(
                path=path,
                json=json,
                request_headers=request_headers,
                method=normalized_method,
                cache_namespace=cache_namespace,
                cache_key_parts=cache_key_parts,
            )

        if cache_enabled and not cache_bypass and cache_key:
            cached_response = self._cache.get(cache_key)
            if cached_response is not None:
                return cached_response

        response: BaseHTTPResponse | None
        created_task = False
        inflight_task: asyncio.Task[Any] | None = None

        if dedupe_in_flight and not cache_bypass and cache_key:
            async with self._inflight_lock:
                if cache_enabled:
                    cached_response = self._cache.get(cache_key)
                    if cached_response is not None:
                        return cached_response

                inflight_task = self._inflight_requests.get(cache_key)
                if inflight_task is None:
                    inflight_task = asyncio.create_task(
                        self._perform_request(
                            path=path,
                            json=json,
                            request_timeout=request_timeout,
                            request_retries=request_retries,
                            request_headers=request_headers,
                            method=normalized_method,
                        )
                    )
                    self._inflight_requests[cache_key] = inflight_task
                    created_task = True

            try:
                response = await inflight_task
            finally:
                if created_task:
                    async with self._inflight_lock:
                        if self._inflight_requests.get(cache_key) is inflight_task:
                            del self._inflight_requests[cache_key]
        else:
            response = await self._perform_request(
                path=path,
                json=json,
                request_timeout=request_timeout,
                request_retries=request_retries,
                request_headers=request_headers,
                method=normalized_method,
            )

        if self._is_success_response(response):
            if cache_invalidate_on_success:
                self._cache.invalidate_namespaces(cache_invalidate_on_success)

            if cache_enabled and not cache_bypass and cache_key:
                ttl_seconds = cache_ttl_seconds or self._default_cache_ttl_seconds
                self._cache.set(
                    cache_key,
                    response,
                    ttl_seconds=ttl_seconds,
                    namespace=cache_namespace or "",
                )

        return response
