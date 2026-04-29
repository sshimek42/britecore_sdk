"""Example: Batch Quote Creation for High-Volume Workflows.

This example demonstrates how to efficiently create 100+ quotes using the
BriteCore SDK's batching features. Both synchronous (ThreadPoolExecutor) and
asynchronous (asyncio) approaches are shown.

Use Case:
    A nightly automation task needs to create 150 quotes in under 5 minutes
    without timing out. With sequential calls at 5-10 seconds each, this would
    take 12-25 minutes. Using batch creation with concurrency reduces time to
    ~2-3 minutes.

Approaches:
    1. Synchronous batch with ThreadPoolExecutor (simpler, good for scripts)
    2. Asynchronous batch with asyncio (best for web services, more control)
    3. Chunking very large batches (e.g., 1000+) to avoid resource exhaustion
"""

import asyncio
import time
from typing import Any

from britecore_sdk.api.api_calls.v2.async_quotes import acreate_full_quotes_batch
from britecore_sdk.api.api_calls.v2.quotes import create_full_quotes_batch


def generate_sample_quotes(count: int) -> list[dict[str, Any]]:
    """Generate synthetic quote payloads for testing.

    In a real scenario, these would be loaded from your database or CSV.
    """
    return [
        {
            "number": f"BATCH-{i:06d}",
            "policy_type_id": "HomeownersPolicy",
            "insured": {
                "first_name": f"Customer{i}",
                "last_name": "Test",
                "email": f"customer{i}@example.com",
            },
            "property": {
                "address": {
                    "street": "123 Main St",
                    "city": "Anytown",
                    "state": "NY",
                    "zip": "12345",
                    "country": "US",
                },
            },
            "line": {
                "coverage_limit": 250000,
                "deductible": 1000,
            },
        }
        for i in range(1, count + 1)
    ]


def example_sync_batch_creation():
    """Synchronous batch creation example.

    Best for:
        - Standalone scripts or CLI tools
        - When you want simpler code (no async/await)
        - Predictable worker pool management

    Performance:
        - 100 quotes with max_workers=5 → ~20-50 seconds (5×-10× faster than serial)
        - Thread-safe; safe to use from Django/Flask views
    """
    print("\n" + "=" * 70)
    print("SYNC BATCH QUOTE CREATION (ThreadPoolExecutor)")
    print("=" * 70)

    quotes = generate_sample_quotes(10)  # Use 100 in production
    print(f"Creating {len(quotes)} quotes...")

    start_time = time.time()

    result = create_full_quotes_batch(
        quotes,
        max_workers=5,
        fail_fast=False,  # Continue on errors; useful for partial success
    )

    elapsed = time.time() - start_time

    print(f"\n✓ Completed in {elapsed:.1f}s")
    print(f"  Total:    {result['total']}")
    print(f"  Succeeded: {result['succeeded']}")
    print(f"  Failed:    {result['failed']}")

    if result["failed"] > 0:
        print("\nFailed quotes:")
        for item in result["results"]:
            if not item["success"]:
                print(f"  Index {item['index']}: {item['error']}")

    # Optional: save successful quote IDs
    success_ids = [item["quote_id"] for item in result["results"] if item["success"]]
    print(f"\nSuccessfully created quote IDs: {success_ids[:5]}...")


async def example_async_batch_creation():
    """Asynchronous batch creation example.

    Best for:
        - Web services / async request handlers (FastAPI, aiohttp)
        - When you need fine-grained concurrency control
        - High-throughput systems with caching

    Performance:
        - 100 quotes with max_concurrent=5 → ~20-50 seconds
        - Runs coroutines concurrently; more efficient than threads for I/O
        - Integrates seamlessly with asyncio event loop
    """
    print("\n" + "=" * 70)
    print("ASYNC BATCH QUOTE CREATION (asyncio)")
    print("=" * 70)

    quotes = generate_sample_quotes(10)  # Use 100 in production
    print(f"Creating {len(quotes)} quotes concurrently...")

    start_time = time.time()

    result = await acreate_full_quotes_batch(
        quotes,
        max_concurrent=5,
        fail_fast=False,
    )

    elapsed = time.time() - start_time

    print(f"\n✓ Completed in {elapsed:.1f}s")
    print(f"  Total:     {result['total']}")
    print(f"  Succeeded: {result['succeeded']}")
    print(f"  Failed:    {result['failed']}")

    if result["failed"] > 0:
        print("\nFailed quotes:")
        for item in result["results"]:
            if not item["success"]:
                print(f"  Index {item['index']}: {item['error']}")

    # Optional: save successful quote IDs
    success_ids = [item["quote_id"] for item in result["results"] if item["success"]]
    print(f"\nSuccessfully created quote IDs: {success_ids[:5]}...")


