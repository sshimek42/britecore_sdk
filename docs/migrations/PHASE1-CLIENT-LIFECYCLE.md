# Phase 1: Client Lifecycle Migration Guide (v2.0.0)

*Last updated: July 16, 2026*
*Document type: Migration guide*

## Overview

**v2.0.0 introduces an explicit client parameter to all endpoint wrappers**, moving away from the implicit module-global client pattern used in v1.x. This change improves:

- **Testability** — No hidden global state
- **Multi-tenancy** — Easy to manage multiple clients with different credentials
- **Type safety** — Explicit dependencies are clearer to IDEs and type checkers
- **Parallelism** — Safe concurrent requests without race conditions

---

## Quick Reference

| Pattern | v1.x (deprecated in v2.0.0) | v2.0.0 (recommended) |
|---------|-----|-----|
| **Setup** | `init_api_client(target_site="site")` | `client = BritecoreAPIClient("site").init_client()` |
| **Use** | `retrieve_quote(quote_id="Q123")` | `retrieve_quote(quote_id="Q123", client=client)` |
| **Cleanup** | (implicit, pooled) | `client.close()` or use context manager |
| **Multi-site** | `use_api_client(client_b)` context | Multiple explicit client instances |

---

## Migration Patterns

### Pattern 1: Simple One-Site Script

#### Before (v1.x)
```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import quotes, policies

# Initialize implicit global client
init_api_client(target_site="production")

# Use endpoint wrappers without passing client
quote = quotes.retrieve_quote(quote_number="Q123")
policy = policies.retrieve_policy(policy_number="P456")

print(f"Quote: {quote['premium']}")
print(f"Policy: {policy['status']}")
```

#### After (v2.0.0)
```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes, policies

# Create and initialize explicit client
client = BritecoreAPIClient("production").init_client()

# Pass client to endpoint wrappers
quote = quotes.retrieve_quote(quote_number="Q123", client=client)
policy = policies.retrieve_policy(policy_number="P456", client=client)

print(f"Quote: {quote['premium']}")
print(f"Policy: {policy['status']}")

# Cleanup (automatic with context manager - recommended)
client.close()
```

**Or with context manager (recommended):**

```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes, policies

# Use context manager for automatic cleanup
with BritecoreAPIClient("production").init_client() as client:
    quote = quotes.retrieve_quote(quote_number="Q123", client=client)
    policy = policies.retrieve_policy(policy_number="P456", client=client)
    
    print(f"Quote: {quote['premium']}")
    print(f"Policy: {policy['status']}")
# Cleanup happens automatically on context exit
```

---

### Pattern 2: Multi-Site or Multi-Environment

#### Before (v1.x)
```python
from britecore_sdk.api.api_calls import (
    init_api_client,
    reset_api_client,
    use_api_client,
)
from britecore_sdk.api.api_calls.v2 import quotes

# Approach A: reset_api_client (clears state)
client_prod = init_api_client(target_site="production")
quote_prod = quotes.retrieve_quote(quote_number="Q123")

reset_api_client()

client_staging = init_api_client(target_site="staging")
quote_staging = quotes.retrieve_quote(quote_number="Q123")

# Approach B: use_api_client context manager (cleaner)
client_prod = init_api_client(target_site="production")
quote_prod = quotes.retrieve_quote(quote_number="Q123")

client_staging = init_api_client(target_site="staging")
with use_api_client(client_staging):
    quote_staging = quotes.retrieve_quote(quote_number="Q123")
```

#### After (v2.0.0)
```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes

# Multiple explicit clients - no hidden state
client_prod = BritecoreAPIClient("production").init_client()
client_staging = BritecoreAPIClient("staging").init_client()

# Concurrent requests to different sites
quote_prod = quotes.retrieve_quote(quote_number="Q123", client=client_prod)
quote_staging = quotes.retrieve_quote(quote_number="Q123", client=client_staging)

# Cleanup
client_prod.close()
client_staging.close()

# Or use context managers for safety
with BritecoreAPIClient("production").init_client() as client_prod, \
     BritecoreAPIClient("staging").init_client() as client_staging:
    
    quote_prod = quotes.retrieve_quote(quote_number="Q123", client=client_prod)
    quote_staging = quotes.retrieve_quote(quote_number="Q123", client=client_staging)
```

