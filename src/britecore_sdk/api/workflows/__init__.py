"""Staged workflow helpers for orchestrating dependent BriteCore object creation.

This package provides synchronous and asynchronous helpers that execute
creation workflows in dependency order:

    Contacts → Quotes → Policies/Revisions → Risks

Within each stage, items run concurrently with bounded concurrency.

Modules
-------
staged_creation
    Synchronous staged workflow helper using ``ThreadPoolExecutor``.
async_staged_creation
    Asynchronous staged workflow helper using ``asyncio``.

Quick start::

    from britecore_sdk.api.workflows import create_entities_staged_batch

    jobs = [
        {
            "contact_payload": {"name": "Jane Doe", "address": [...]},
            "policy_payload": {"policy_number": "POL-001", "policy_type_id": "..."},
            "risk_payloads": [{"property_group_number": 1}],
        },
        ...
    ]

    result = create_entities_staged_batch(jobs)

See ``docs/STAGED_WORKFLOWS.md`` and ``examples/staged_workflow_creation.py``
for detailed usage and tuning guidance.
"""

from britecore_sdk.api.workflows.staged_creation import (
    StagedWorkflowJob,
    StagedWorkflowResult,
    create_entities_staged_batch,
)
from britecore_sdk.api.workflows.async_staged_creation import (
    acreate_entities_staged_batch,
)

__all__ = [
    "StagedWorkflowJob",
    "StagedWorkflowResult",
    "acreate_entities_staged_batch",
    "create_entities_staged_batch",
]
