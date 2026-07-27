"""Async batch workflow helpers for contact creation.

This module houses higher-level async orchestration for bulk contact creation.
Endpoint wrappers for individual contact calls live in
``britecore_sdk.api.api_calls.v2.async_contacts``.
"""

import asyncio
from typing import Any, Unpack

from britecore_sdk import BritecoreError
from britecore_sdk.api.api_calls import AsyncBritecoreAPIClient, RequestParameters
from britecore_sdk.api.api_calls.v2.async_contacts import anew_contact
from britecore_sdk.api.workflows.batch_contacts import BatchContactCreateResult
from britecore_sdk.models import BatchItemResult


def _with_legacy_contact_keys(
    item: BatchItemResult,
    *,
    include_legacy_keys: bool,
) -> BatchContactCreateResult:
    """Attach legacy contact keys for compatibility during migration."""
    result: BatchContactCreateResult = {
        "index": item["index"],
        "success": item["success"],
        "id": item["id"],
        "data": item["data"],
        "error": item["error"],
        "error_type": item["error_type"],
    }
    if include_legacy_keys:
        result["contact_id"] = item["id"]
        result["contact_data"] = item["data"]
    return result


ContactTaskResult = tuple[int, Any, str | None]


async def acreate_contacts_batch(
    contacts_json: list[dict[str, Any]],
    max_concurrent: int = 5,
    fail_fast: bool = False,
    include_legacy_keys: bool = True,
    client: AsyncBritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many contacts concurrently and return per-item outcomes.

    This helper runs ``anew_contact(...)`` with bounded concurrency so
    high-volume contact creation jobs complete much faster than fully
    serial execution.  Each payload dict must include ``name`` and
    ``address`` keys (matching ``anew_contact`` parameters).

    Args:
        contacts_json: List of contact payload dicts.  Each dict must contain
            at minimum ``name`` (str) and ``address`` (list[dict]).  Optional
            keys ``phone``, ``email``, and ``contact_type`` are forwarded if
            present.
        max_concurrent: Maximum concurrent coroutines.  Defaults to ``5``.
        fail_fast: When ``True``, raises the first encountered exception and
            cancels remaining tasks.  Defaults to ``False``.
        include_legacy_keys: When ``True`` (default), include legacy
            ``contact_id``/``contact_data`` aliases alongside ``id``/``data``.
        client: Optional explicit async API client to use for all create calls.
        **kwargs: ``RequestParameters`` passed through to each contact create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list[BatchContactCreateResult] ordered by input index

    Raises:
        BritecoreError.MissingParameter: If ``contacts_json`` is missing/empty.
        ValueError: If ``max_concurrent`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not contacts_json or not isinstance(contacts_json, list):
        raise BritecoreError.MissingParameter(
            "contacts_json is required and must be a non-empty list"
        )
    if max_concurrent < 1:
        raise ValueError("max_concurrent must be at least 1")

    results: list[BatchItemResult | None] = [None] * len(contacts_json)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _create_one_semaphored(
        index: int, payload: dict[str, Any]
    ) -> ContactTaskResult:
        async with semaphore:
            contact_data, contact_id = await anew_contact(
                name=payload["name"],
                address=payload["address"],
                phone=payload.get("phone"),
                email=payload.get("email"),
                contact_type=payload.get("contact_type", "individual"),
                client=client,
                **kwargs,
            )
            return index, contact_data, contact_id

    tasks = [
        asyncio.create_task(_create_one_semaphored(idx, payload))
        for idx, payload in enumerate(contacts_json)
    ]

    if fail_fast:
        try:
            task_results: list[ContactTaskResult] = await asyncio.gather(*tasks)
            for result_idx, contact_data, contact_id in task_results:
                success_result: BatchContactCreateResult = {
                    "index": result_idx,
                    "success": True,
                    "id": contact_id,
                    "data": contact_data,
                    "error": None,
                    "error_type": None,
                }
                results[result_idx] = success_result
        except Exception:
            for task in tasks:
                task.cancel()
            raise
    else:
        gathered: list[ContactTaskResult | BaseException] = await asyncio.gather(
            *tasks, return_exceptions=True
        )
        for idx, result in enumerate(gathered):
            if isinstance(result, Exception):
                failed_result: BatchContactCreateResult = {
                    "index": idx,
                    "success": False,
                    "id": None,
                    "data": None,
                    "error": str(result),
                    "error_type": type(result).__name__,
                }
                results[idx] = failed_result
            elif not isinstance(result, BaseException):
                result_idx, contact_data, contact_id = result
                ok_result: BatchContactCreateResult = {
                    "index": result_idx,
                    "success": True,
                    "id": contact_id,
                    "data": contact_data,
                    "error": None,
                    "error_type": None,
                }
                results[result_idx] = ok_result

    finalized_items = [item for item in results if item is not None]
    finalized_results = [
        _with_legacy_contact_keys(item, include_legacy_keys=include_legacy_keys)
        for item in finalized_items
    ]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(contacts_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


__all__ = ["BatchContactCreateResult", "acreate_contacts_batch"]
