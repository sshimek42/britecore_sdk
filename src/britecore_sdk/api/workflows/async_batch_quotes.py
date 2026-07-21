"""Async batch workflow helpers for quote creation.

This module houses higher-level async orchestration for bulk quote creation.
Endpoint wrappers for individual quote calls live in
``britecore_sdk.api.api_calls.v2.async_quotes``.
"""

import asyncio
from typing import Any

from britecore_sdk import BritecoreError
from britecore_sdk.api.api_calls.v2.async_quotes import acreate_full_quote
from britecore_sdk.api.workflows.batch_quotes import BatchQuoteCreateResult

QuoteTaskResult = tuple[int, dict[str, Any] | None, str | None]


async def acreate_full_quotes_batch(
    quotes_json: list[dict[str, Any]],
    max_concurrent: int = 5,
    fail_fast: bool = False,
    **kwargs: Any,
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
    ) -> QuoteTaskResult:
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
            task_results: list[QuoteTaskResult] = await asyncio.gather(*tasks)
            for result_idx, quote_data, quote_id in task_results:
                success_result: BatchQuoteCreateResult = {
                    "index": result_idx,
                    "success": True,
                    "quote_data": quote_data,
                    "quote_id": quote_id,
                    "error": None,
                }
                results[result_idx] = success_result
        except Exception:
            for task in tasks:
                task.cancel()
            raise
    else:
        gathered: list[QuoteTaskResult | BaseException] = await asyncio.gather(
            *tasks, return_exceptions=True
        )
        for idx, result in enumerate(gathered):
            if isinstance(result, Exception):
                failed_result: BatchQuoteCreateResult = {
                    "index": idx,
                    "success": False,
                    "quote_data": None,
                    "quote_id": None,
                    "error": str(result),
                }
                results[idx] = failed_result
            elif not isinstance(result, BaseException):
                result_idx, quote_data, quote_id = result
                ok_result: BatchQuoteCreateResult = {
                    "index": result_idx,
                    "success": True,
                    "quote_data": quote_data,
                    "quote_id": quote_id,
                    "error": None,
                }
                results[result_idx] = ok_result

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(quotes_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


__all__ = ["BatchQuoteCreateResult", "acreate_full_quotes_batch"]
