# Common BriteCore API Patterns

*Last updated: September 2, 2026*
*Document type: Implementation guide*

This guide demonstrates common patterns and recipes for using the BriteCore SDK effectively.

> Migration note: Patterns that rely on implicit module-level client state remain supported,
> but new code should prefer explicit `client=` passing or scoped `use_api_client(...)`
> to align with the deprecation path toward `v3.0.0`.

## Pattern 1: Policy Lookup with Fallback

Sometimes you need to find a policy but aren't sure whether you have the policy number or ID. This pattern tries both:

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies
from britecore_sdk.exceptions import NotFoundError

def find_policy(policy_number=None, policy_id=None):
    """Find a policy by number or ID, trying both if available."""
    client = get_api_client()

    # Try by policy number first (more common)
    if policy_number:
        try:
            return policies.retrieve_policy(policy_number=policy_number, client=client)
        except NotFoundError:
            pass

    # Try by policy ID
    if policy_id:
        try:
            return policies.retrieve_policy(policy_id=policy_id, client=client)
        except NotFoundError:
            pass

    raise ValueError("Could not find policy with provided identifiers")
```

## Pattern 2: Batch Contact Import with Validation

Import multiple contacts efficiently with error handling:

```python
from britecore_sdk.models import BritecoreContact
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import contacts
from britecore_sdk.exceptions import ValidationError, BritecoreError

def import_contacts_bulk(contact_list):
    """Import a list of contact dictionaries with validation."""
    client = get_api_client()
    results = {
        "total": len(contact_list),
        "succeeded": 0,
        "failed": 0,
        "errors": [],
    }

    for idx, contact_data in enumerate(contact_list):
        try:
            # Validate the contact
            contact = BritecoreContact(**contact_data)
            validated = contact.process_contact()

            # Create the contact
            result = contacts.new_contact(contact=validated, client=client)
            results["succeeded"] += 1

        except ValidationError as e:
            results["failed"] += 1
            results["errors"].append({
                "index": idx,
                "data": contact_data,
                "error": f"Validation error: {e}",
            })
        except BritecoreError.Base as e:
            results["failed"] += 1
            results["errors"].append({
                "index": idx,
                "data": contact_data,
                "error": f"API error: {e}",
            })

    return results
```

## Pattern 3: Rate Limit Aware Loops

Handle rate limiting gracefully when processing many items:

```python
import time
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies
from britecore_sdk.exceptions import RateLimitError
from britecore_sdk.api.rate_limiter import RateLimiter

def process_policies_with_rate_limiting(policy_numbers, delay_ms=100):
    """Process policies with built-in rate limiting."""
    client = get_api_client()
    rate_limiter = RateLimiter(
        requests_per_second=10,  # Adjust to API limits
        burst_size=5,
    )

    results = []
    for policy_num in policy_numbers:
        # Check rate limit before making request
        rate_limiter.acquire()

        try:
            policy = policies.retrieve_policy(policy_number=policy_num, client=client)
            results.append(policy)

        except RateLimitError:
            # Exponential backoff on rate limit
            wait_time = 1
            while True:
                time.sleep(wait_time)
                try:
                    policy = policies.retrieve_policy(policy_number=policy_num, client=client)
                    results.append(policy)
                    break
                except RateLimitError:
                    wait_time *= 2
                    if wait_time > 60:
                        raise  # Give up after 60 seconds

    return results
```

## Pattern 3b: Dry-Run Request Preview

Preview request payloads and headers without sending traffic:

```python
from britecore_sdk.api.api_calls.v2 import policies

def preview_policy_lookup(policy_number):
    """Preview a request with RequestParameters dry_run=True."""
    from britecore_sdk.api.api_calls import get_api_client

    client = get_api_client()
    preview = policies.retrieve_policy(
        policy_number=policy_number,
        client=client,
        dry_run=True,
    )
    return {
        "request_id": preview.get("request_id"),
        "url": preview.get("url"),
        "method": preview.get("method"),
        "dry_run": preview.get("dry_run"),
    }
```

## Pattern 4: Pagination Through Large Result Sets

Efficiently iterate through paginated results:

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import contacts
from britecore_sdk.api.response_helpers import paginate

def process_all_contacts(batch_size=100):
    """Process all contacts in the system."""
    client = get_api_client()

    # Use paginate helper to automatically handle pagination
    for contact in paginate(
        client,
        contacts.list_contacts,
        page_size=batch_size,
        max_pages=None,  # No limit
    ):
        # Process each contact
        print(f"Processing contact: {contact.get('name')}")
        yield contact
```

## Pattern 5: Batch Operations with Progress Tracking

Track progress when performing bulk operations:

```python
from britecore_sdk.api.api_calls.v2 import policies
from britecore_sdk.exceptions import BritecoreError

def create_policies_with_tracking(policy_list, show_progress=True):
    """Create multiple policies with progress tracking."""
    from britecore_sdk.api.api_calls import get_api_client

    client = get_api_client()
    total = len(policy_list)
    results = []

    for idx, policy_data in enumerate(policy_list, 1):
        try:
            result = policies.create_policy(client=client, **policy_data)
            results.append(result)

            if show_progress:
                percentage = (idx / total) * 100
                print(f"Progress: {idx}/{total} ({percentage:.1f}%)")

        except BritecoreError.Base as e:
            print(f"Error creating policy {idx}: {e}")
            results.append({"error": str(e)})

    return results
```

## Pattern 6: Conditional Policy Updates

