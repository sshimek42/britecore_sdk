# Batch Quote Creation Guide

*Last updated: July 27, 2026*
*Document type: Implementation guide*

## Overview

The BriteCore SDK provides **synchronous and asynchronous batch quote creation helpers** to efficiently handle high-volume quote creation workflows. This guide explains how to use batch operations to create 100+ quotes in minutes instead of hours.

## Problem Statement

Without batching, creating quotes sequentially results in excessive runtime:

```text
100 quotes × 5-10 seconds per quote = 8-17 minutes
```

**Batch creation with concurrency reduces this to 2-3 minutes** (5-6× faster), making long-running automation tasks feasible within typical task timeouts.

---

## Quick Start

### Synchronous Batch (Simple)

For scripts and CLI tools:

```python
from britecore_sdk.api.workflows import create_full_quotes_batch

# Generate or load 100+ quote payloads
quotes = [
    {
        "number": f"BATCH-{i:06d}",
        "policy_type_id": "HomeownersPolicy",
        "insured": {...},
        # ... full quote payload
    }
    for i in range(1, 101)
]

# Create all quotes in parallel (max 5 concurrent workers)
result = create_full_quotes_batch(
    quotes,
    max_workers=5,
    fail_fast=False,  # Collect all errors instead of stopping on first
)

print(f"✓ Created {result['succeeded']}/{result['total']} quotes")
if result['failed'] > 0:
    for item in result['results']:
        if not item['success']:
            print(f"  Quote {item['index']}: {item['error']}")
```

### Asynchronous Batch (For Web Services)

For FastAPI, aiohttp, or other async frameworks:

```python
import asyncio
from britecore_sdk.api.workflows import acreate_full_quotes_batch

async def create_batch_quotes():
    # Same quote payloads as above
    quotes = [...]

    # Create all quotes concurrently (max 5 concurrent coroutines)
    result = await acreate_full_quotes_batch(
        quotes,
        max_concurrent=5,
        fail_fast=False,
    )

    return result

# In your async handler:
result = await create_batch_quotes()
```

---

## API Reference

### Synchronous: `create_full_quotes_batch()`

**Location:** `britecore_sdk.api.workflows.batch_quotes`

