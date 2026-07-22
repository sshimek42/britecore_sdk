"""
Example: Async Operations and Batch Processing

This example demonstrates:
- Async/await for non-blocking operations
- Concurrent batch processing
- Semaphore-based concurrency control
- Async error handling
"""

import asyncio
import logging
from typing import Any

from britecore_sdk.api.api_calls import init_async_api_client
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy
from britecore_sdk.api.api_calls.v2.async_quotes import acreate_quote
from britecore_sdk.exceptions import BritecoreError, NotFoundError

logger = logging.getLogger(__name__)


async def fetch_policies_concurrent(
    policy_ids: list[str], max_concurrent: int = 5
) -> dict[str, Any]:
    """
    Fetch multiple policies concurrently with controlled concurrency.

    Uses a semaphore to limit concurrent requests to avoid overwhelming
    the server.
    """
    init_async_api_client("production")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_with_limit(policy_id: str):
        async with semaphore:
            try:
                return {
                    "policy_id": policy_id,
                    "status": "success",
                    "data": await aretrieve_policy(policy_id=policy_id),
                }
            except NotFoundError:
                return {
                    "policy_id": policy_id,
                    "status": "not_found",
                    "error": f"Policy {policy_id} not found",
                }
            except BritecoreError.Base as e:
                return {"policy_id": policy_id, "status": "error", "error": str(e)}

    # Create tasks for all policies
    tasks = [fetch_with_limit(pid) for pid in policy_ids]

    # Run concurrently
    print(
        f"Fetching {len(policy_ids)} policies with max {max_concurrent} concurrent..."
    )
    results = await asyncio.gather(*tasks)

    # Organize results
    return {
        "succeeded": [r for r in results if r["status"] == "success"],
        "not_found": [r for r in results if r["status"] == "not_found"],
        "errors": [r for r in results if r["status"] == "error"],
        "total": len(policy_ids),
    }


async def create_quotes_batch(
    quote_data_list: list[dict[str, Any]],
    max_concurrent: int = 5,
    delay_between_requests: float = 0.1,
) -> dict[str, Any]:
    """
    Create multiple quotes concurrently with rate limiting.

    Includes:
    - Concurrency control via semaphore
    - Delay between requests for rate limiting
    - Error collection
    """
    init_async_api_client("production")

    semaphore = asyncio.Semaphore(max_concurrent)

    async def create_with_limit(idx: int, quote_data: dict[str, Any]):
        async with semaphore:
            # Add delay for rate limiting
            await asyncio.sleep(delay_between_requests * idx)

            try:
                result = await acreate_quote(**quote_data)
                return {
                    "index": idx,
                    "status": "success",
                    "quote_id": result.get("data", {}).get("quote_id"),
                    "insured": quote_data.get("insured_name"),
                }
            except BritecoreError.Base as e:
                return {
                    "index": idx,
                    "status": "error",
                    "error": str(e),
                    "insured": quote_data.get("insured_name"),
                }

    # Create tasks
    tasks = [create_with_limit(idx, data) for idx, data in enumerate(quote_data_list)]

    # Run concurrently
    print(
        f"Creating {len(quote_data_list)} quotes with max {max_concurrent} concurrent..."
    )
    results = await asyncio.gather(*tasks)

    # Organize results
    return {
        "succeeded": [r for r in results if r["status"] == "success"],
        "failed": [r for r in results if r["status"] == "error"],
        "total": len(quote_data_list),
    }


async def orchestrate_complex_workflow() -> None:
    """
    Example of orchestrating multiple async operations.

    Demonstrates:
    - Running multiple async functions
    - Error handling in async context
    - Structured results collection
    """
    print("Complex Async Workflow Example\n" + "=" * 50)

    # Prepare data
    policy_ids = [f"POL-{i:06d}" for i in range(1, 21)]  # 20 policies
    quotes_data = [
        {"insured_name": f"Business {i}", "policy_type": "Commercial"}
        for i in range(1, 11)  # 10 quotes
    ]

    try:
        # Run multiple async operations
        print("\nPhase 1: Fetching policies...")
        policy_results = await fetch_policies_concurrent(policy_ids, max_concurrent=5)
        print(f"  Fetched: {len(policy_results['succeeded'])} policies")
        print(f"  Not found: {len(policy_results['not_found'])}")
        print(f"  Errors: {len(policy_results['errors'])}")

        print("\nPhase 2: Creating quotes...")
        quote_results = await create_quotes_batch(quotes_data, max_concurrent=3)
        print(f"  Created: {len(quote_results['succeeded'])} quotes")
        print(f"  Failed: {len(quote_results['failed'])}")

        # Summary
        print("\n" + "=" * 50)
        print("Workflow Summary:")
        print(f"  Policies processed: {policy_results['total']}")
        print(f"  Quotes created: {quote_results['total']}")

    except Exception as e:
        logger.error(f"Workflow failed: {e}", exc_info=True)


async def main():
    """Main async entry point."""
    logging.basicConfig(level=logging.INFO)
    await orchestrate_complex_workflow()


if __name__ == "__main__":
    # Run async example
    asyncio.run(main())
