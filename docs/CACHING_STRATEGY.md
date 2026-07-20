# Response Caching Strategy

This document explains when and how to use response caching in the BriteCore SDK.

## Overview

The SDK includes an optional response caching layer that stores API responses in memory to avoid redundant API calls. Caching can significantly improve performance for read-heavy workloads, but requires careful consideration of data freshness.

## When to Enable Caching

### ✅ Good Use Cases

1. **Read-only operations**
   ```python
   # Perfect for caching - policy data changes infrequently
   from britecore_sdk.api.api_calls import get_async_api_client

   client = get_async_api_client()
   # Cached for 3600 seconds
   policy = await client.aretrieve_policy(policy_number="POL-123", cache_ttl=3600)
   ```

2. **Reference data lookups**
   ```python
   # Cache policy types, rating factors, etc.
   # These rarely change during a session
   result = retrieve_policy_types(cache_ttl=7200)  # 2 hours
   ```

3. **Batch operations with repeated lookups**
   ```python
   # When processing a list of policies, avoid re-fetching the same data
   client = get_api_client()
   client.enable_response_caching(max_size=1000, ttl=300)  # 5 min TTL
   ```

4. **Development and testing**
   ```python
   # Speed up test runs by caching fixture data
   @pytest.fixture
   def mock_policy(monkeypatch):
       result = retrieve_policy(..., cache_ttl=86400)  # Cache for test session
       return result
   ```

### ❌ Poor Use Cases

1. **Mutable operations** - Don't cache write operations
   ```python
   # WRONG - never cache create/update/delete
   result = create_policy(..., cache_ttl=3600)  # ❌ BAD
   ```

2. **Time-sensitive data**
   ```python
   # WRONG - quote availability changes frequently
   quote = create_quote(..., cache_ttl=3600)  # ❌ BAD
   # Use cache_ttl=0 or don't cache at all
   ```

3. **Real-time integrations**
   ```python
   # WRONG - when you need real-time data
   policy = retrieve_policy(..., cache_ttl=3600)  # ❌ BAD
   # Use cache_ttl=0 instead
   ```

4. **Operations with side effects**
   ```python
   # WRONG - operations that update related data
   risk = create_risk(..., cache_ttl=3600)  # ❌ BAD
   ```

## Configuration

### Per-Request Configuration

Cache control on individual requests:

```python
from britecore_sdk.api.api_calls.v2 import policies

# Cache for 1 hour
result = policies.retrieve_policy(
    policy_number="POL-123",
    cache_ttl=3600,
)

# No caching (always fresh)
result = policies.retrieve_policy(
    policy_number="POL-123",
    cache_ttl=0,
)

# Use default TTL from settings
result = policies.retrieve_policy(
    policy_number="POL-123",
    # cache_ttl parameter omitted uses configured default
)
```

### Global Configuration

Configure default caching behavior:

```python
# In settings.toml
[default]
cache_enabled = true
cache_ttl = 300  # 5 minute default
cache_max_size = 1000  # Store up to 1000 responses
```

Or programmatically:

```python
from britecore_sdk.api.api_calls import get_api_client

client = get_api_client()
# Configure caching on async client
from britecore_sdk.api.api_calls import get_async_api_client
async_client = get_async_api_client()
async_client._cache.clear()  # Clear cache
async_client._default_cache_ttl_seconds = 300
```

## Cache Behavior

### Key Generation

Cache keys are based on:
- HTTP method (GET, POST, etc.)
- Request path
- Query parameters
- Request headers (selective)

Two requests with identical parameters will hit the cache:

```python
# First request - hits API
policy1 = policies.retrieve_policy(policy_number="POL-123")

# Second request - returns cached response
policy2 = policies.retrieve_policy(policy_number="POL-123")

# Same data (from cache)
assert policy1 == policy2
```

### Cache Invalidation

Caches are invalidated by:

1. **TTL expiration** - Response expires after configured TTL
   ```python
   result = retrieve_policy(..., cache_ttl=300)  # 5 minute TTL
   # After 5 minutes, this request will hit the API again
   ```

2. **Manual invalidation**
   ```python
   client = get_async_api_client()
   # Clear entire cache
   client.clear_cache()

   # Invalidate specific namespaces
   client.invalidate_cache_namespaces(["policies", "contacts"])
   ```

3. **Cache overflow** - Oldest entries evicted when max_size reached
   ```python
   # If cache holds 1000 responses and you add the 1001st,
   # the oldest entry is evicted
   ```

