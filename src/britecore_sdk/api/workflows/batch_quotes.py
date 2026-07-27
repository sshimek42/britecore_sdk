"""Sync batch workflow helpers for quote creation.

This module houses higher-level orchestration for bulk quote creation.
Endpoint wrappers for individual quote calls live in
``britecore_sdk.api.api_calls.v2.quotes``.
"""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any, NotRequired, Unpack

from britecore_sdk import BritecoreError
from britecore_sdk.api.api_calls import BritecoreAPIClient, RequestParameters
from britecore_sdk.api.api_calls.v2.quotes import create_full_quote
from britecore_sdk.models import BatchItemResult


class BatchQuoteCreateResult(BatchItemResult, total=False):
    """Per-item quote batch result with optional legacy aliases."""

    quote_id: NotRequired[str | None]
    quote_data: NotRequired[dict[str, Any] | None]


def _with_legacy_quote_keys(
    item: BatchItemResult,
    *,
    include_legacy_keys: bool,
) -> BatchQuoteCreateResult:
    """Attach legacy quote keys for compatibility during migration."""
    result: BatchQuoteCreateResult = {
        "index": item["index"],
        "success": item["success"],
        "id": item["id"],
        "data": item["data"],
        "error": item["error"],
        "error_type": item["error_type"],
    }
    if include_legacy_keys:
        result["quote_id"] = item["id"]
        result["quote_data"] = item["data"]
    return result


def create_full_quotes_batch(
    quotes_json: list[dict[str, Any]],
    max_workers: int = 5,
    fail_fast: bool = False,
    include_legacy_keys: bool = True,
    client: BritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many quotes concurrently and return per-item outcomes.

    This helper runs ``create_full_quote(...)`` in a bounded thread pool so
    high-volume quote creation jobs can complete much faster than fully
    serial execution. It returns a stable, index-aligned result list with
    success/error metadata for each submitted payload.

    Args:
        quotes_json: List of quote payload dictionaries.
        max_workers: Maximum concurrent workers. Defaults to ``5``.
        fail_fast: When ``True``, re-raises the first encountered exception and
            cancels pending futures. Defaults to ``False``.
        include_legacy_keys: When ``True`` (default), include legacy
            ``quote_id``/``quote_data`` aliases alongside ``id``/``data``.
        client: Optional explicit API client to use for all create calls.
        **kwargs: ``RequestParameters`` passed through to each quote create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted quote payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list[BatchQuoteCreateResult] ordered by input index

    Raises:
        BritecoreError.MissingParameter: If ``quotes_json`` is missing/empty.
        ValueError: If ``max_workers`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not quotes_json or not isinstance(quotes_json, list):
        raise BritecoreError.MissingParameter(
            "quotes_json is required and must be a non-empty list"
        )
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")

    worker_count = min(max_workers, len(quotes_json))
    results: list[BatchItemResult | None] = [None] * len(quotes_json)

    def _create_one(
        index: int, payload: dict[str, Any]
    ) -> tuple[int, dict[str, Any] | None, str | None]:
        quote_data, quote_id = create_full_quote(payload, client=client, **kwargs)
        return index, quote_data, quote_id

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map: dict[Future[tuple[int, dict[str, Any] | None, str | None]], int] = {
            executor.submit(_create_one, idx, payload): idx
            for idx, payload in enumerate(quotes_json)
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                result_idx, quote_data, quote_id = future.result()
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "id": quote_id,
                    "data": quote_data,
                    "error": None,
                    "error_type": None,
                }
            except Exception as exc:
                if fail_fast:
                    for pending in future_map:
                        pending.cancel()
                    raise
                results[idx] = {
                    "index": idx,
                    "success": False,
                    "id": None,
                    "data": None,
                    "error": str(exc),
                    "error_type": type(exc).__name__,
                }

    finalized_items = [item for item in results if item is not None]
    finalized_results = [
        _with_legacy_quote_keys(item, include_legacy_keys=include_legacy_keys)
        for item in finalized_items
    ]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(quotes_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


__all__ = ["BatchQuoteCreateResult", "create_full_quotes_batch"]
