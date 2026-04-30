"""Higher-level workflow helpers for the BriteCore SDK.

This package provides both staged workflow helpers that orchestrate dependent
object creation and batch helpers for bulk parallel operations.

Staged workflow helpers
-----------------------
Execute creation workflows in dependency order:

    Contacts → Quotes → Policies/Revisions → Risks

Within each stage, items run concurrently with bounded concurrency.

- :mod:`britecore_sdk.api.workflows.staged_creation` — synchronous staged
  workflow helper using ``ThreadPoolExecutor``
- :mod:`britecore_sdk.api.workflows.async_staged_creation` — asynchronous
  staged workflow helper using ``asyncio``

Batch helpers
-------------
Domain-scoped parallel bulk-create helpers:

- :mod:`britecore_sdk.api.workflows.batch_contacts` /
  :mod:`britecore_sdk.api.workflows.async_batch_contacts` — bulk contact
  creation
- :mod:`britecore_sdk.api.workflows.batch_policies` /
  :mod:`britecore_sdk.api.workflows.async_batch_policies` — bulk policy and
  risk creation
- :mod:`britecore_sdk.api.workflows.batch_quotes` — bulk quote creation via
  ``ThreadPoolExecutor``
- :mod:`britecore_sdk.api.workflows.async_batch_quotes` — bulk quote creation
  via ``asyncio``

All public helpers are re-exported from this package for convenience::

    from britecore_sdk.api.workflows import create_entities_staged_batch
    from britecore_sdk.api.workflows import create_contacts_batch
    from britecore_sdk.api.workflows import create_policies_batch
    from britecore_sdk.api.workflows import create_risks_batch
    from britecore_sdk.api.workflows import create_full_quotes_batch
    from britecore_sdk.api.workflows import acreate_full_quotes_batch

See ``docs/STAGED_WORKFLOWS.md``, ``docs/BATCH_QUOTE_CREATION.md``, and the
``examples/`` directory for usage and tuning guidance.
"""

from britecore_sdk.api.workflows.async_batch_contacts import acreate_contacts_batch
from britecore_sdk.api.workflows.async_batch_policies import (
    acreate_policies_batch,
    acreate_risks_batch,
)
from britecore_sdk.api.workflows.async_batch_quotes import acreate_full_quotes_batch
from britecore_sdk.api.workflows.async_staged_creation import (
    acreate_entities_staged_batch,
)
from britecore_sdk.api.workflows.batch_contacts import (
    BatchContactCreateResult,
    create_contacts_batch,
)
from britecore_sdk.api.workflows.batch_policies import (
    BatchPolicyCreateResult,
    BatchRiskCreateResult,
    create_policies_batch,
    create_risks_batch,
)
from britecore_sdk.api.workflows.batch_quotes import (
    BatchQuoteCreateResult,
    create_full_quotes_batch,
)
from britecore_sdk.api.workflows.staged_creation import (
    StagedWorkflowJob,
    StagedWorkflowResult,
    create_entities_staged_batch,
)

__all__ = [
    # Result types
    "BatchContactCreateResult",
    "BatchPolicyCreateResult",
    "BatchQuoteCreateResult",
    "BatchRiskCreateResult",
    "StagedWorkflowJob",
    "StagedWorkflowResult",
    # Async batch helpers
    "acreate_contacts_batch",
    "acreate_entities_staged_batch",
    "acreate_full_quotes_batch",
    "acreate_policies_batch",
    "acreate_risks_batch",
    # Sync batch helpers
    "create_contacts_batch",
    "create_entities_staged_batch",
    "create_full_quotes_batch",
    "create_policies_batch",
    "create_risks_batch",
]