Update policies only when specific conditions are met:

```python
from britecore_sdk.api.api_calls.v2 import policies
from britecore_sdk.exceptions import BritecoreError

def update_expired_policies(policy_list, new_expiration_date):
    """Update expiration date for policies that match criteria."""
    from britecore_sdk.api.api_calls import get_api_client

    client = get_api_client()
    updated = []
    skipped = []

    for policy in policy_list:
        current_expiration = policy.get("expiration_date")

        # Only update if expiration is before new date
        if current_expiration and current_expiration < new_expiration_date:
            try:
                result = policies.update_policy(
                    policy_id=policy["policy_id"],
                    expiration_date=new_expiration_date,
                    client=client,
                )
                updated.append(result)
            except BritecoreError.Base as e:
                print(f"Failed to update policy {policy['policy_id']}: {e}")
        else:
            skipped.append(policy["policy_id"])

    return {"updated": updated, "skipped": skipped}
```

## Pattern 7: Error Recovery with Retry

Implement retry logic for transient failures:

```python
import time
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import quotes
from britecore_sdk.exceptions import BritecoreError, RequestTimeoutError

def create_quote_with_retry(quote_data, max_retries=3, backoff_factor=2):
    """Create a quote with automatic retry on failure."""
    client = get_api_client()
    last_error = None

    for attempt in range(max_retries):
        try:
            quote = quotes.create_quote(client=client, **quote_data)
            if attempt > 0:
                print(f"Quote created on retry {attempt + 1}")
            return quote

        except RequestTimeoutError as e:
            last_error = e
            wait_time = backoff_factor ** attempt
            print(f"Timeout on attempt {attempt + 1}, waiting {wait_time}s before retry...")
            time.sleep(wait_time)

        except BritecoreError.Base as e:
            # Don't retry on validation or auth errors
            if "Validation" in str(type(e)) or "Authentication" in str(type(e)):
                raise
            last_error = e
            wait_time = backoff_factor ** attempt
            print(f"Error on attempt {attempt + 1}, waiting {wait_time}s before retry...")
            time.sleep(wait_time)

    if last_error is not None:
        raise last_error
    raise RuntimeError("Failed after retries")
```

## Pattern 8: Extract and Transform Responses

Transform API responses into usable formats:

```python
from britecore_sdk.api.api_calls.v2 import policies
from britecore_sdk.api.response_helpers import extract_data, transform_response
from britecore_sdk.api.api_calls import get_api_client

client = get_api_client()

def get_policy_summary(policy_number):
    """Get a simplified policy summary."""
    response = policies.retrieve_policy(policy_number=policy_number, client=client)

    # Extract just the data
    data = extract_data(response)

    # Transform into summary format
    return {
        "policy_number": data["policy_number"],
        "status": data["status"],
        "premium": data["premium"],
        "effective_date": data["inception_date"],
    }

def get_policy_ids(policy_numbers):
    """Get policy IDs for a list of policy numbers."""
    return [
        transform_response(
            policies.retrieve_policy(policy_number=pn, client=client),
            lambda d: d.get("policy_id"),
        )
        for pn in policy_numbers
    ]
```

## Pattern 9: Async Bulk Operations

Process multiple operations concurrently:

```python
import asyncio
from britecore_sdk.api.api_calls import get_async_api_client, init_async_api_client
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy

async def fetch_policies_concurrently(policy_numbers, max_concurrent=5):
    """Fetch multiple policies concurrently."""
    init_async_api_client("your_site")
    client = get_async_api_client()
    semaphore = asyncio.Semaphore(max_concurrent)

    async def fetch_one(policy_number):
        async with semaphore:
            return await aretrieve_policy(policy_number=policy_number, client=client)

    tasks = [fetch_one(pn) for pn in policy_numbers]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Separate successful results from errors
    policies = []
    errors = []
    for result in results:
        if isinstance(result, Exception):
            errors.append(result)
        else:
            policies.append(result)

    return policies, errors
```

## Pattern 10: Context-Based Configuration

Use different credentials for different environments:

```python
from britecore_sdk.api.api_calls import init_api_client, use_api_client
from contextlib import contextmanager

@contextmanager
def api_context(environment):
    """Context manager for working with a specific environment."""
    client = init_api_client(target_site=environment)
    with use_api_client(client):
        yield client

# Usage:
with api_context("production") as client:
    from britecore_sdk.api.api_calls.v2 import policies
    prod_policy = policies.retrieve_policy(policy_number="PROD-001", client=client)

# Automatically switched back to previous client or None after block
```

## Tips and Best Practices

- **Use response helpers**: The `britecore_sdk.api.response_helpers` module provides utilities for pagination, batching, and data extraction
- **Handle rate limiting**: Check rate limit status before making bulk requests
- **Use context managers**: The `use_api_client()` context manager safely manages client switching
- **Validate input**: Use `BritecoreContact` and `BritecorePolicy` validators before creating/updating
- **Log operations**: Enable SDK logging to debug issues: `from britecore_sdk import configure_logging; configure_logging()`
- **Use dry-run for validation**: Pass `dry_run=True` to wrappers to inspect outbound requests without network calls
- **Test error paths**: Most patterns above include error handling; test these paths in your application
- **Use async for I/O**: For high-volume operations, consider using async functions to maximize throughput

## See Also

- [API Reference](./api_reference.rst)
- [Configuration Guide](./CONFIGURATION.md)
- [Error Handling](../TROUBLESHOOTING.md)
