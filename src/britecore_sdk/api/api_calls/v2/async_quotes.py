"""BriteCore v2 Async Quotes API endpoint wrappers.

Asynchronous (cached) counterparts to the synchronous wrappers in quotes.py.
Uses AsyncBritecoreAPIClient for non-blocking, TTL-cached HTTP requests.

Provides:
    acreate_full_quote           -- Async create a full quote from a JSON payload.
    acreate_full_quotes_batch    -- Async batch create many quotes concurrently.
    aget_quote                   -- Async retrieve a quote by ID (cached by default).
"""

import asyncio
from logging import Logger
from typing import Any, TypedDict, Unpack

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import (
    AsyncBritecoreAPIClient,
    RequestParameters,
    async_api_client,
)


class BatchQuoteCreateResult(TypedDict):
    """Per-item outcome for ``acreate_full_quotes_batch``."""

    index: int
    success: bool
    quote_data: dict[str, Any] | None
    quote_id: str | None
    error: str | None


LOGGER: Logger = logger

API_CLIENT: AsyncBritecoreAPIClient = async_api_client
QUOTE_CACHE_NAMESPACE = "quotes"
DEFAULT_CACHE_TTL_SECONDS = 60


def _apply_quote_read_cache(
    kwargs: dict[str, Any], *, cache_key_parts: list[str] | None = None
) -> dict[str, Any]:
    """Apply default caching for quote read requests while allowing overrides."""
    kwargs.setdefault("cache_enabled", True)
    kwargs.setdefault("cache_namespace", QUOTE_CACHE_NAMESPACE)
    kwargs.setdefault("cache_ttl_seconds", DEFAULT_CACHE_TTL_SECONDS)
    if cache_key_parts:
        kwargs.setdefault("cache_key_parts", cache_key_parts)
    return kwargs


def _apply_quote_mutation_cache(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Invalidate cached quote reads after a successful quote mutation."""
    kwargs.setdefault("cache_invalidate_on_success", [QUOTE_CACHE_NAMESPACE])
    return kwargs


async def acreate_full_quote(
    quote_json: dict[str, Any], **kwargs: Unpack[RequestParameters]
) -> tuple[dict[str, Any] | None, str | None]:
    """Create a full quote asynchronously.

    Use ``quote_json`` for the complete quote payload expected by the quote-create
    workflow exposed by this SDK. Returns the async ``aprocess_result(...)``
    payload together with the extracted quote ID, invalidates cached quote reads
    on success, and accepts ``RequestParameters`` overrides via ``**kwargs``.
    """
    request_kwargs = _apply_quote_mutation_cache(dict(kwargs))
    request_result: Any = await API_CLIENT.ado_request(
        path="/api/v2/quotes/create_full_quote",
        json=quote_json,
        **request_kwargs,
    )
    json_info: Any = await API_CLIENT.aprocess_result(request_result)

    if not json_info:
        return None, None

    return json_info, json_info.get("id")


async def aget_quote(id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a quote by ID with short-lived async caching enabled by default.

    The request uses ``id`` to fetch the quote through the async quote client and
    enables the default quote read cache unless the caller overrides it. Returns
    the async ``aprocess_result(...)`` payload, and ``**kwargs`` accepts
    ``RequestParameters`` plus cache override settings.
    """
    quote_json: dict[str, str] = {"id": id}
    LOGGER.debug("Getting quote")
    request_kwargs = _apply_quote_read_cache(
        dict(kwargs), cache_key_parts=[f"quote:{id}"]
    )
    request_result: Any = await API_CLIENT.ado_request(
        path="/api/v2/quotes/get_quote",
        json=quote_json,
        **request_kwargs,
    )
    return await API_CLIENT.aprocess_result(request_result)


async def acreate_full_quotes_batch(
    quotes_json: list[dict[str, Any]],
    max_concurrent: int = 5,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many quotes concurrently and return per-item outcomes.

    This helper runs ``acreate_full_quote(...)`` with bounded concurrency so
    high-volume quote creation jobs can complete much faster than fully
    serial execution. It returns a stable, index-aligned result list with
    success/error metadata for each submitted payload.

    Args:
        quotes_json: List of quote payload dictionaries.
        max_concurrent: Maximum concurrent coroutines. Defaults to ``5``.
        fail_fast: When ``True``, raises the first encountered exception and
            cancels remaining tasks. Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each quote create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted quote payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list[BatchQuoteCreateResult] ordered by input index

    Raises:
        BritecoreError.MissingParameter: If ``quotes_json`` is missing/empty.
        ValueError: If ``max_concurrent`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not quotes_json or not isinstance(quotes_json, list):
        raise BritecoreError.MissingParameter(
            "quotes_json is required and must be a non-empty list"
        )
    if max_concurrent < 1:
        raise ValueError("max_concurrent must be at least 1")

    results: list[BatchQuoteCreateResult | None] = [None] * len(quotes_json)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _create_one_semaphored(
        index: int, payload: dict[str, Any]
    ) -> tuple[int, dict[str, Any] | None, str | None]:
        """Create a quote with semaphore-controlled concurrency."""
        async with semaphore:
            quote_data, quote_id = await acreate_full_quote(payload, **kwargs)
            return index, quote_data, quote_id

    tasks = [
        asyncio.create_task(_create_one_semaphored(idx, payload))
        for idx, payload in enumerate(quotes_json)
    ]

    if fail_fast:
        try:
            task_results = await asyncio.gather(*tasks)
            for result_idx, quote_data, quote_id in task_results:
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "quote_data": quote_data,
                    "quote_id": quote_id,
                    "error": None,
                }
        except Exception:
            for task in tasks:
                task.cancel()
            raise
    else:
        task_results = await asyncio.gather(*tasks, return_exceptions=True)  # type: ignore[assignment]
        for idx, result in enumerate(task_results):
            if isinstance(result, Exception):
                results[idx] = {
                    "index": idx,
                    "success": False,
                    "quote_data": None,
                    "quote_id": None,
                    "error": str(result),
                }
            else:
                result_idx, quote_data, quote_id = result
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "quote_data": quote_data,
                    "quote_id": quote_id,
                    "error": None,
                }

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(quotes_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


__all__ = ["acreate_full_quote", "acreate_full_quotes_batch", "aget_quote"]
