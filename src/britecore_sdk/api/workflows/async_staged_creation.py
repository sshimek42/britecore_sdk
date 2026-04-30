"""Asynchronous staged workflow helper for bulk creation of BriteCore objects.

Async counterpart to :mod:`staged_creation`.  Stages execute sequentially;
within each stage all pending items run concurrently via ``asyncio.Semaphore``.

Typical usage::

    import asyncio
    from britecore_sdk.api.workflows.async_staged_creation import (
        acreate_entities_staged_batch,
    )

    jobs = [
        {
            "contact_payload": {
                "name": "Jane Doe",
                "address": [{"address1": "123 Main St", "city": "Springfield",
                             "state": "IL", "zip": "62701"}],
            },
            "policy_payload": {
                "policy_number": "POL-001",
                "policy_type_id": "pt-uuid",
            },
            "risk_payloads": [{"property_group_number": 1}],
        },
    ]

    result = asyncio.run(
        acreate_entities_staged_batch(
            jobs,
            contact_max_concurrent=5,
            policy_max_concurrent=3,
            risk_max_concurrent=3,
            fail_fast=False,
        )
    )

See ``docs/STAGED_WORKFLOWS.md`` for tuning guidance and integration notes.
"""

import asyncio
from logging import Logger
from typing import Any, Unpack

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2.async_contacts import anew_contact
from britecore_sdk.api.api_calls.v2.async_policies import acreate_policy, acreate_risk
from britecore_sdk.api.api_calls.v2.async_quotes import acreate_full_quote
from britecore_sdk.api.workflows.staged_creation import (
    StagedWorkflowJob,
    StagedWorkflowResult,
)

LOGGER: Logger = logger


async def _run_stage_async(
    stage_name: str,
    pending_indices: list[int],
    worker_fn: Any,
    max_concurrent: int,
    fail_fast: bool,
    per_item_results: list[StagedWorkflowResult | None],
) -> tuple[list[int], bool]:
    """Execute one async stage over ``pending_indices`` with a semaphore.

    Returns ``(still_pending, had_error)``.
    """
    if not pending_indices:
        return [], False

    semaphore = asyncio.Semaphore(max_concurrent)
    still_pending: list[int] = []
    had_error = False

    async def _bounded(idx: int) -> int:
        async with semaphore:
            await worker_fn(idx)
        return idx

    tasks = [asyncio.create_task(_bounded(idx)) for idx in pending_indices]

    if fail_fast:
        try:
            completed = await asyncio.gather(*tasks)
            still_pending.extend(completed)
        except Exception:
            for t in tasks:
                t.cancel()
            had_error = True
            raise
    else:
        task_results = await asyncio.gather(*tasks, return_exceptions=True)  # type: ignore[assignment]
        for idx, tr in zip(pending_indices, task_results, strict=True):
            if isinstance(tr, Exception):
                had_error = True
                result = per_item_results[idx]
                if result is not None:
                    result["success"] = False
                    result["error"] = str(tr)
                    result["failed_stage"] = stage_name
                LOGGER.error(
                    "Async staged workflow error [stage=%s, index=%d]: %s",
                    stage_name,
                    idx,
                    tr,
                )
            else:
                still_pending.append(idx)

    return still_pending, had_error


