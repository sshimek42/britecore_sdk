"""Async batch workflow helpers for policy and risk creation.

This module houses higher-level async orchestration for bulk policy and risk
creation. Endpoint wrappers for individual calls live in
``britecore_sdk.api.api_calls.v2.async_policies``.
"""

import asyncio
from typing import Any

from britecore_sdk import BritecoreError
from britecore_sdk.api.api_calls.v2.async_policies import acreate_policy, acreate_risk
from britecore_sdk.api.workflows.batch_policies import (
    BatchPolicyCreateResult,
    BatchRiskCreateResult,
)

PolicyTaskResult = tuple[int, Any, str | None]
RiskTaskResult = tuple[int, Any, str | None]


async def acreate_policies_batch(
    policies_json: list[dict[str, Any]],
    max_concurrent: int = 3,
    fail_fast: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create many policies concurrently and return per-item outcomes.

    This helper runs ``acreate_policy(...)`` with bounded concurrency so
    high-volume policy creation jobs complete much faster than fully serial
    execution.  Each payload dict is unpacked as keyword arguments to
    ``acreate_policy``.

    Args:
        policies_json: List of policy payload dicts forwarded as kwargs to
            ``acreate_policy``.
        max_concurrent: Maximum concurrent coroutines.  Default is ``3``
            (conservative because each policy create triggers heavy backend
            work).
        fail_fast: When ``True``, raises the first encountered exception and
            cancels remaining tasks.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each policy create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list[BatchPolicyCreateResult] ordered by input index

    Raises:
        BritecoreError.MissingParameter: If ``policies_json`` is missing/empty.
        ValueError: If ``max_concurrent`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not policies_json or not isinstance(policies_json, list):
        raise BritecoreError.MissingParameter(
            "policies_json is required and must be a non-empty list"
        )
    if max_concurrent < 1:
        raise ValueError("max_concurrent must be at least 1")

    results: list[BatchPolicyCreateResult | None] = [None] * len(policies_json)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _create_one_semaphored(
        index: int, payload: dict[str, Any]
    ) -> PolicyTaskResult:
        async with semaphore:
            policy_data, revision_id = await acreate_policy(**payload, **kwargs)
            return index, policy_data, revision_id

    tasks = [
        asyncio.create_task(_create_one_semaphored(idx, payload))
        for idx, payload in enumerate(policies_json)
    ]

    if fail_fast:
        try:
            task_results: list[PolicyTaskResult] = await asyncio.gather(*tasks)
            for result_idx, policy_data, revision_id in task_results:
                success_result: BatchPolicyCreateResult = {
                    "index": result_idx,
                    "success": True,
                    "policy_data": policy_data,
                    "revision_id": revision_id,
                    "error": None,
                }
                results[result_idx] = success_result
        except Exception:
            for task in tasks:
                task.cancel()
            raise
    else:
        gathered: list[PolicyTaskResult | BaseException] = await asyncio.gather(
            *tasks, return_exceptions=True
        )
        for idx, result in enumerate(gathered):
            if isinstance(result, Exception):
                failed_result: BatchPolicyCreateResult = {
                    "index": idx,
                    "success": False,
                    "policy_data": None,
                    "revision_id": None,
                    "error": str(result),
                }
                results[idx] = failed_result
            elif not isinstance(result, BaseException):
                result_idx, policy_data, revision_id = result
                ok_result: BatchPolicyCreateResult = {
                    "index": result_idx,
                    "success": True,
                    "policy_data": policy_data,
                    "revision_id": revision_id,
                    "error": None,
                }
                results[result_idx] = ok_result

    finalized_results = [item for item in results if item is not None]
    succeeded = sum(1 for item in finalized_results if item["success"])
    failed = len(finalized_results) - succeeded

    return {
        "total": len(policies_json),
        "succeeded": succeeded,
        "failed": failed,
        "results": finalized_results,
    }


async def acreate_risks_batch(
    risks_json: list[dict[str, Any]],
    max_concurrent: int = 3,
    fail_fast: bool = False,
    **kwargs: Any,
) -> dict[str, Any]:
    """Create many risks concurrently and return per-item outcomes.

    This helper runs ``acreate_risk(...)`` with bounded concurrency so
    high-volume risk creation jobs complete much faster than fully serial
    execution.  Each payload dict must include ``revision_id``; optional
    keys ``property_group_number``, ``building_number``, and
    ``force_categories`` are forwarded if present.

    Args:
        risks_json: List of risk payload dicts forwarded as kwargs to
            ``acreate_risk``.
        max_concurrent: Maximum concurrent coroutines.  Default is ``3``.
        fail_fast: When ``True``, raises the first encountered exception and
            cancels remaining tasks.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` passed through to each risk create call.

    Returns:
        dict[str, Any]:
            - ``total``: total submitted payload count
            - ``succeeded``: number of successful creates
            - ``failed``: number of failed creates
            - ``results``: list[BatchRiskCreateResult] ordered by input index

    Raises:
        BritecoreError.MissingParameter: If ``risks_json`` is missing/empty.
        ValueError: If ``max_concurrent`` is less than 1.
        Exception: First worker exception when ``fail_fast=True``.
    """
    if not risks_json or not isinstance(risks_json, list):
        raise BritecoreError.MissingParameter(
            "risks_json is required and must be a non-empty list"
        )
    if max_concurrent < 1:
        raise ValueError("max_concurrent must be at least 1")

    results: list[BatchRiskCreateResult | None] = [None] * len(risks_json)
    semaphore = asyncio.Semaphore(max_concurrent)

    async def _create_one_semaphored(
        index: int, payload: dict[str, Any]
    ) -> RiskTaskResult:
        async with semaphore:
            risk_data = await acreate_risk(**payload, **kwargs)
            risk_id: str | None = None
            if isinstance(risk_data, dict):
                risk_id = risk_data.get("risk_id") or risk_data.get("id")
            return index, risk_data, risk_id

    tasks = [
        asyncio.create_task(_create_one_semaphored(idx, payload))
        for idx, payload in enumerate(risks_json)
    ]

    if fail_fast:
        try:
            task_results_risk: list[RiskTaskResult] = await asyncio.gather(*tasks)
            for result_idx, risk_data, risk_id in task_results_risk:
                success_result_risk: BatchRiskCreateResult = {
                    "index": result_idx,
                    "success": True,
                    "risk_data": risk_data,
                    "risk_id": risk_id,
                    "error": None,
                }
                results[result_idx] = success_result_risk
        except Exception:
            for task in tasks:
                task.cancel()
            raise
    else:
        gathered_risk: list[RiskTaskResult | BaseException] = await asyncio.gather(
            *tasks, return_exceptions=True
        )
        for idx, result in enumerate(gathered_risk):
            if isinstance(result, Exception):
                failed_result_risk: BatchRiskCreateResult = {
                    "index": idx,
                    "success": False,
                    "risk_data": None,
                    "risk_id": None,
                    "error": str(result),
                }
                results[idx] = failed_result_risk
            elif not isinstance(result, BaseException):
                result_idx, risk_data, risk_id = result
                ok_result_risk: BatchRiskCreateResult = {
                    "index": result_idx,
                    "success": True,
                    "risk_data": risk_data,
                    "risk_id": risk_id,
                    "error": None,
                }
                results[result_idx] = ok_result_risk

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
    "acreate_policies_batch",
    "acreate_risks_batch",
]