---

### Pattern 3: Testing & Mocking

#### Before (v1.x)
```python
from unittest.mock import patch, MagicMock
from britecore_sdk.api.api_calls import init_api_client, reset_api_client
from britecore_sdk.api.api_calls.v2 import quotes

def test_quote_retrieval():
    init_api_client(target_site="test")
    
    # Messy: need to mock the module-level api_client
    with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock_client:
        mock_client.do_request.return_value = MagicMock()
        mock_client.process_result.return_value = {"id": "Q123", "premium": 100}
        
        result = quotes.retrieve_quote(quote_number="Q123")
        assert result["premium"] == 100
    
    reset_api_client()
```

#### After (v2.0.0)
```python
from unittest.mock import MagicMock
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes

def test_quote_retrieval():
    # Create a mock client
    mock_client = MagicMock(spec=BritecoreAPIClient)
    mock_client.do_request.return_value = MagicMock()
    mock_client.process_result.return_value = {"id": "Q123", "premium": 100}
    
    # Pass mock client explicitly - no patching needed
    result = quotes.retrieve_quote(quote_number="Q123", client=mock_client)
    assert result["premium"] == 100
    
    # Verify calls
    mock_client.do_request.assert_called_once()
    mock_client.process_result.assert_called_once()
```

---

### Pattern 4: Async Workflows

#### Before (v1.x)
```python
import asyncio
from britecore_sdk.api.api_calls import init_async_api_client
from britecore_sdk.api.api_calls.v2 import async_quotes

async def fetch_quotes():
    init_async_api_client(target_site="production")
    
    # Implicit global async client
    quotes = await asyncio.gather(
        async_quotes.aretrieve_quote(quote_number="Q1"),
        async_quotes.aretrieve_quote(quote_number="Q2"),
    )
    return quotes

asyncio.run(fetch_quotes())
```

#### After (v2.0.0)
```python
import asyncio
from britecore_sdk import AsyncBritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import async_quotes

async def fetch_quotes():
    client = AsyncBritecoreAPIClient("production").init_client()
    
    try:
        # Explicit client passed to async wrappers
        quotes = await asyncio.gather(
            async_quotes.aretrieve_quote(quote_number="Q1", client=client),
            async_quotes.aretrieve_quote(quote_number="Q2", client=client),
        )
        return quotes
    finally:
        await client.aclose()

asyncio.run(fetch_quotes())
```

**Or with async context manager:**

```python
async def fetch_quotes():
    async with AsyncBritecoreAPIClient("production").init_client() as client:
        quotes = await asyncio.gather(
            async_quotes.aretrieve_quote(quote_number="Q1", client=client),
            async_quotes.aretrieve_quote(quote_number="Q2", client=client),
        )
        return quotes
```

---

### Pattern 5: Class-Based Workflows

#### Before (v1.x)
```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import quotes

class QuoteManager:
    def __init__(self, site: str):
        self.site = site
        init_api_client(target_site=site)
    
    def get_quote(self, quote_id: str):
        # Relies on module-level client being initialized
        return quotes.retrieve_quote(quote_number=quote_id)
```

#### After (v2.0.0)
```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import quotes

class QuoteManager:
    def __init__(self, site: str):
        self.site = site
        self.client = BritecoreAPIClient(site).init_client()
    
    def get_quote(self, quote_id: str):
        # Explicit client stored as instance variable
        return quotes.retrieve_quote(quote_number=quote_id, client=self.client)
    
    def close(self):
        self.client.close()

# Usage
manager = QuoteManager("production")
try:
    quote = manager.get_quote("Q123")
finally:
    manager.close()

# Or context manager support
class QuoteManager:
    def __init__(self, site: str):
        self.site = site
        self.client = BritecoreAPIClient(site).init_client()
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.client.close()
    
    def get_quote(self, quote_id: str):
        return quotes.retrieve_quote(quote_number=quote_id, client=self.client)

# Usage with context manager
with QuoteManager("production") as manager:
    quote = manager.get_quote("Q123")
```

---

## Backwards Compatibility

**v1.x patterns still work in v2.0.0** (but will generate deprecation warnings):

