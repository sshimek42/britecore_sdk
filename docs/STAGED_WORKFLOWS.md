# Staged Workflow Creation

This document describes the **staged workflow batching** helpers in the BriteCore SDK,
which orchestrate dependent object creation in the correct order while maximizing
concurrency within each stage.

---

## Why Staged Workflows?

BriteCore objects have dependencies:

- A **risk** requires a **revision**, which belongs to a **policy**.
- A **policy** may require a **contact** as the named insured.

You cannot create 500 policies in parallel and then link risks — you need the
`revision_id` that comes back from each policy create before you can create
risks for that policy. The staged workflow helpers solve this:

```text
Stage 1 (parallel): Create contacts     → produces contact_ids
Stage 2 (parallel): Create quotes       → produces quote_ids     (optional)
Stage 3 (parallel): Create policies     → produces revision_ids
Stage 4 (parallel): Create risks        → uses revision_ids
```

Each stage runs all items concurrently with a bounded worker pool. Stages
execute sequentially so that IDs flow from one stage to the next.

---

## Quick Start

### Synchronous (ThreadPoolExecutor)

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.workflows import create_entities_staged_batch

init_api_client("my-site")

jobs = [
    {
        "contact_payload": {
            "name": "Jane Doe",
            "address": [
                {"address1": "123 Main St", "city": "Springfield",
                 "state": "IL", "zip": "62701"}
            ],
        },
        "policy_payload": {
            "policy_number": "POL-001",
            "policy_type_id": "pt-uuid-here",
        },
        "risk_payloads": [{"property_group_number": 1}],
    },
    # ... more jobs
]

result = create_entities_staged_batch(
    jobs,
    contact_max_workers=5,
    policy_max_workers=3,
    risk_max_workers=3,
    fail_fast=False,
)

print(f"Total: {result['total']}, Succeeded: {result['succeeded']}, "
      f"Failed: {result['failed']}")

for item in result["results"]:
    if item["success"]:
        print(f"  [{item['index']}] contact={item['contact_id']}  "
              f"revision={item['revision_id']}  "
              f"risks={item['risk_ids']}")
    else:
        print(f"  [{item['index']}] FAILED at '{item['failed_stage']}': "
              f"{item['error']}")
```

### Asynchronous (asyncio)

```python
import asyncio
from britecore_sdk.api.api_calls import init_async_api_client
from britecore_sdk.api.workflows import acreate_entities_staged_batch

init_async_api_client("my-site")

async def main():
    result = await acreate_entities_staged_batch(
        jobs,
        contact_max_concurrent=5,
        policy_max_concurrent=3,
        risk_max_concurrent=3,
    )
    print(result)

asyncio.run(main())
```

---

## Job Format

Each `StagedWorkflowJob` is a dict with optional stage payloads:

| Key | Type | Description |
|-----|------|-------------|
| `contact_payload` | `dict` | Kwargs for `new_contact`. Required: `name`, `address`. Optional: `phone`, `email`, `contact_type`. |
| `quote_payload` | `dict` | Full quote payload for `create_full_quote`. |
| `policy_payload` | `dict` | Kwargs for `create_policy`. |
| `risk_payloads` | `list[dict]` | List of risk payloads for `create_risk`. `revision_id` is injected from the policy stage when omitted. |

Omitting a payload key skips that stage for that job. For example, jobs
without `contact_payload` skip the contacts stage entirely.

---

## Result Format

```python
{
    "total": int,           # Total jobs submitted
    "succeeded": int,       # Jobs where all stages succeeded
    "failed": int,          # Jobs with at least one failed stage
    "stage_totals": {
        "contacts":  {"total": N, "succeeded": M, "failed": P},
        "quotes":    {"total": N, "succeeded": M, "failed": P},
        "policies":  {"total": N, "succeeded": M, "failed": P},
        "risks":     {"total": N, "succeeded": M, "failed": P},
    },
    "results": [
        {
            "index": 0,             # Input list position
            "success": True,
            "contact_id": "...",
            "contact_data": {...},
            "quote_id": "...",
            "quote_data": {...},
            "revision_id": "...",
            "policy_data": {...},
            "risk_ids": ["...", "..."],
            "risk_results": [...],
            "error": None,
            "failed_stage": None,   # "contacts"|"quotes"|"policies"|"risks"
        },
        # ...
    ],
}
```

---

## Concurrency Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `contact_max_workers` / `contact_max_concurrent` | `5` | Contacts are fast creates |
| `quote_max_workers` / `quote_max_concurrent` | `5` | Quotes are fast creates |
| `policy_max_workers` / `policy_max_concurrent` | `3` | Conservative; each policy triggers heavy backend work |
| `risk_max_workers` / `risk_max_concurrent` | `3` | Conservative; risks are created per-revision |

**Tuning guidance:**

- Start with the defaults. If your BriteCore instance can handle more concurrency
  without returning 429 or timing out, increase incrementally.
- Never set `policy_max_workers > 10` without testing. Policy creation triggers
  underwriting rules, rating, and other backend work.
- For very large batches (500+ jobs), consider chunking into groups of 50–100
  and calling the helper in a loop.

---

## fail_fast Behavior

When `fail_fast=True`:

- The first exception within any stage is re-raised immediately.
- Remaining concurrent futures/tasks for that stage are cancelled.
- **Subsequent stages do not run at all.**

When `fail_fast=False` (default):

- Each item's failure is captured in `results[i]["error"]` and
  `results[i]["failed_stage"]`.
- Items that fail a stage are excluded from subsequent stages (to avoid creating
  dependent objects without their parent IDs).
- Processing continues for all remaining items.

---

## Rate Limiting Integration

Pass `RequestParameters` kwargs directly to the helper, and they will be
forwarded to every underlying API call:

```python
result = create_entities_staged_batch(
    jobs,
    request_timeout=30,      # seconds per individual call
    request_retries=2,
)
```

If your `BritecoreAPIClient` is initialized with rate limiting enabled, all
calls automatically go through the rate limiter. See
[RATE_LIMITING.md](RATE_LIMITING.md) for details.

---

## Adding New Stages

The staged workflow abstraction is designed to be extensible. To add a new
stage (e.g., "Attachments"), follow this pattern in `staged_creation.py`:

```python
# 1. Import the endpoint function at module level
from britecore_sdk.api.api_calls.v2.attachments import create_attachment

# 2. Add a new key to StagedWorkflowJob
class StagedWorkflowJob(TypedDict, total=False):
    ...
    attachment_payloads: list[dict[str, Any]]

# 3. Add a stage block after the existing risk stage
attachment_pending = [
    i for i, job in enumerate(jobs)
    if job.get("attachment_payloads") and i not in all_failed_so_far
]
# ... (follow the same _run_stage pattern)
```

The same pattern applies to the async variant in `async_staged_creation.py`.

---

## See Also

- `examples/staged_workflow_creation.py` — runnable sync + async examples
- `docs/LINE_EXTRACT_STITCHING.md` — stitched line file extract helper
- `docs/BATCH_QUOTE_CREATION.md` — quote-specific batch docs
- `docs/RATE_LIMITING.md` — rate limiter integration
