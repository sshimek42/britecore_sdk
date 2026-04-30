# Line File Extract Stitching

This document describes the **stitched line file extract** helpers in the BriteCore SDK,
which retrieve export data for multiple lines and merge the results into a single
structured response.

---

## Background: Why Stitching?

BriteCore's `get_export_line_file` endpoint is called **once per line** (LOB/state
combination). Each call can take **45–60 seconds** to complete because the server
processes the full line configuration before responding.

There is no single "get all lines at once" endpoint. To retrieve N lines you must
make N separate requests and then combine the results — that's what the stitching
helper does.

---

## Important: Timeout Guidance

> ⚠️ **Always pass an explicit `request_timeout`.**  
> The default SDK timeout is 5 seconds, which is far too short for line file
> extracts. Set `request_timeout` to at least 90 seconds, and ideally 120–180.

```python
result = get_export_line_files_stitched(
    lines,
    request_timeout=120,   # 2 minutes per extract call
)
```

---

## Quick Start

### Synchronous

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2.lines import get_export_line_files_stitched

init_api_client("my-site")

# Each tuple: (effective_date_id, state_id, line_id)
lines = [
    ("eff-uuid-1", "state-uuid-1", "line-uuid-1"),
    ("eff-uuid-2", "state-uuid-2", "line-uuid-2"),
    ("eff-uuid-3", "state-uuid-3", "line-uuid-3"),
]

result = get_export_line_files_stitched(
    lines,
    max_workers=2,          # Low concurrency — these are long-running calls
    include_custom_sequences=False,
    request_timeout=120,    # REQUIRED: default 5s is too short
)

print(f"Extracted {result['succeeded']}/{result['total']} lines successfully")

for item in result["results"]:
    if item["success"]:
        print(f"  Line {item['line'][2]}: {len(item['data'])} bytes")
    else:
        print(f"  Line {item['line'][2]} FAILED: {item['error']}")
```

### Asynchronous

```python
import asyncio
from britecore_sdk.api.api_calls import init_async_api_client
from britecore_sdk.api.api_calls.v2.async_lines import aget_export_line_files_stitched

init_async_api_client("my-site")

async def main():
    result = await aget_export_line_files_stitched(
        lines,
        max_concurrent=2,
        include_custom_sequences=False,
        request_timeout=120,
    )
    return result

result = asyncio.run(main())
```

---

## Line Tuple Format

Each element in the `lines` list is a 3-tuple:

```python
(effective_date_id, state_id, line_id)
```

Retrieve these IDs using the supporting helpers:

```python
from britecore_sdk.api.api_calls.v2 import lines

# 1. Get available effective dates
eff_dates = lines.get_all_effective_dates()

# 2. Get states for an effective date
states = lines.get_all_states(effective_date_id="eff-uuid")

# 3. Get lines for effective date + state
available_lines = lines.get_all_lines(effective_date_id="eff-uuid")
```

---

## Concurrency Guidance

| Setting | Recommended | Notes |
|---------|------------|-------|
| `max_workers` / `max_concurrent` | **1–2** | Each call is 45–60s; more concurrency often causes server-side contention |
| `request_timeout` | **120–180s** | Accounts for variability in extract time |
| Retry | **0–1** | Avoid retrying long jobs unless you're confident the failure was transient |

**Why low concurrency?**

- Each extract call saturates a backend processing thread.
- Running 5+ extracts in parallel often makes all of them slower (or timeout).
- 2 concurrent extracts at 60s each ≈ 60s wall time vs 5 sequential ≈ 300s.
  That's a reasonable trade-off for most use cases.

---

## Result Format

```python
{
    "total": int,           # Number of lines requested
    "succeeded": int,       # Successful extracts
    "failed": int,          # Failed extracts
    "results": [
        {
            "index": 0,         # Position in the input list
            "line": ("eff-id", "state-id", "line-id"),
            "success": True,
            "data": {...},      # Parsed JSON payload from the extract
            "error": None,
        },
        {
            "index": 1,
            "line": ("eff-id-2", "state-id-2", "line-id-2"),
            "success": False,
            "data": None,
            "error": "Request timed out after 120s",
        },
    ],
}
```

Results are ordered by input index, making it easy to correlate output
with the original `lines` list.

---

## Error Handling

Failures for individual lines do **not** abort the rest of the extract:

```python
result = get_export_line_files_stitched(lines, request_timeout=120)

succeeded = [r for r in result["results"] if r["success"]]
failed = [r for r in result["results"] if not r["success"]]

# Retry failed lines individually with an even longer timeout
if failed:
    retry_lines = [r["line"] for r in failed]
    retry_result = get_export_line_files_stitched(
        retry_lines,
        max_workers=1,
        request_timeout=180,
    )
```

---

## Single-Line Extract

To retrieve a single line, use the underlying `get_export_line_file` directly:

```python
from britecore_sdk.api.api_calls.v2.lines import get_export_line_file

data = get_export_line_file(
    ("eff-uuid", "state-uuid", "line-uuid"),
    request_timeout=120,
)
```

---

## See Also

- `examples/stitched_line_extract.py` — runnable sync + async examples
- `docs/STAGED_WORKFLOWS.md` — staged workflow helper for object creation
- `docs/BATCH_QUOTE_CREATION.md` — batch quote creation