```python
def create_full_quotes_batch(
    quotes_json: list[dict[str, Any]],
    max_workers: int = 5,
    fail_fast: bool = False,
    include_legacy_keys: bool = True,
    client: BritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|---|
| `quotes_json` | `list[dict]` | **Required** | List of quote payload dicts. |
| `max_workers` | `int` | `5` | Max concurrent threads. Tune based on API rate limits & network I/O. |
| `fail_fast` | `bool` | `False` | If `True`, stop on first error & cancel pending futures. If `False`, collect all errors. |
| `include_legacy_keys` | `bool` | `True` | Include compatibility aliases `quote_id` and `quote_data` in each result item. |
| `client` | `BritecoreAPIClient \| None` | `None` | Optional explicit client override for multi-site/multi-client workflows. |
| `**kwargs` | `RequestParameters` | — | Timeout, retry, header overrides (passed to each create call). |

**Returns:**

```python
{
    "total": int,          # Total submitted quotes
    "succeeded": int,      # Successfully created
    "failed": int,         # Failed creates
    "results": [
        {
            "index": int,                       # Original input index
            "success": bool,                    # True/False
            "id": str | None,                   # Extracted quote ID (on success)
            "data": dict | None,                # Full API response (on success)
            "error": str | None,                # Error message (on failure)
            "error_type": str | None,           # Exception class name (on failure)
            # Optional compatibility aliases when include_legacy_keys=True:
            "quote_id": str | None,
            "quote_data": dict | None,
        },
        ...
    ]
}
```

**Raises:**

- `BritecoreError.MissingParameter`: Empty or invalid `quotes_json`.
- `ValueError`: `max_workers < 1`.
- `Exception`: First worker exception if `fail_fast=True`.

---

### Asynchronous: `acreate_full_quotes_batch()`

**Location:** `britecore_sdk.api.workflows.async_batch_quotes`

```python
async def acreate_full_quotes_batch(
    quotes_json: list[dict[str, Any]],
    max_concurrent: int = 5,
    fail_fast: bool = False,
    include_legacy_keys: bool = True,
    client: AsyncBritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
```

**Parameters:** Same as sync version, except:

| Parameter | Type | Default | Description |
|-----------|------|---------|---|
| `max_concurrent` | `int` | `5` | Max concurrent coroutines (uses `asyncio.Semaphore`). |

**Returns:** Same as sync version.

**Raises:** Same as sync version.

---

## Usage Patterns

### Pattern 1: Simple Batch Creation

Create all quotes at once, accept partial failures:

```python
from britecore_sdk.api.workflows import create_full_quotes_batch

result = create_full_quotes_batch(quotes, max_workers=5, fail_fast=False)

# Log summary
print(f"Created: {result['succeeded']}/{result['total']}")

# Save successful quote IDs to database
successful_ids = [item['id'] for item in result['results'] if item['success']]
db.save_quote_ids(successful_ids)

# Retry failed quotes (optional)
failed_payloads = [
    quotes[item['index']] for item in result['results'] if not item['success']
]
if failed_payloads and len(failed_payloads) < len(quotes):
    retry_result = create_full_quotes_batch(failed_payloads, max_workers=2, fail_fast=False)
```

### Pattern 2: Chunked Batch for Very Large Volumes

For 1000+ quotes, split into chunks to avoid memory/connection exhaustion:

```python
from britecore_sdk.api.workflows import create_full_quotes_batch

quotes = load_1000_quotes()
chunk_size = 50
chunks = [quotes[i:i+chunk_size] for i in range(0, len(quotes), chunk_size)]

all_successful = []
all_failed = []

for chunk_idx, chunk in enumerate(chunks, 1):
    print(f"Processing chunk {chunk_idx}/{len(chunks)}...")
    result = create_full_quotes_batch(chunk, max_workers=5, fail_fast=False)

    all_successful.extend([item['id'] for item in result['results'] if item['success']])
    all_failed.extend([
        {
            'index': item['index'],
            'error': item['error'],
            'payload': chunk[item['index']]
        }
        for item in result['results'] if not item['success']
    ])

print(f"✓ Total created: {len(all_successful)}")
print(f"✗ Total failed: {len(all_failed)}")
```

### Pattern 3: Async with Progress Tracking

For web services, track progress and provide feedback:

```python
import asyncio
from britecore_sdk.api.workflows import acreate_full_quotes_batch

async def batch_create_with_progress(quotes: list, websocket=None):
    """Create quotes and stream progress to WebSocket client."""
    chunk_size = 25
    chunks = [quotes[i:i+chunk_size] for i in range(0, len(quotes), chunk_size)]

    total_succeeded = 0
    total_failed = 0

    for chunk_idx, chunk in enumerate(chunks, 1):
        result = await acreate_full_quotes_batch(chunk, max_concurrent=5)

        total_succeeded += result['succeeded']
        total_failed += result['failed']

        # Stream progress to client
        if websocket:
            await websocket.send_json({
                'chunk': chunk_idx,
                'total_chunks': len(chunks),
                'succeeded_so_far': total_succeeded,
                'failed_so_far': total_failed,
            })

    return {
        'total': len(quotes),
        'succeeded': total_succeeded,
        'failed': total_failed,
    }

# In FastAPI route:
@app.post("/batch-quotes")
async def batch_quotes_endpoint(ws: WebSocket):
    await ws.accept()
    quotes = await ws.receive_json()
    result = await batch_create_with_progress(quotes, websocket=ws)
    await ws.send_json(result)
    await ws.close()
```

### Pattern 4: Fail-Fast for Transactions

When all-or-nothing semantics are required:

```python
from britecore_sdk.api.workflows import create_full_quotes_batch

try:
    result = create_full_quotes_batch(
        quotes,
        max_workers=5,
        fail_fast=True,  # Stop on first error
    )
    # If we reach here, all quotes succeeded
    db.commit()
except Exception as e:
    print(f"Batch failed at first error: {e}")
    db.rollback()
```

---

## Performance Tuning

### Choosing `max_workers` / `max_concurrent`

| Setting | Recommendation |
|---------|---|
| **1** | Debug mode; sequential execution. Useful for testing. |
| **3-5** (default) | Conservative; safe for most API servers. Start here. |
| **10-20** | Aggressive; use if API supports high concurrency & you have sufficient network bandwidth. Monitor for 429 (Too Many Requests) errors. |
| **>20** | Usually unnecessary; hitting network/connection pool limits before API throughput. |

**How to measure:**

1. Start with `max_workers=5`.
2. Monitor batch execution time and API response codes.
3. If you see mostly 200-201 responses and fast completion, try `max_workers=10`.
4. If you see 429s (rate limit) or timeouts, reduce by 2-3.
5. Find the sweet spot where execution time ≈ (total_time / num_quotes) × 5 seconds.

### Example Tuning Session

```python
import time

for max_workers in [3, 5, 10]:
    start = time.time()
    result = create_full_quotes_batch(100_quotes, max_workers=max_workers)
    elapsed = time.time() - start

    print(f"max_workers={max_workers}: {elapsed:.1f}s "
          f"({result['succeeded']}/{result['total']} success, "
          f"{result['failed']} failed)")
```

---

## Error Handling

### Partial Success Workflow

```python
result = create_full_quotes_batch(quotes, max_workers=5, fail_fast=False)

if result['failed'] > 0:
    # Analyze failures
    failures_by_error = {}
    for item in result['results']:
        if not item['success']:
            error_type = item.get('error_type') or item['error'].split(':')[0]
            failures_by_error.setdefault(error_type, []).append({
                'index': item['index'],
                'error': item['error']
            })

    # Log for investigation
    for error_type, items in failures_by_error.items():
        print(f"{error_type}: {len(items)} failures")
        for item in items[:3]:  # Show first 3
            print(f"  Index {item['index']}: {item['error']}")
```

### Retry with Exponential Backoff

```python
import time
from britecore_sdk.api.workflows import create_full_quotes_batch

def batch_with_retry(quotes, max_retries=3):
    failed_payloads = quotes[:]

    for attempt in range(1, max_retries + 1):
        if not failed_payloads:
            break

        print(f"Attempt {attempt}: Creating {len(failed_payloads)} quotes...")
        result = create_full_quotes_batch(failed_payloads, max_workers=5, fail_fast=False)

        # Extract failed for next attempt
        failed_payloads = [
            failed_payloads[item['index']]
            for item in result['results'] if not item['success']
        ]

        if failed_payloads and attempt < max_retries:
            backoff_seconds = 2 ** attempt  # 2s, 4s, 8s
            print(f"  {len(failed_payloads)} failed. Retrying in {backoff_seconds}s...")
            time.sleep(backoff_seconds)

    return result
```

---

## Comparison: Sync vs. Async

| Aspect | Sync (`create_full_quotes_batch`) | Async (`acreate_full_quotes_batch`) |
|--------|---|---|
| **Best For** | Scripts, CLI tools, standalone jobs | Web services, FastAPI, aiohttp |
| **Concurrency** | `ThreadPoolExecutor` (threads) | `asyncio.gather` (coroutines) |
| **Overhead** | Low | Very low (no thread switching) |
| **I/O Efficiency** | Good (threads handle blocking) | Excellent (no blocking) |
| **Integration** | Synchronous codebase | Async/await codebase |
| **Example** | Nightly batch scripts | REST API handlers |

---

## Integration with Rate Limiting

Batch operations work well with the SDK's **rate limiter**. Enable it to prevent cascading 429 errors across parallel workers:

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.workflows import create_full_quotes_batch

# Initialize client with rate limiting enabled
client = init_api_client("production")
client.rate_limiter.enable()

# Now batch operations respect the configured rate limit
result = create_full_quotes_batch(quotes, max_workers=10)
# Workers will automatically throttle to stay within the rate limit
```

See [RATE_LIMITING.md](./RATE_LIMITING.md) for configuration options.

---

## Real-World Example: Nightly Batch Job

```python
"""
Nightly quote creation job: processes up to 200 quotes from a queue,
creates them in parallel, and logs results.
"""

import logging
import sys
from datetime import datetime

from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.workflows import create_full_quotes_batch

logger = logging.getLogger(__name__)


def main():
    # Initialize API client
    init_api_client("production", enable_rate_limiter=True)

    # Load quotes from database
    quotes = db.load_pending_quotes(limit=200)
    if not quotes:
        logger.info("No pending quotes. Exiting.")
        return 0

    logger.info(f"Creating {len(quotes)} quotes...")
    start = datetime.now()

    # Create in batches of 50 quotes each (4 chunks)
    all_results = []
    chunk_size = 50

    for chunk_idx in range(0, len(quotes), chunk_size):
        chunk = quotes[chunk_idx : chunk_idx + chunk_size]
        logger.info(f"Processing chunk {chunk_idx // chunk_size + 1}...")

        result = create_full_quotes_batch(
            chunk,
            max_workers=5,
            fail_fast=False,
        )

        all_results.extend(result['results'])

        logger.info(
            f"  Chunk: {result['succeeded']}/{result['total']} "
            f"succeeded, {result['failed']} failed"
        )

    elapsed = datetime.now() - start

    # Log summary
    total_succeeded = sum(1 for r in all_results if r['success'])
    total_failed = len(all_results) - total_succeeded

    logger.info(
        f"Nightly batch complete: {total_succeeded}/{len(all_results)} "
        f"succeeded in {elapsed.total_seconds():.1f}s"
    )

    # Save results
    db.save_batch_results({
        'timestamp': datetime.now(),
        'total': len(all_results),
        'succeeded': total_succeeded,
        'failed': total_failed,
        'duration_seconds': elapsed.total_seconds(),
    })

    # Alert on failures
    if total_failed > 0:
        failed_items = [r for r in all_results if not r['success']]
        logger.error(
            f"{total_failed} quotes failed. Sample errors:\n" +
            "\n".join(f"  {item['error']}" for item in failed_items[:5])
        )
        return 1

    return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    sys.exit(main())
```

---

## Troubleshooting

### Issue: Slow Batch Execution

**Symptoms:** Batch takes 5+ minutes for 100 quotes.

**Diagnosis:**
1. Check `max_workers` — if it's 1 or 2, increase it.
2. Check network latency — run `curl -w '@curl-format.txt' -o /dev/null -s https://<api-url>` to measure response time.
3. Check API server logs for errors (5xx responses).
4. Enable debug logging:

   ```python
   import logging
   logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)
   ```

### Issue: 429 (Too Many Requests) Errors

**Solution:** Enable rate limiter or reduce `max_workers`:

```python
# Option 1: Enable SDK rate limiter
client.rate_limiter.enable()
result = create_full_quotes_batch(quotes, max_workers=10)

# Option 2: Reduce workers
result = create_full_quotes_batch(quotes, max_workers=3)

# Option 3: Add delay between workers
import time
time.sleep(0.5)  # Add delay between batch calls
```

### Issue: Connection Pool Exhausted

**Symptoms:** `ConnectionError: Max retries exceeded`.

**Solution:** Reduce `max_workers` or increase connection pool size in `urllib3`:

```python
# Reduce workers (simplest)
result = create_full_quotes_batch(quotes, max_workers=3)
```

### Issue: Memory Usage Grows During Batch

**Solution:** Use chunked batch pattern (see "Chunked Batch for Very Large Volumes" above).

```python
# Instead of:
result = create_full_quotes_batch(all_1000_quotes, max_workers=5)

# Use:
result = process_in_chunks(all_1000_quotes, chunk_size=100)
```

---

## Performance Benchmarks

Typical execution times for 100 quotes (5-10 seconds each):

| Configuration | Time | Speedup |
|---|---|---|
| Sequential (1 worker) | 8-17 min | — |
| `max_workers=3` | 3-6 min | 2.5× |
| `max_workers=5` (default) | 2-4 min | **4-5×** |
| `max_workers=10` (with rate limiting) | 1.5-3 min | **5-6×** |

*Note: Actual times depend on API response latency, network conditions, and quote payload complexity.*

---

## See Also

- [Rate Limiting](./RATE_LIMITING.md) — Configure automatic backoff for 429 responses.
- [Examples](../examples/batch_quote_creation.py) — Runnable code samples.
- [API Reference](./api_reference.rst) — Full endpoint documentation.
