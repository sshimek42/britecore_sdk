"""Synchronous staged workflow helper for bulk creation of BriteCore objects.

This module orchestrates multi-stage creation workflows in dependency order:

    Stage 1: Contacts  (optional)
    Stage 2: Quotes    (optional)
    Stage 3: Policies  (creates revision_id)
    Stage 4: Risks     (optional; requires revision_id from Stage 3)

Within each stage, all pending items run concurrently using a bounded
``ThreadPoolExecutor``.  Stages execute sequentially so that IDs produced
by earlier stages are available to later ones.

Typical usage::

    from britecore_sdk.api.workflows.staged_creation import (
        create_entities_staged_batch,
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

    result = create_entities_staged_batch(
        jobs,
        contact_max_workers=5,
        policy_max_workers=3,
        risk_max_workers=3,
        fail_fast=False,
    )

See ``docs/STAGED_WORKFLOWS.md`` for tuning guidance and integration notes.
"""

from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from logging import Logger
from typing import Any, TypedDict, Unpack

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2.contacts import new_contact
from britecore_sdk.api.api_calls.v2.policies import create_policy, create_risk
from britecore_sdk.api.api_calls.v2.quotes import create_full_quote

LOGGER: Logger = logger


class StagedWorkflowJob(TypedDict, total=False):
    """Input descriptor for a single end-to-end entity creation job.

    All stage payloads are optional; omit a payload to skip that stage for
    this job.  When ``contact_payload`` is present, the created
    ``contact_id`` is made available for subsequent stages.

    Fields
    ------
    contact_payload:
        Keyword arguments for ``new_contact``.  Required keys: ``name``
        (str), ``address`` (list[dict]).  Optional: ``phone``, ``email``,
        ``contact_type``.
    quote_payload:
        Full quote payload dict forwarded to ``create_full_quote``.
    policy_payload:
        Keyword arguments forwarded to ``create_policy``.
    risk_payloads:
        List of risk payload dicts, each forwarded to ``create_risk``.
        ``revision_id`` is injected automatically when omitted.
    """

    contact_payload: dict[str, Any]
    quote_payload: dict[str, Any]
    policy_payload: dict[str, Any]
    risk_payloads: list[dict[str, Any]]


class StagedWorkflowResult(TypedDict):
    """Per-job outcome returned by ``create_entities_staged_batch``."""

    index: int
    success: bool
    contact_id: str | None
    contact_data: dict[str, Any] | None
    quote_id: str | None
    quote_data: dict[str, Any] | None
    revision_id: str | None
    policy_data: dict[str, Any] | None
    risk_ids: list[str]
    risk_results: list[Any]
    error: str | None
    failed_stage: str | None


def _run_stage(
    stage_name: str,
    pending_indices: list[int],
    worker_fn: Any,
    max_workers: int,
    fail_fast: bool,
    per_item_results: list[StagedWorkflowResult | None],
) -> tuple[list[int], bool]:
    """Execute one stage over ``pending_indices`` using a bounded thread pool.

    Returns ``(still_pending, had_error)`` so the caller can decide whether
    to advance to the next stage.

    Parameters
    ----------
    stage_name:
        Human-readable label for log messages and ``failed_stage`` fields.
    pending_indices:
        Indices into ``per_item_results`` that should be processed this stage.
    worker_fn:
        Callable ``(index: int) -> None`` that mutates ``per_item_results``
        in place.  Raising an exception marks the item as failed.
    max_workers:
        Upper bound on concurrent futures.
    fail_fast:
        When ``True``, the first exception cancels remaining futures and is
        re-raised.
    per_item_results:
        Shared result list mutated by ``worker_fn``.

    Returns
    -------
    tuple[list[int], bool]
        ``(still_pending, had_error)``
    """
    if not pending_indices:
        return [], False

    worker_count = min(max_workers, len(pending_indices))
    still_pending: list[int] = []
    had_error = False

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        future_map: dict[Future[None], int] = {
            executor.submit(worker_fn, idx): idx for idx in pending_indices
        }

        for future in as_completed(future_map):
            idx = future_map[future]
            try:
                future.result()
                still_pending.append(idx)
            except Exception as exc:
                had_error = True
                result = per_item_results[idx]
                if result is not None:
                    result["success"] = False
                    result["error"] = str(exc)
                    result["failed_stage"] = stage_name
                LOGGER.error(
                    "Staged workflow error [stage=%s, index=%d]: %s",
                    stage_name,
                    idx,
                    exc,
                )
                if fail_fast:
                    for pending in future_map:
                        pending.cancel()
                    raise

    return still_pending, had_error