## Performance Considerations

### Memory Usage

Cached responses consume memory. Monitor and tune:

```python
# Consider memory when setting cache size
async_client._cache.clear()  # Free memory
async_client._default_cache_ttl_seconds = 60  # Shorter TTL = less memory

# Typical memory usage
# - Small response (100 bytes) * 1000 = ~100 KB
# - Large response (10 KB) * 1000 = ~10 MB
```

### TTL Tuning

Balance freshness vs. performance:

```python
# Reference data - can use longer TTL
reference_ttl = 3600  # 1 hour

# Frequently changing data - shorter TTL
dynamic_ttl = 60  # 1 minute

# Time-sensitive operations - no cache
real_time_ttl = 0  # No caching
```

## Caching Strategies

### Strategy 1: Read-Through Cache

Cache reads transparently:

```python
from britecore_sdk.api.api_calls import get_async_api_client
from britecore_sdk.api.response_helpers import paginate

async def list_all_contacts(page_size=100):
    """List contacts with caching."""
    client = get_async_api_client()

    # Each page is cached independently
    for contact in paginate(
        client.get_client(),
        contact.list_contacts,
        page_size=page_size,
        cache_ttl=300,
    ):
        yield contact
```

### Strategy 2: Write-Through Cache

Clear cache after writes:

```python
from britecore_sdk.api.api_calls.v2 import policies

async def update_policy(policy_id, updates):
    """Update policy and clear cache."""
    client = get_async_api_client()

    # Make write request (don't cache)
    result = await policies.update_policy(
        policy_id=policy_id,
        **updates,
        cache_ttl=0,  # Don't cache writes
    )

    # Invalidate related cache entries
    client.invalidate_cache_namespaces(["policies"])

    return result
```

### Strategy 3: Time-Based Invalidation

Refresh cache periodically:

```python
import asyncio
from britecore_sdk.api.api_calls import get_async_api_client

async def periodic_refresh(interval_seconds=3600):
    """Periodically clear cache to refresh data."""
    client = get_async_api_client()

    while True:
        await asyncio.sleep(interval_seconds)
        client.clear_cache()
        print("Cache cleared and will refresh")
```

### Strategy 4: Selective Caching

Cache only what's needed:

```python
from britecore_sdk.api.api_calls.v2 import policies

# Cache lookups - high hit rate
policy = policies.retrieve_policy(
    policy_number="POL-123",
    cache_ttl=3600,
)

# Don't cache writes
new_policy = policies.create_policy(
    **policy_data,
    cache_ttl=0,
)

# Minimal cache for mutable operations
updated = policies.update_policy(
    policy_id=policy["id"],
    **updates,
    cache_ttl=60,  # Short TTL in case of immediate refresh
)
```

## Troubleshooting

### "Getting stale data from cache"

**Solution:** Adjust TTL or clear cache after writes

```python
# Option 1: Use shorter TTL
result = retrieve_policy(..., cache_ttl=60)  # 1 minute instead of 1 hour

# Option 2: Clear cache after writes
client = get_async_api_client()
await policies.update_policy(...)
client.invalidate_cache_namespaces(["policies"])
```

### "Cache consuming too much memory"

**Solution:** Reduce cache size or TTL

```python
client = get_async_api_client()

# Reduce TTL
client._default_cache_ttl_seconds = 60  # 1 minute instead of 5

# Or use smaller cache
# Recreate client with smaller max_size
```

### "Cache hits are low"

**Solution:** Review access patterns and adjust configuration

```python
# If you're querying different records often:
# - Longer TTL may not help
# - Consider filtering or pagination strategies

# If you're querying same records:
# - Increase TTL and cache size
# - Monitor for memory impact
```

## Best Practices

1. **Default to no caching** - Enable only where proven beneficial
2. **Monitor performance** - Use timing middleware to measure impact
3. **Test cache behavior** - Verify invalidation works as expected
4. **Document TTL choices** - Explain why specific TTLs are used
5. **Use selective caching** - Different TTLs for different operations
6. **Plan invalidation** - Design invalidation strategy upfront
7. **Watch memory** - Monitor cache growth over time
8. **Log cache operations** - Enable debug logging to diagnose issues

## See Also

- [Request Timing Middleware](../timing_middleware.py)
- [Common Patterns](COMMON_PATTERNS.md)
- [Configuration Guide](./CONFIGURATION.md)
- [Performance Optimization](./OBSERVABILITY.md)