async def acreate_entities_staged_batch(
    jobs: list[StagedWorkflowJob],
    *,
    contact_max_concurrent: int = 5,
    quote_max_concurrent: int = 5,
    policy_max_concurrent: int = 3,
    risk_max_concurrent: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create contacts, quotes, policies, and risks in a staged async batch workflow.

    Async counterpart to :func:`~staged_creation.create_entities_staged_batch`.
    Stages execute sequentially in dependency order; within each stage all
    pending items run concurrently bounded by ``asyncio.Semaphore``.

    Stages:

    1. **Contacts** — ``anew_contact`` (optional per job)
    2. **Quotes** — ``acreate_full_quote`` (optional per job)
    3. **Policies** — ``acreate_policy`` (optional per job; produces
       ``revision_id`` used by the risks stage)
    4. **Risks** — ``acreate_risk`` (optional per job; uses ``revision_id``
       from Stage 3 when not supplied)

    Args:
        jobs: List of :class:`StagedWorkflowJob` dicts describing one
            end-to-end creation per element.
        contact_max_concurrent: Max concurrent coroutines for contacts stage.
            Defaults to ``5``.
        quote_max_concurrent: Max concurrent coroutines for quotes stage.
            Defaults to ``5``.
        policy_max_concurrent: Max concurrent coroutines for policies stage.
            Defaults to ``3``.
        risk_max_concurrent: Max concurrent coroutines for risks stage.
            Defaults to ``3``.
        fail_fast: When ``True``, raises the first stage exception and cancels
            remaining tasks.  Defaults to ``False``.
        **kwargs: ``RequestParameters`` forwarded to every API call.

    Returns:
        dict[str, Any]:
            - ``total``: total number of input jobs
            - ``succeeded``: jobs with all requested stages successful
            - ``failed``: jobs that encountered at least one error
            - ``stage_totals``: dict keyed by stage name with
              ``total``, ``succeeded``, ``failed`` sub-dicts
            - ``results``: list of :class:`StagedWorkflowResult` ordered by
              input index

    Raises:
        BritecoreError.MissingParameter: If ``jobs`` is missing/empty.
        Exception: First stage exception when ``fail_fast=True``.
    """
    if not jobs or not isinstance(jobs, list):
        raise BritecoreError.MissingParameter(
            "jobs is required and must be a non-empty list"
        )

    results: list[StagedWorkflowResult | None] = [
        StagedWorkflowResult(
            index=i,
            success=True,
            contact_id=None,
            contact_data=None,
            quote_id=None,
            quote_data=None,
            revision_id=None,
            policy_data=None,
            risk_ids=[],
            risk_results=[],
            error=None,
            failed_stage=None,
        )
        for i in range(len(jobs))
    ]

    stage_totals: dict[str, dict[str, int]] = {
        "contacts": {"total": 0, "succeeded": 0, "failed": 0},
        "quotes": {"total": 0, "succeeded": 0, "failed": 0},
        "policies": {"total": 0, "succeeded": 0, "failed": 0},
        "risks": {"total": 0, "succeeded": 0, "failed": 0},
    }

    # ------------------------------------------------------------------ #
    # Stage 1: Contacts                                                    #
    # ------------------------------------------------------------------ #
    contact_pending = [i for i, job in enumerate(jobs) if job.get("contact_payload")]
    stage_totals["contacts"]["total"] = len(contact_pending)

    async def _create_contact(idx: int) -> None:
        payload = jobs[idx]["contact_payload"]
        contact_data, contact_id = await anew_contact(
            name=payload["name"],
            address=payload["address"],
            phone=payload.get("phone"),
            email=payload.get("email"),
            contact_type=payload.get("contact_type", "individual"),
            **kwargs,
        )
        result = results[idx]
        if result is not None:
            result["contact_data"] = contact_data
            result["contact_id"] = contact_id

    contact_still_pending, _ = await _run_stage_async(
        "contacts",
        contact_pending,
        _create_contact,
        contact_max_concurrent,
        fail_fast,
        results,
    )
    stage_totals["contacts"]["succeeded"] = len(contact_still_pending)
    stage_totals["contacts"]["failed"] = (
        stage_totals["contacts"]["total"] - stage_totals["contacts"]["succeeded"]
    )
    contact_failed = {i for i in contact_pending if i not in contact_still_pending}

    # ------------------------------------------------------------------ #
    # Stage 2: Quotes                                                      #
    # ------------------------------------------------------------------ #
    quote_pending = [
        i
        for i, job in enumerate(jobs)
        if job.get("quote_payload") and i not in contact_failed
    ]
    stage_totals["quotes"]["total"] = len(quote_pending)

    async def _create_quote(idx: int) -> None:
        payload = jobs[idx]["quote_payload"]
        quote_data, quote_id = await acreate_full_quote(payload, **kwargs)
        result = results[idx]
        if result is not None:
            result["quote_data"] = quote_data
            result["quote_id"] = quote_id

    quote_still_pending, _ = await _run_stage_async(
        "quotes",
        quote_pending,
        _create_quote,
        quote_max_concurrent,
        fail_fast,
        results,
    )
    stage_totals["quotes"]["succeeded"] = len(quote_still_pending)
    stage_totals["quotes"]["failed"] = (
        stage_totals["quotes"]["total"] - stage_totals["quotes"]["succeeded"]
    )
    quote_failed = {i for i in quote_pending if i not in quote_still_pending}
    all_failed_so_far = contact_failed | quote_failed

    # ------------------------------------------------------------------ #
    # Stage 3: Policies                                                    #
    # ------------------------------------------------------------------ #
    policy_pending = [
        i
        for i, job in enumerate(jobs)
        if job.get("policy_payload") and i not in all_failed_so_far
    ]
    stage_totals["policies"]["total"] = len(policy_pending)

    async def _create_policy(idx: int) -> None:
        payload = dict(jobs[idx]["policy_payload"])
        policy_data, revision_id = await acreate_policy(**payload, **kwargs)
        result = results[idx]
        if result is not None:
            result["policy_data"] = policy_data
            result["revision_id"] = revision_id

    policy_still_pending, _ = await _run_stage_async(
        "policies",
        policy_pending,
        _create_policy,
        policy_max_concurrent,
        fail_fast,
        results,
    )
    stage_totals["policies"]["succeeded"] = len(policy_still_pending)
    stage_totals["policies"]["failed"] = (
        stage_totals["policies"]["total"] - stage_totals["policies"]["succeeded"]
    )
    policy_failed = {i for i in policy_pending if i not in policy_still_pending}
    all_failed_so_far = all_failed_so_far | policy_failed

    # ------------------------------------------------------------------ #
    # Stage 4: Risks                                                       #
    # ------------------------------------------------------------------ #
    risk_pending = [
        i
        for i, job in enumerate(jobs)
        if job.get("risk_payloads") and i not in all_failed_so_far
    ]
    stage_totals["risks"]["total"] = len(risk_pending)

    async def _create_risks(idx: int) -> None:
        risk_payloads = jobs[idx].get("risk_payloads") or []
        result = results[idx]
        revision_id = result["revision_id"] if result else None
        risk_ids: list[str] = []
        risk_results_list: list[Any] = []
        for rp in risk_payloads:
            payload = dict(rp)
            if "revision_id" not in payload and revision_id:
                payload["revision_id"] = revision_id
            risk_data = await acreate_risk(**payload, **kwargs)
            risk_results_list.append(risk_data)
            if isinstance(risk_data, dict):
                rid = risk_data.get("risk_id") or risk_data.get("id")
                if rid:
                    risk_ids.append(rid)
        if result is not None:
            result["risk_ids"] = risk_ids
            result["risk_results"] = risk_results_list

    risk_still_pending, _ = await _run_stage_async(
        "risks",
        risk_pending,
        _create_risks,
        risk_max_concurrent,
        fail_fast,
        results,
    )
    stage_totals["risks"]["succeeded"] = len(risk_still_pending)
    stage_totals["risks"]["failed"] = (
        stage_totals["risks"]["total"] - stage_totals["risks"]["succeeded"]
    )

    # ------------------------------------------------------------------ #
    # Finalize                                                             #
    # ------------------------------------------------------------------ #
    finalized: list[StagedWorkflowResult] = [
        item for item in results if item is not None
    ]
    succeeded = sum(1 for item in finalized if item["success"])
    failed = len(finalized) - succeeded

    return {
        "total": len(jobs),
        "succeeded": succeeded,
        "failed": failed,
        "stage_totals": stage_totals,
        "results": finalized,
    }


__all__ = [
    "acreate_entities_staged_batch",
]
