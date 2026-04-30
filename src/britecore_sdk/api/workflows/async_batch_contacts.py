"""Async batch workflow helpers for contact creation.

This module houses higher-level async orchestration for bulk contact creation.
Endpoint wrappers for individual contact calls live in
``britecore_sdk.api.api_calls.v2.async_contacts``.
"""

import asyncio
from typing import Any, Unpack

from britecore_sdk import BritecoreError
from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2.async_contacts import anew_contact
from britecore_sdk.api.workflows.batch_contacts import BatchContactCreateResult


async def acreate_contacts_batch(
    contacts_json: list[dict[str, Any]],
    max_concurrent: int = 5,
    fail_fast: bool = False,
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

    results: list[BatchContactCreateResult | None] = [None] * len(contacts_json)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _create_one_semaphored(
        index: int, payload: dict[str, Any]
    ) -> tuple[int, Any, str | None]:
        async with semaphore:
            contact_data, contact_id = await anew_contact(
                name=payload["name"],
                address=payload["address"],
                phone=payload.get("phone"),
                email=payload.get("email"),
                contact_type=payload.get("contact_type", "individual"),
                **kwargs,
            )
            return index, contact_data, contact_id

    tasks = [
        asyncio.create_task(_create_one_semaphored(idx, payload))
        for idx, payload in enumerate(contacts_json)
    ]

    if fail_fast:
        try:
            task_results = await asyncio.gather(*tasks)
            for result_idx, contact_data, contact_id in task_results:
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "contact_data": contact_data,
                    "contact_id": contact_id,
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
                    "contact_data": None,
                    "contact_id": None,
                    "error": str(result),
                }
            else:
                result_idx, contact_data, contact_id = result
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "contact_data": contact_data,
                    "contact_id": contact_id,
                    "error": None,
                }

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(contacts_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


__all__ = ["BatchContactCreateResult", "acreate_contacts_batch"]
