"""Async facade for the synchronous BriteCore API client."""

from __future__ import annotations

import asyncio
from typing import Any

from urllib3 import BaseHTTPResponse
from urllib3.util import Retry, Timeout

from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.request_cache import RequestCache, build_cache_key


class AsyncBritecoreAPIClient:
    """Async wrapper around ``BritecoreAPIClient`` with in-memory response caching."""

    def __init__(
        self,
        target_site: str | None = None,
        client: BritecoreAPIClient | None = None,
        cache: RequestCache | None = None,
        default_cache_ttl_seconds: int = 60,
        client_dry_run: bool | None = None,
        base_url: str | None = None,
        api_key: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        """Create an async client facade with optional injected sync client/cache.

        Credentials can be supplied in two ways:

        **File-based (default):** omit all credential kwargs.  The underlying sync
        client reads credentials from the layered config file search hierarchy.

        **Explicit (inline):** pass ``base_url`` (required) plus any combination of
        ``api_key``, ``client_id``, and ``client_secret``.  File-based lookup is
        bypassed when ``base_url`` is provided.

        Args:
            target_site: Target site name / label.
            client: Pre-built :class:`BritecoreAPIClient` to wrap (skips lazy init).
            cache: Optional :class:`~britecore_sdk.api.request_cache.RequestCache`.
            default_cache_ttl_seconds: Default TTL for cached responses.
            client_dry_run: Forward to the underlying sync client's dry-run mode.
            base_url: Explicit base URL; bypasses config-file lookup when provided.
            api_key: Explicit API key (used only when ``base_url`` is also given).
            client_id: Explicit OAuth client ID (used only when ``base_url`` is given).
            client_secret: Explicit OAuth client secret (used only when ``base_url`` is given).
        """
        self.target_site = target_site or getattr(client, "target_site", None)
        self._client = client
        self._cache = cache or RequestCache()
        self._default_cache_ttl_seconds = default_cache_ttl_seconds
        self._client_dry_run = (
            getattr(client, "client_dry_run", False)
            if client_dry_run is None
            else client_dry_run
        )
        # Explicit credential overrides
        self._base_url = base_url
        self._api_key = api_key
        self._client_id = client_id
        self._client_secret = client_secret
        self._client_init_lock = asyncio.Lock()
        self._inflight_lock = asyncio.Lock()
        self._inflight_requests: dict[str, asyncio.Task[Any]] = {}

    async def aget_client(self) -> BritecoreAPIClient:
        """Return the configured sync client, initializing it lazily if necessary."""
        if self._client is not None:
            return self._client

        async with self._client_init_lock:
            if self._client is None:
                # Ensure target_site is str, fallback to empty string if None
                target_site: str = (
                    self.target_site if self.target_site is not None else ""
                )
                client = BritecoreAPIClient(target_site)
                init_kwargs: dict[str, object] = {
                    "client_dry_run": self._client_dry_run
                }
                if self._base_url is not None:
                    init_kwargs["base_url"] = self._base_url
                if self._api_key is not None:
                    init_kwargs["api_key"] = self._api_key
                if self._client_id is not None:
                    init_kwargs["client_id"] = self._client_id
                if self._client_secret is not None:
                    init_kwargs["client_secret"] = self._client_secret
                await asyncio.to_thread(client.init_client, **init_kwargs)  # type: ignore[arg-type]
                self._client = client
            self._client_dry_run = getattr(self._client, "client_dry_run", False)

        return self._client

    def clear_cache(self) -> None:
        """Clear all cached responses."""
        self._cache.clear()

    def invalidate_cache_namespaces(
        self, namespaces: list[str] | tuple[str, ...]
    ) -> int:
        """Invalidate cached responses for the given namespaces."""
        return self._cache.invalidate_namespaces(namespaces)

    async def aprocess_result(
        self, response: BaseHTTPResponse, logs: bool = False
    ) -> Any:
        """Process a sync HTTP response in the same way as ``BritecoreAPIClient``."""
        client = await self.aget_client()
        return client.process_result(response, logs=logs)

    async def _perform_request(
        self,
        *,
        path: str,
        json: dict[str, Any] | None,
        request_timeout: Timeout | None,
        request_retries: Retry | None,
        request_headers: dict[str, Any] | None,
        method: str,
        rate_limiter_bypass: bool,
        dry_run: bool | None,
        dry_run_include_sensitive_headers: bool,
    ) -> BaseHTTPResponse | None:
        """Execute the sync request in a worker thread."""
        client = await self.aget_client()
        return await asyncio.to_thread(
            client.do_request,
            path=path,
            json=json,
            request_timeout=request_timeout,
            request_retries=request_retries,
            request_headers=request_headers,
            method=method,
            rate_limiter_bypass=rate_limiter_bypass,
            dry_run=dry_run,
            dry_run_include_sensitive_headers=dry_run_include_sensitive_headers,
        )

    def _build_request_cache_key(
        self,
        *,
        path: str,
        json: dict[str, Any] | None,
        request_headers: dict[str, Any] | None,
        method: str,
        cache_namespace: str | None,
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

    async def _request_with_optional_dedupe(
        self,
        *,
        path: str,
        json: dict[str, Any] | None,
        request_timeout: Timeout | None,
        request_retries: Retry | None,
        request_headers: dict[str, Any] | None,
        method: str,
        rate_limiter_bypass: bool,
        dry_run: bool | None,
        dry_run_include_sensitive_headers: bool,
        dedupe_in_flight: bool,
        cache_bypass: bool,
        cache_enabled: bool,
        cache_key: str,
    ) -> BaseHTTPResponse | None:
        """Execute request directly or via in-flight dedupe task map."""
        if not (dedupe_in_flight and not cache_bypass and cache_key):
            return await self._perform_request(
                path=path,
                json=json,
                request_timeout=request_timeout,
                request_retries=request_retries,
                request_headers=request_headers,
                method=method,
                rate_limiter_bypass=rate_limiter_bypass,
                dry_run=dry_run,
                dry_run_include_sensitive_headers=dry_run_include_sensitive_headers,
            )

        created_task = False
        inflight_task: asyncio.Task[Any] | None = None

        async with self._inflight_lock:
            if cache_enabled:
                cached_response = self._cache.get(cache_key)
                if cached_response is not None:
                    return cached_response

            inflight_task = self._inflight_requests.get(cache_key)
            if inflight_task is None:
                new_task = asyncio.create_task(
                    self._perform_request(
                        path=path,
                        json=json,
                        request_timeout=request_timeout,
                        request_retries=request_retries,
                        request_headers=request_headers,
                        method=method,
                        rate_limiter_bypass=rate_limiter_bypass,
                        dry_run=dry_run,
                        dry_run_include_sensitive_headers=dry_run_include_sensitive_headers,
                    )
                )
                self._inflight_requests[cache_key] = new_task
                inflight_task = new_task
                created_task = True

        try:
            return await inflight_task
        finally:
            if created_task:
                async with self._inflight_lock:
                    if self._inflight_requests.get(cache_key) is inflight_task:
                        del self._inflight_requests[cache_key]

    def _cache_response_on_success(
        self,
        *,
        response: BaseHTTPResponse | None,
        cache_enabled: bool,
        cache_bypass: bool,
        cache_key: str,
        cache_ttl_seconds: int | None,
        cache_namespace: str | None,
        cache_invalidate_on_success: list[str] | tuple[str, ...] | None,
    ) -> None:
        """Apply invalidation and optional write-through cache on success responses."""
        if not self._is_success_response(response):
            return

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

    async def ado_request(
        self,
        path: str,
        json: dict[str, Any] | None = None,
        request_timeout: Timeout | None = None,
        request_retries: Retry | None = None,
        request_headers: dict[str, Any] | None = None,
        method: str | None = "POST",
        cache_enabled: bool = False,
        cache_ttl_seconds: int | None = None,
        cache_namespace: str | None = None,
        cache_key_parts: list[str] | tuple[str, ...] | None = None,
        cache_bypass: bool = False,
        cache_invalidate_on_success: list[str] | tuple[str, ...] | None = None,
        dedupe_in_flight: bool = True,
        rate_limiter_bypass: bool = False,
        dry_run: bool | None = None,
        dry_run_include_sensitive_headers: bool = False,
    ) -> BaseHTTPResponse | None:
        """Execute a request asynchronously with optional response caching."""
        client = await self.aget_client()
        normalized_method = (method or "POST").upper()
        effective_dry_run = client.client_dry_run if dry_run is None else dry_run
        should_build_key = (cache_enabled or dedupe_in_flight) and not effective_dry_run
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
        response = await self._request_with_optional_dedupe(
            path=path,
            json=json,
            request_timeout=request_timeout,
            request_retries=request_retries,
            request_headers=request_headers,
            method=normalized_method,
            rate_limiter_bypass=rate_limiter_bypass,
            dry_run=effective_dry_run,
            dry_run_include_sensitive_headers=dry_run_include_sensitive_headers,
            dedupe_in_flight=dedupe_in_flight and not effective_dry_run,
            cache_bypass=cache_bypass or effective_dry_run,
            cache_enabled=cache_enabled and not effective_dry_run,
            cache_key=cache_key,
        )

        self._cache_response_on_success(
            response=response,
            cache_enabled=cache_enabled and not effective_dry_run,
            cache_bypass=cache_bypass or effective_dry_run,
            cache_key=cache_key,
            cache_ttl_seconds=cache_ttl_seconds,
            cache_namespace=cache_namespace,
            cache_invalidate_on_success=cache_invalidate_on_success,
        )

        return response

    # ------------------------------------------------------------------
    # Workflow: batch helpers
    # ------------------------------------------------------------------

    async def acreate_full_quotes_batch(
        self,
        quotes_json: list[Any],
        max_concurrent: int = 5,
        fail_fast: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create many quotes concurrently and return per-item outcomes.

        Delegates to
        :func:`britecore_sdk.api.workflows.async_batch_quotes.acreate_full_quotes_batch`.
        See that function for full documentation.

        Args:
            quotes_json: List of quote payload dictionaries.
            max_concurrent: Maximum concurrent coroutines. Defaults to ``5``.
            fail_fast: When ``True``, raises the first encountered exception and
                cancels remaining tasks. Defaults to ``False``.
            **kwargs: ``RequestParameters`` passed through to each quote create
                call.

        Returns:
            dict with ``total``, ``succeeded``, ``failed``, and ``results`` keys.
        """
        from britecore_sdk.api.workflows.async_batch_quotes import (
            acreate_full_quotes_batch as _acreate_full_quotes_batch,
        )

        return await _acreate_full_quotes_batch(
            quotes_json,
            max_concurrent=max_concurrent,
            fail_fast=fail_fast,
            **kwargs,
        )

    async def acreate_contacts_batch(
        self,
        contacts_json: list[Any],
        max_concurrent: int = 5,
        fail_fast: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create many contacts concurrently and return per-item outcomes.

        Delegates to
        :func:`britecore_sdk.api.workflows.async_batch_contacts.acreate_contacts_batch`.
        See that function for full documentation.

        Args:
            contacts_json: List of contact payload dicts (each must contain
                ``name`` and ``address``).
            max_concurrent: Maximum concurrent coroutines. Defaults to ``5``.
            fail_fast: When ``True``, raises the first encountered exception and
                cancels remaining tasks. Defaults to ``False``.
            **kwargs: ``RequestParameters`` passed through to each contact create
                call.

        Returns:
            dict with ``total``, ``succeeded``, ``failed``, and ``results`` keys.
        """
        from britecore_sdk.api.workflows.async_batch_contacts import (
            acreate_contacts_batch as _acreate_contacts_batch,
        )

        return await _acreate_contacts_batch(
            contacts_json,
            max_concurrent=max_concurrent,
            fail_fast=fail_fast,
            **kwargs,
        )

    async def acreate_policies_batch(
        self,
        policies_json: list[Any],
        max_concurrent: int = 3,
        fail_fast: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create many policies concurrently and return per-item outcomes.

        Delegates to
        :func:`britecore_sdk.api.workflows.async_batch_policies.acreate_policies_batch`.
        See that function for full documentation.

        Args:
            policies_json: List of policy payload dicts forwarded as kwargs to
                ``acreate_policy``.
            max_concurrent: Maximum concurrent coroutines. Defaults to ``3``.
            fail_fast: When ``True``, raises the first encountered exception and
                cancels remaining tasks. Defaults to ``False``.
            **kwargs: ``RequestParameters`` passed through to each policy create
                call.

        Returns:
            dict with ``total``, ``succeeded``, ``failed``, and ``results`` keys.
        """
        from britecore_sdk.api.workflows.async_batch_policies import (
            acreate_policies_batch as _acreate_policies_batch,
        )

        return await _acreate_policies_batch(
            policies_json,
            max_concurrent=max_concurrent,
            fail_fast=fail_fast,
            **kwargs,
        )

    async def acreate_risks_batch(
        self,
        risks_json: list[Any],
        max_concurrent: int = 3,
        fail_fast: bool = False,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Create many risks concurrently and return per-item outcomes.

        Delegates to
        :func:`britecore_sdk.api.workflows.async_batch_policies.acreate_risks_batch`.
        See that function for full documentation.

        Args:
            risks_json: List of risk payload dicts (each must contain
                ``revision_id``).
            max_concurrent: Maximum concurrent coroutines. Defaults to ``3``.
            fail_fast: When ``True``, raises the first encountered exception and
                cancels remaining tasks. Defaults to ``False``.
            **kwargs: ``RequestParameters`` passed through to each risk create
                call.

        Returns:
            dict with ``total``, ``succeeded``, ``failed``, and ``results`` keys.
        """
        from britecore_sdk.api.workflows.async_batch_policies import (
            acreate_risks_batch as _acreate_risks_batch,
        )

        return await _acreate_risks_batch(
            risks_json,
            max_concurrent=max_concurrent,
            fail_fast=fail_fast,
            **kwargs,
        )
