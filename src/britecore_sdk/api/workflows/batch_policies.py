"""Sync batch workflow helpers for policy and risk creation.

This module houses higher-level orchestration for bulk policy and risk creation.
Endpoint wrappers for individual calls live in
``britecore_sdk.api.api_calls.v2.policies``.
"""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from typing import Any, TypedDict, Unpack

from britecore_sdk import BritecoreError
from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2.policies import create_policy, create_risk


class BatchPolicyCreateResult(TypedDict):
    """Per-item outcome for ``create_policies_batch``."""

    index: int
    success: bool
    policy_data: dict[str, Any] | None
    revision_id: str | None
    error: str | None


class BatchRiskCreateResult(TypedDict):
    """Per-item outcome for ``create_risks_batch``."""

    index: int
    success: bool
    risk_data: dict[str, Any] | None
    risk_id: str | None
    error: str | None


def create_policies_batch(
    policies_json: list[dict[str, Any]],
    max_workers: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many policies concurrently and return per-item outcomes.

    This helper runs ``create_policy(...)`` in a bounded thread pool so
    high-volume policy creation jobs complete much faster than fully
    serial execution.  Each payload dict is unpacked as keyword arguments
    to ``create_policy``; at minimum ``policy_number`` and ``policy_type_id``
    are typically required.

    Args:
        policies_json: List of policy payload dicts.  Each dict is forwarded
            as keyword arguments to ``create_policy``.
        max_workers: Maximum concurrent workers.  Default is ``3`` (conservative
            because each policy create triggers heavy backend work).
        fail_fast: When ``True``, re-raises the first encountered exception and
            cancels pending futures.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each policy create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list[BatchPolicyCreateResult] ordered by input index

    Raises:
        BritecoreError.MissingParameter: If ``policies_json`` is missing/empty.
        ValueError: If ``max_workers`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not policies_json or not isinstance(policies_json, list):
        raise BritecoreError.MissingParameter(
            "policies_json is required and must be a non-empty list"
        )
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")

    worker_count = min(max_workers, len(policies_json))
    results: list[BatchPolicyCreateResult | None] = [None] * len(policies_json)

    def _create_one(index: int, payload: dict[str, Any]) -> tuple[int, Any, str | None]:
        policy_data, revision_id = create_policy(**payload, **kwargs)
        return index, policy_data, revision_id

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map: dict[Future[tuple[int, Any, str | None]], int] = {
            executor.submit(_create_one, idx, payload): idx
            for idx, payload in enumerate(policies_json)
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                result_idx, policy_data, revision_id = future.result()
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "policy_data": policy_data,
                    "revision_id": revision_id,
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
                    "policy_data": None,
                    "revision_id": None,
                    "error": str(exc),
                }

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(policies_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


def create_risks_batch(
    risks_json: list[dict[str, Any]],
    max_workers: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create many risks concurrently and return per-item outcomes.

    This helper runs ``create_risk(...)`` in a bounded thread pool so
    high-volume risk creation jobs complete much faster than fully serial
    execution.  Each payload dict must include a ``revision_id`` key; optional
    keys ``property_group_number``, ``building_number``, and
    ``force_categories`` are forwarded if present.

    Args:
        risks_json: List of risk payload dicts.  Each dict must contain at
            minimum ``revision_id`` (str).
        max_workers: Maximum concurrent workers.  Default is ``3``.
        fail_fast: When ``True``, re-raises the first encountered exception and
            cancels pending futures.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each risk create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list[BatchRiskCreateResult] ordered by input index

    Raises:
        BritecoreError.MissingParameter: If ``risks_json`` is missing/empty.
        ValueError: If ``max_workers`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not risks_json or not isinstance(risks_json, list):
        raise BritecoreError.MissingParameter(
            "risks_json is required and must be a non-empty list"
        )
    if max_workers < 1:
        raise ValueError("max_workers must be at least 1")

    worker_count = min(max_workers, len(risks_json))
    results: list[BatchRiskCreateResult | None] = [None] * len(risks_json)

    def _create_one(index: int, payload: dict[str, Any]) -> tuple[int, Any, str | None]:
        risk_data = create_risk(**payload, **kwargs)
        risk_id: str | None = None
        if isinstance(risk_data, dict):
            risk_id = risk_data.get("risk_id") or risk_data.get("id")
        return index, risk_data, risk_id

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map: dict[Future[tuple[int, Any, str | None]], int] = {
            executor.submit(_create_one, idx, payload): idx
            for idx, payload in enumerate(risks_json)
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                result_idx, risk_data, risk_id = future.result()
                results[result_idx] = {
                    "index": result_idx,
                    "success": True,
                    "risk_data": risk_data,
                    "risk_id": risk_id,
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
                    "risk_data": None,
                    "risk_id": None,
                    "error": str(exc),
                }

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(risks_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


__all__ = [
    "BatchPolicyCreateResult",
    "BatchRiskCreateResult",
    "create_policies_batch",
    "create_risks_batch",
]
