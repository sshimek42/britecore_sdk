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

- :mod:`britecore_sdk.api.workflows.batch_quotes` — bulk quote creation via
  ``ThreadPoolExecutor``
- :mod:`britecore_sdk.api.workflows.async_batch_quotes` — bulk quote creation
  via ``asyncio``

All public helpers are re-exported from this package for convenience::

    from britecore_sdk.api.workflows import create_entities_staged_batch
    from britecore_sdk.api.workflows import create_full_quotes_batch
    from britecore_sdk.api.workflows import acreate_full_quotes_batch

See ``docs/STAGED_WORKFLOWS.md``, ``docs/BATCH_QUOTE_CREATION.md``, and the
``examples/`` directory for detailed usage and tuning guidance.
"""

from britecore_sdk.api.workflows.async_batch_quotes import acreate_full_quotes_batch
from britecore_sdk.api.workflows.async_staged_creation import (
    acreate_entities_staged_batch,
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
    "BatchQuoteCreateResult",
    "StagedWorkflowJob",
    "StagedWorkflowResult",
    "acreate_entities_staged_batch",
    "acreate_full_quotes_batch",
    "create_entities_staged_batch",
    "create_full_quotes_batch",
]