def example_chunked_batch_for_very_large_volumes():
    """Handle very large batches (1000+) by chunking to avoid resource exhaustion.

    For extremely large volumes, split into chunks to:
        - Control memory usage (don't load all 1000 responses at once)
        - Distribute API load (avoid spike)
        - Enable progress tracking per chunk
        - Survive partial network failures (retry failed chunks)
    """
    print("\n" + "=" * 70)
    print("CHUNKED BATCH CREATION (for 1000+ quotes)")
    print("=" * 70)

    quotes = generate_sample_quotes(100)  # Pretend this is 1000
    chunk_size = 50
    chunks = [quotes[i : i + chunk_size] for i in range(0, len(quotes), chunk_size)]

    print(f"Creating {len(quotes)} quotes in {len(chunks)} chunks of {chunk_size}...\n")

    all_results = []
    total_succeeded = 0
    total_failed = 0

    for chunk_idx, chunk in enumerate(chunks, 1):
        print(f"[Chunk {chunk_idx}/{len(chunks)}] Processing {len(chunk)} quotes...")

        start = time.time()
        result = create_full_quotes_batch(chunk, max_workers=5, fail_fast=False)
        elapsed = time.time() - start

        all_results.extend(result["results"])
        total_succeeded += result["succeeded"]
        total_failed += result["failed"]

        print(f"  ✓ {result['succeeded']} success, {result['failed']} failed ({elapsed:.1f}s)")

    print(f"\n✓ All chunks complete!")
    print(f"  Total succeeded: {total_succeeded}")
    print(f"  Total failed:    {total_failed}")


async def example_async_chunked_with_progress():
    """Async chunked creation with progress callback.

    Demonstrates how to track progress across multiple chunks.
    """
    print("\n" + "=" * 70)
    print("ASYNC CHUNKED WITH PROGRESS TRACKING")
    print("=" * 70)

    quotes = generate_sample_quotes(100)
    chunk_size = 25
    chunks = [quotes[i : i + chunk_size] for i in range(0, len(quotes), chunk_size)]

    print(f"Creating {len(quotes)} quotes async, {len(chunks)} chunks...\n")

    all_succeeded = 0
    all_failed = 0

    for chunk_idx, chunk in enumerate(chunks, 1):
        print(f"[Chunk {chunk_idx}/{len(chunks)}] Starting {len(chunk)} concurrent creates...")

        result = await acreate_full_quotes_batch(
            chunk, max_concurrent=3, fail_fast=False
        )

        all_succeeded += result["succeeded"]
        all_failed += result["failed"]

        success_rate = (
            100 * result["succeeded"] / result["total"] if result["total"] > 0 else 0
        )
        print(f"  ✓ {result['succeeded']}/{result['total']} ({success_rate:.0f}% success)")

    print(f"\n✓ All chunks complete!")
    print(f"  Total succeeded: {all_succeeded}")
    print(f"  Total failed:    {all_failed}")


def example_error_handling():
    """Demonstrate error handling strategies.

    Options:
        1. fail_fast=True: Stop on first error (atomicity)
        2. fail_fast=False: Collect all errors (partial success acceptable)
    """
    print("\n" + "=" * 70)
    print("ERROR HANDLING EXAMPLES")
    print("=" * 70)

    quotes = generate_sample_quotes(5)
    # Introduce an invalid payload
    quotes[2] = {"incomplete": "payload"}

    print("Scenario 1: fail_fast=False (collect all errors)")
    print("-" * 70)
    result = create_full_quotes_batch(quotes, max_workers=2, fail_fast=False)
    print(f"Result: {result['succeeded']} succeeded, {result['failed']} failed\n")

    print("Scenario 2: fail_fast=True (stop on first error)")
    print("-" * 70)
    try:
        result = create_full_quotes_batch(quotes, max_workers=2, fail_fast=True)
    except Exception as e:
        print(f"Batch stopped due to error: {type(e).__name__}: {e}\n")


async def main():
    """Run all examples."""
    # Sync examples
    example_sync_batch_creation()
    example_chunked_batch_for_very_large_volumes()
    example_error_handling()

    # Async examples
    await example_async_batch_creation()
    await example_async_chunked_with_progress()


if __name__ == "__main__":
    # Uncomment the example you want to run:

    # Sync examples (run these first)
    # example_sync_batch_creation()
    # example_chunked_batch_for_very_large_volumes()
    # example_error_handling()

    # Async examples (require asyncio)
    print("Run with: python -m asyncio batch_quote_creation.py")
    asyncio.run(main())