```python
# ✅ Still works in v2.0.0 (with deprecation warning)
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import quotes

init_api_client(target_site="production")
quote = quotes.retrieve_quote(quote_number="Q123")  # No client= parameter
```

**Deprecation warning output:**

```
DeprecationWarning: Implicit module-level client usage is deprecated and will be removed in v2.1.0.
Pass client= parameter explicitly or call resolve_client(None).
```

---

## Transition Timeline

### v2.0.0 (Current)
- ✅ Explicit `client=` parameter available on all wrappers
- ✅ Implicit client still works (with deprecation warnings)
- ✅ Migration guide provided

### v2.1.0 (Future)
- 🔄 Implicit client usage will generate louder warnings
- 🔄 Consider adding strict mode flag to disable implicit client
- 🔄 Update all examples to explicit client pattern

### v3.0.0 (Future Major)
- ❌ Implicit client support removed
- ❌ All wrappers require explicit `client=` parameter
- ❌ Module-level state fully eliminated

---

## Helper Functions

### resolve_client

```python
from britecore_sdk.api.api_calls import resolve_client, get_api_client

# Explicitly handle client resolution
client = resolve_client(client_param)  # Use explicit if provided, else module-level

# Get module-level client directly
module_client = get_api_client()

# Get async client
module_async_client = get_async_api_client()
```

### use_api_client (v1.x-style, still works)

```python
from britecore_sdk.api.api_calls import init_api_client, use_api_client
from britecore_sdk.api.api_calls.v2 import quotes

# Initialize default client
default_client = init_api_client(target_site="production")

# Temporarily use different client in a context
other_client = init_api_client(target_site="staging")
with use_api_client(other_client):
    quote = quotes.retrieve_quote(quote_number="Q123")  # Uses other_client
# Back to default_client after context exits
```

**Note:** `use_api_client` is a v1.x compatibility helper. In v2.0.0, just pass the `client=` parameter directly.

---

## Checklist: Migrating Your Code

- [ ] Install britecore_sdk ≥ 2.0.0
- [ ] Replace `from britecore_sdk.api.api_calls import init_api_client` with `from britecore_sdk import BritecoreAPIClient`
- [ ] Replace `init_api_client(target_site="...")` with `client = BritecoreAPIClient("...").init_client()`
- [ ] Add `client=client` parameter to all endpoint wrapper calls
- [ ] Add cleanup: `.close()` or use context manager (`with ... as client:`)
- [ ] Update tests to pass mock clients instead of patching module-level state
- [ ] Update type hints if using type stubs (new `client` parameter type)
- [ ] Run tests to verify no regressions
- [ ] Update internal documentation and examples

---

## FAQ

**Q: Do I have to migrate immediately?**

A: No. v2.0.0 still supports the v1.x implicit client pattern (with deprecation warnings). Migration can happen incrementally over several releases.

**Q: Can I use both patterns in the same codebase?**

A: Yes. You can mix v1.x and v2.0.0 patterns. Just ensure:
- Module-level client is initialized (if using implicit pattern)
- Explicit client is passed (if using explicit pattern)

**Q: Will my v1.x tests still work?**

A: Most likely yes, but you may see deprecation warnings. Update tests to use explicit clients for cleaner, isolated tests.

**Q: What about batch operations?**

A: Batch helpers also accept the explicit `client=` parameter. Example:

```python
from britecore_sdk import BritecoreAPIClient
from britecore_sdk.api.workflows import batch_quotes

client = BritecoreAPIClient("site").init_client()

results = batch_quotes.create_full_quotes_batch(
    quotes=[...],
    client=client,
)
```

**Q: How do I handle cleanup with context managers?**

A: Use the `with` statement:

```python
from britecore_sdk import BritecoreAPIClient

with BritecoreAPIClient("site").init_client() as client:
    # Use client here
    result = retrieve_quote(quote_id="Q123", client=client)
# Cleanup happens automatically
```

---

## See Also

- [V2_ROADMAP.md](V2_ROADMAP.md) — Full v2.0.0 architecture roadmap
- [DEPRECATION.md](DEPRECATION.md) — Deprecation policy
- [AGENTS.md](AGENTS.md) — Development workflow

