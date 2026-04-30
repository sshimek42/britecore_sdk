"""Example: Stitched Line File Extract for Multiple Lines.

This example demonstrates how to retrieve export data for multiple BriteCore
lines (LOBs) and stitch the results together into a single structured response.
Both synchronous and asynchronous approaches are shown.

Use Case:
    An administrator needs to export configuration data for 5 lines of business
    (e.g., Auto, Home, Commercial, Farm, and Umbrella). Each extract call takes
    45–60 seconds. Sequential extraction would take 225–300 seconds. With
    max_workers=2, total time drops to ~150–180 seconds.

⚠️  IMPORTANT: Always pass ``request_timeout`` >= 90 seconds.
    The SDK default (5s) is far too short for line file extracts.

Run:
    python examples/stitched_line_extract.py
"""

import time
from typing import Any

# ---------------------------------------------------------------------------
# Helper to discover line tuples (in a real workflow you'd use these helpers)
# ---------------------------------------------------------------------------


def get_line_tuples_example() -> list[tuple]:
    """Show how to discover (effective_date_id, state_id, line_id) tuples.

    In a real workflow, use the helpers to discover available lines:
    """
    # from britecore_sdk.api.api_calls.v2 import lines
    #
    # # 1. Get effective dates
    # eff_dates = lines.get_all_effective_dates()
    # eff_date_id = eff_dates[0]["id"]
    #
    # # 2. Get states for the effective date
    # states = lines.get_all_states(effective_date_id=eff_date_id)
    # state_id = states[0]["id"]
    #
    # # 3. Get available lines
    # available_lines = lines.get_all_lines(effective_date_id=eff_date_id)
    # line_id = available_lines[0]["id"]
    #
    # line_tuples = [
    #     (eff_date_id, state_id, line["id"]) for line in available_lines
    # ]

    # Placeholder for demonstration:
    return [
        ("eff-uuid-1", "state-uuid-1", "line-uuid-1"),
        ("eff-uuid-2", "state-uuid-2", "line-uuid-2"),
        ("eff-uuid-3", "state-uuid-3", "line-uuid-3"),
    ]


# ---------------------------------------------------------------------------
# Synchronous stitched extract
# ---------------------------------------------------------------------------


def example_sync_stitched_extract() -> None:
    """Synchronous stitched line file extract.

    Best for:
        - Standalone scripts, cron jobs.
        - When you need simple, predictable execution.

    ⚠️  request_timeout is REQUIRED — default 5s will time out on every call.
    """
    from britecore_sdk.api.api_calls.v2.lines import get_export_line_files_stitched

    print("\n" + "=" * 70)
    print("SYNC STITCHED LINE FILE EXTRACT")
    print("=" * 70)

    line_tuples = get_line_tuples_example()
    print(f"Extracting {len(line_tuples)} lines (max_workers=2, timeout=120s)...")

    start = time.time()

    result = get_export_line_files_stitched(
        line_tuples,
        max_workers=2,  # Low concurrency — these calls are slow
        include_custom_sequences=False,
        request_timeout=120,  # ← REQUIRED: at least 90s, ideally 120–180s
    )

    elapsed = time.time() - start

    print(f"\n✓ Completed in {elapsed:.1f}s")
    print(f"  Total:     {result['total']}")
    print(f"  Succeeded: {result['succeeded']}")
    print(f"  Failed:    {result['failed']}")

    # Process succeeded extracts
    for item in result["results"]:
        if item["success"]:
            data = item["data"]
            line = item["line"]
            print(f"\n  Line {line[2]}:")
            print(f"    Keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}")
        else:
            print(f"\n  ✗ Line {item['line'][2]} FAILED: {item['error']}")

    return result


# ---------------------------------------------------------------------------
# Asynchronous stitched extract
# ---------------------------------------------------------------------------


async def example_async_stitched_extract() -> None:
    """Asynchronous stitched line file extract.

    Best for:
        - FastAPI, aiohttp or other async frameworks.
        - When you're already in an async context.
    """
    from britecore_sdk.api.api_calls.v2.async_lines import (
        aget_export_line_files_stitched,
    )

    print("\n" + "=" * 70)
    print("ASYNC STITCHED LINE FILE EXTRACT")
    print("=" * 70)

    line_tuples = get_line_tuples_example()
    print(f"Extracting {len(line_tuples)} lines asynchronously...")

    start = time.time()

    result = await aget_export_line_files_stitched(
        line_tuples,
        max_concurrent=2,  # Low concurrency
        include_custom_sequences=False,
        request_timeout=120,  # ← REQUIRED
    )

    elapsed = time.time() - start

    print(f"\n✓ Completed in {elapsed:.1f}s")
    print(
        f"  Total: {result['total']}, "
        f"Succeeded: {result['succeeded']}, "
        f"Failed: {result['failed']}"
    )


# ---------------------------------------------------------------------------
# Retry pattern for failed extracts
# ---------------------------------------------------------------------------


def example_retry_failed_lines(initial_result: dict[str, Any]) -> None:
    """Retry only the lines that failed in a previous extract run.

    A common pattern: run the full extract, then retry only the failures
    with a longer timeout.
    """
    from britecore_sdk.api.api_calls.v2.lines import get_export_line_files_stitched

    failed_lines = [
        item["line"] for item in initial_result["results"] if not item["success"]
    ]

    if not failed_lines:
        print("No failures to retry.")
        return

    print(f"\nRetrying {len(failed_lines)} failed line(s) with extended timeout...")

    retry_result = get_export_line_files_stitched(
        failed_lines,
        max_workers=1,  # One at a time for retries
        request_timeout=180,  # Even longer timeout for retries
    )

    print(
        f"Retry result: {retry_result['succeeded']}/{retry_result['total']} succeeded"
    )


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

    print("Stitched Line File Extract Examples")
    print(
        "(These require a configured BriteCore API client to run against a live server)"
    )
    print()
    print("⚠️  REMINDER: Always pass request_timeout >= 90 for line file extracts")

    # Uncomment to run:
    # sync_result = example_sync_stitched_extract()
    # example_retry_failed_lines(sync_result)
    # asyncio.run(example_async_stitched_extract())

    print("\nExamples defined. Uncomment calls above to execute against a live server.")
