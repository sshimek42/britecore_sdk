"""Example: Staged Workflow Creation for High-Volume Workflows.

This example demonstrates how to efficiently create the full chain of
BriteCore objects (contacts → policies → risks) using the SDK's
staged workflow helpers.  Both synchronous (ThreadPoolExecutor) and
asynchronous (asyncio) approaches are shown.

Use Case:
    A nightly automation task needs to onboard 50 new policyholders,
    each requiring a contact record, a policy, and one or more risks.
    Sequential creation at ~5s per API call would take ~750 seconds.
    With staged batching at default concurrency (3–5 workers per stage),
    total time drops to ~100–150 seconds.

Prerequisites:
    - A configured BriteCore site in your settings file, or use
      ``init_api_client(base_url=..., api_key=...)`` for explicit creds.
    - Valid ``policy_type_id`` UUIDs from your BriteCore instance.

Run:
    python examples/staged_workflow_creation.py
"""

import time
from typing import Any

# In a real script you'd import these at the top. Here we show both:
# Sync:  from britecore_sdk.api.workflows import create_entities_staged_batch
# Async: from britecore_sdk.api.workflows import acreate_entities_staged_batch


def generate_sample_jobs(n: int = 5) -> list[dict[str, Any]]:
    """Generate sample staged workflow jobs for demonstration."""
    jobs = []
    for i in range(n):
        jobs.append(
            {
                "contact_payload": {
                    "name": f"Sample Person {i:03d}",
                    "address": [
                        {
                            "address1": f"{i + 100} Main Street",
                            "city": "Springfield",
                            "state": "IL",
                            "zip": "62701",
                        }
                    ],
                    "phone": [{"number": "555-1234", "type": "Home"}],
                    "email": [{"address": f"person{i}@example.com", "type": "Work"}],
                },
                "policy_payload": {
                    "policy_number": f"POL-{i:04d}",
                    "policy_type_id": "your-policy-type-uuid-here",
                    "inception_date": "2025-01-01",
                    "term_type": "1 Year",
                },
                "risk_payloads": [
                    {"property_group_number": 1},
                ],
            }
        )
    return jobs


def example_sync_staged_workflow() -> None:
    """Synchronous staged workflow example using ThreadPoolExecutor.

    Best for:
        - Standalone scripts, cron jobs, Django management commands.
        - Simpler code (no async/await required).

    Performance:
        - 50 jobs × 3 stages × ~5s/call with max_workers=5 → ~50–75 seconds
        - vs. 750s fully sequential (15x speedup).
    """
    from britecore_sdk.api.workflows import create_entities_staged_batch

    print("\n" + "=" * 70)
    print("SYNC STAGED WORKFLOW CREATION")
    print("=" * 70)

    jobs = generate_sample_jobs(5)
    print(f"Processing {len(jobs)} jobs through staged workflow...")

    start = time.time()

    result = create_entities_staged_batch(
        jobs,
        contact_max_workers=5,  # Contacts are fast
        quote_max_workers=5,  # Quotes are fast (skipped if no quote_payload)
        policy_max_workers=3,  # Conservative: policies are heavy
        risk_max_workers=3,  # Conservative: risks depend on revision_id
        fail_fast=False,  # Continue on partial failures
        request_timeout=30,  # 30s per individual API call
    )

    elapsed = time.time() - start

    print(f"\n✓ Completed in {elapsed:.1f}s")
    print(f"  Total:     {result['total']}")
    print(f"  Succeeded: {result['succeeded']}")
    print(f"  Failed:    {result['failed']}")
    print("\nStage breakdown:")
    for stage, totals in result["stage_totals"].items():
        if totals["total"] > 0:
            print(f"  {stage:12s}: {totals['succeeded']}/{totals['total']} succeeded")

    print("\nPer-job results (first 3):")
    for item in result["results"][:3]:
        if item["success"]:
            print(
                f"  [{item['index']}] ✓ contact={item['contact_id']}  "
                f"revision={item['revision_id']}  "
                f"risks={item['risk_ids']}"
            )
        else:
            print(
                f"  [{item['index']}] ✗ failed at '{item['failed_stage']}': "
                f"{item['error']}"
            )


async def example_async_staged_workflow() -> None:
    """Asynchronous staged workflow example using asyncio.

    Best for:
        - FastAPI, aiohttp, or other async web frameworks.
        - When you need fine-grained concurrency control.
        - High-throughput systems with other async I/O happening concurrently.
    """
    from britecore_sdk.api.workflows import acreate_entities_staged_batch

    print("\n" + "=" * 70)
    print("ASYNC STAGED WORKFLOW CREATION")
    print("=" * 70)

    jobs = generate_sample_jobs(5)
    print(f"Processing {len(jobs)} jobs asynchronously...")

    start = time.time()

    result = await acreate_entities_staged_batch(
        jobs,
        contact_max_concurrent=5,
        policy_max_concurrent=3,
        risk_max_concurrent=3,
        fail_fast=False,
        request_timeout=30,
    )

    elapsed = time.time() - start

    print(f"\n✓ Completed in {elapsed:.1f}s")
    print(
        f"  Total: {result['total']}, Succeeded: {result['succeeded']}, "
        f"Failed: {result['failed']}"
    )


def example_chunked_large_batch() -> None:
    """Handle very large batches by chunking.

    For 500+ jobs, chunk into groups to avoid thread pool exhaustion
    and to allow incremental progress tracking.
    """
    from britecore_sdk.api.workflows import create_entities_staged_batch

    print("\n" + "=" * 70)
    print("CHUNKED LARGE BATCH (example only)")
    print("=" * 70)

    all_jobs = generate_sample_jobs(20)  # Pretend this is 500 in production
    chunk_size = 5
    all_results: list[dict[str, Any]] = []

    for chunk_start in range(0, len(all_jobs), chunk_size):
        chunk = all_jobs[chunk_start : chunk_start + chunk_size]
        print(f"  Processing chunk {chunk_start}–{chunk_start + len(chunk) - 1}...")

        chunk_result = create_entities_staged_batch(
            chunk,
            policy_max_workers=3,
            fail_fast=False,
        )
        all_results.extend(chunk_result["results"])
        print(f"    → {chunk_result['succeeded']}/{chunk_result['total']} succeeded")

    total_succeeded = sum(1 for r in all_results if r["success"])
    print(f"\nFinal: {total_succeeded}/{len(all_jobs)} succeeded across all chunks")


if __name__ == "__main__":
    # NOTE: These examples require a configured BriteCore API client.
    # Uncomment the appropriate init line for your environment:
    #
    #   from britecore_sdk.api.api_calls import init_api_client
    #   init_api_client("your-site-name")
    #
    # Or with explicit credentials:
    #   init_api_client(base_url="https://your-instance.britecorenow.com",
    #                   api_key="your-api-key")

    print("Staged Workflow Creation Examples")
    print(
        "(These require a configured BriteCore API client to run against a live server)"
    )

    # Uncomment to run:
    # example_sync_staged_workflow()
    # asyncio.run(example_async_staged_workflow())
    # example_chunked_large_batch()

    print("\nExamples defined. Uncomment calls above to execute against a live server.")