def create_entities_staged_batch(
    jobs: list[StagedWorkflowJob],
    *,
    contact_max_workers: int = 5,
    quote_max_workers: int = 5,
    policy_max_workers: int = 3,
    risk_max_workers: int = 3,
    fail_fast: bool = False,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """Create contacts, quotes, policies, and risks in a staged batch workflow.

    Stages execute in dependency order; within each stage all pending items
    run concurrently with bounded workers.  Stages are:

    1. **Contacts** — ``new_contact`` (optional per job)
    2. **Quotes** — ``create_full_quote`` (optional per job)
    3. **Policies** — ``create_policy`` (optional per job; produces
       ``revision_id`` used by the risks stage)
    4. **Risks** — ``create_risk`` (optional per job; uses ``revision_id``
       from Stage 3 when not supplied)

    Any job that fails a stage is excluded from subsequent stages.  When
    ``fail_fast=True`` the first failure re-raises immediately; otherwise
    failures are captured per item and processing continues.

    Args:
        jobs: List of :class:`StagedWorkflowJob` dicts describing one
            end-to-end creation per element.
        contact_max_workers: Max concurrent workers for the contacts stage.
            Defaults to ``5``.
        quote_max_workers: Max concurrent workers for the quotes stage.
            Defaults to ``5``.
        policy_max_workers: Max concurrent workers for the policies stage.
            Defaults to ``3`` (conservative; each policy create is heavy).
        risk_max_workers: Max concurrent workers for the risks stage.
            Defaults to ``3``.
        fail_fast: When ``True``, re-raises the first stage exception and
            cancels remaining futures.  Defaults to ``False``.
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
    # Stages execute in dependency order; all imports are at module level to
    # allow mocking in tests.
    if not jobs or not isinstance(jobs, list):
        raise BritecoreError.MissingParameter(
            "jobs is required and must be a non-empty list"
        )

    # Initialize per-item results
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

    def _create_contact(idx: int) -> None:
        payload = jobs[idx]["contact_payload"]
        contact_data, contact_id = new_contact(
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

    contact_still_pending, _ = _run_stage(
        "contacts",
        contact_pending,
        _create_contact,
        contact_max_workers,
        fail_fast,
        results,  # type: ignore[arg-type]
    )
    stage_totals["contacts"]["succeeded"] = len(contact_still_pending)
    stage_totals["contacts"]["failed"] = (
        stage_totals["contacts"]["total"] - stage_totals["contacts"]["succeeded"]
    )

    # All jobs (with or without contact) advance to quotes unless they failed
    # Jobs that failed contacts are excluded from later stages
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

    def _create_quote(idx: int) -> None:
        payload = jobs[idx]["quote_payload"]
        quote_data, quote_id = create_full_quote(payload, **kwargs)
        result = results[idx]
        if result is not None:
            result["quote_data"] = quote_data
            result["quote_id"] = quote_id

    quote_still_pending, _ = _run_stage(
        "quotes",
        quote_pending,
        _create_quote,
        quote_max_workers,
        fail_fast,
        results,  # type: ignore[arg-type]
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

    def _create_policy(idx: int) -> None:
        payload = dict(jobs[idx]["policy_payload"])
        policy_data, revision_id = create_policy(**payload, **kwargs)
        result = results[idx]
        if result is not None:
            result["policy_data"] = policy_data
            result["revision_id"] = revision_id

    policy_still_pending, _ = _run_stage(
        "policies",
        policy_pending,
        _create_policy,
        policy_max_workers,
        fail_fast,
        results,  # type: ignore[arg-type]
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

    def _create_risks(idx: int) -> None:
        risk_payloads = jobs[idx].get("risk_payloads") or []
        result = results[idx]
        revision_id = result["revision_id"] if result else None
        risk_ids: list[str] = []
        risk_results_list: list[Any] = []
        for rp in risk_payloads:
            payload = dict(rp)
            if "revision_id" not in payload and revision_id:
                payload["revision_id"] = revision_id
            risk_data = create_risk(**payload, **kwargs)
            risk_results_list.append(risk_data)
            if isinstance(risk_data, dict):
                rid = risk_data.get("risk_id") or risk_data.get("id")
                if rid:
                    risk_ids.append(rid)
        if result is not None:
            result["risk_ids"] = risk_ids
            result["risk_results"] = risk_results_list

    risk_still_pending, _ = _run_stage(
        "risks",
        risk_pending,
        _create_risks,
        risk_max_workers,
        fail_fast,
        results,  # type: ignore[arg-type]
    )
    stage_totals["risks"]["succeeded"] = len(risk_still_pending)
    stage_totals["risks"]["failed"] = (
        stage_totals["risks"]["total"] - stage_totals["risks"]["succeeded"]
    )

    # ------------------------------------------------------------------ #
    # Finalize results                                                     #
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
    "StagedWorkflowJob",
    "StagedWorkflowResult",
    "create_entities_staged_batch",
]
