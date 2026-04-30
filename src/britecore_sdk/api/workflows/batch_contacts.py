"""Sync batch workflow helpers for contact creation.

This module houses higher-level orchestration for bulk contact creation.
Endpoint wrappers for individual contact calls live in
``britecore_sdk.api.api_calls.v2.contacts``.
"""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any, TypedDict, Unpack

from britecore_sdk import BritecoreError
from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2.contacts import new_contact


class BatchContactCreateResult(TypedDict):
    """Per-item outcome for ``create_contacts_batch``."""

    index: int
    success: bool
    contact_data: dict[str, Any] | None
    contact_id: str | None
    error: str | None


def create_contacts_batch(
    contacts_json: list[dict[str, Any]],
    max_workers: int = 5,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many contacts concurrently and return per-item outcomes.

    This helper runs ``new_contact(...)`` in a bounded thread pool so
    high-volume contact creation jobs complete much faster than fully
    serial execution. Each payload dict must include ``name`` and
    ``address`` keys (matching ``new_contact`` parameters).

    Args:
        contacts_json: List of contact payload dicts.  Each dict must contain
            at minimum ``name`` (str) and ``address`` (list[dict]).  Optional
            keys ``phone``, ``email``, and ``contact_type`` are forwarded if
            present.
        max_workers: Maximum concurrent workers.  Defaults to ``5``.
        fail_fast: When ``True``, re-raises the first encountered exception
            and cancels pending futures.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each contact create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list[BatchContactCreateResult] ordered by input index

    Raises:
        BritecoreError.MissingParameter: If ``contacts_json`` is missing/empty.
        ValueError: If ``max_workers`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not contacts_json or not isinstance(contacts_json, list):
        raise BritecoreError.MissingParameter(
            "contacts_json is required and must be a non-empty list"
        )
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")

    worker_count = min(max_workers, len(contacts_json))
    results: list[BatchContactCreateResult | None] = [None] * len(contacts_json)

    def _create_one(index: int, payload: dict[str, Any]) -> tuple[int, Any, str | None]:
        contact_data, contact_id = new_contact(
            name=payload["name"],
            address=payload["address"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            contact_type=payload.get("contact_type", "individual"),
            **kwargs,
        )
        return index, contact_data, contact_id

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map: dict[Future[tuple[int, Any, str | None]], int] = {
            executor.submit(_create_one, idx, payload): idx
            for idx, payload in enumerate(contacts_json)
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                result_idx, contact_data, contact_id = future.result()
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "contact_data": contact_data,
                    "contact_id": contact_id,
                    "error": None,
                }
            except Exception as exc:
                if fail_fast:
                    for pending in future_map:
                        pending.cancel()
                    raise
                results[idx] = {
                    "index": idx,
                    "success": False,
                    "contact_data": None,
                    "contact_id": None,
                    "error": str(exc),
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


__all__ = ["BatchContactCreateResult", "create_contacts_batch"]
