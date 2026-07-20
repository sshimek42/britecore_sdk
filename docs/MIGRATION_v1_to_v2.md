# Migration Guide: SDK v1 → v2

This guide helps you upgrade from BriteCore SDK v1 to v2. While v2 maintains API compatibility, there are some important changes to be aware of.

## Overview of Changes

The v2 upgrade focuses on:
- **Better type hints** for IDE support and type checking
- **Lazy initialization** of API clients
- **Improved exception handling** with structured error messages
- **Async/await support** for high-performance workflows
- **Structured logging** for better observability

## Before (v1) vs After (v2)

### Client Initialization

#### Before (v1 - Eager):
```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

# Client initializes immediately
client = BritecoreAPIClient("production")
client.init_client()
policy = client.do_request(path="/api/policies", ...)
```

#### After (v2 - Lazy & Preferred):
```python
from britecore_sdk.api.api_calls import get_api_client

# Client initializes on first use (lazy)
client = get_api_client()
# OR explicit initialization:
from britecore_sdk.api.api_calls import init_api_client
client = init_api_client("production").init_client()
```

### Endpoint Wrappers

#### Before (v1):
```python
from britecore_sdk.api.api_calls.v1 import policies

# No type hints
result = policies.retrieve_policy(policy_number="POL-123")
```

#### After (v2 - Preferred, v1 still works):
```python
from britecore_sdk.api.api_calls.v2 import policies

# Better type hints, improved docs
result = policies.retrieve_policy(policy_number="POL-123")
```

### Exception Handling

#### Before (v1):
```python
from britecore_sdk.exceptions import BritecoreError

try:
    policy = policies.retrieve_policy(policy_number="POL-123")
except BritecoreError.NotFoundError as e:
    print(f"Policy not found: {e}")
```

#### After (v2 - Flat imports preferred):
```python
from britecore_sdk.exceptions import NotFoundError

try:
    policy = policies.retrieve_policy(policy_number="POL-123")
except NotFoundError as e:
    # Error now includes helpful hints
    print(f"Policy not found: {e}")
    if e.hint:
        print(f"Hint: {e.hint}")
```

### Model Classes

#### Before (v1):
```python
from britecore_sdk.classes import BritecoreContact

contact = BritecoreContact(name="John", ...)
```

#### After (v2):
```python
from britecore_sdk.models import BritecoreContact

contact = BritecoreContact(name="John", ...)
```

### Async Operations

#### Before (v1 - Not available):
```python
# Not supported in v1
```

#### After (v2):
```python
import asyncio
from britecore_sdk.api.api_calls import get_async_api_client
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy

async def get_policies():
    client = get_async_api_client()
    policies = await aretrieve_policy(policy_number="POL-123")
    return policies

# Run async code
result = asyncio.run(get_policies())
```

## Step-by-Step Migration

### Step 1: Update Imports

Find and replace:
- `from britecore_sdk.api.api_calls.v1 import` → `from britecore_sdk.api.api_calls.v2 import`
- `from britecore_sdk.classes import` → `from britecore_sdk.models import`
- `from britecore_sdk.exceptions import BritecoreError` → Use flat imports like `from britecore_sdk.exceptions import NotFoundError`

### Step 2: Update Client Initialization

Old code:
```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

client = BritecoreAPIClient("production")
client.init_client()
```

New code:
```python
from britecore_sdk.api.api_calls import get_api_client

# Lazy - initializes on first use
client = get_api_client()

# OR explicit:
from britecore_sdk.api.api_calls import init_api_client
client = init_api_client("production").init_client()
```

### Step 3: Update Exception Handling

Old code:
```python
from britecore_sdk.exceptions import BritecoreError

try:
    result = endpoint_function()
except BritecoreError.NotFoundError as e:
    handle_not_found(e)
```

New code:
```python
from britecore_sdk.exceptions import NotFoundError

try:
    result = endpoint_function()
except NotFoundError as e:
    handle_not_found(e)
    # New: error includes helpful hints
    if hasattr(e, 'hint'):
        log_hint(e.hint)
```

### Step 4: Update Validator Usage

Old code:
```python
from britecore_sdk.validators import AddressValidator

validator = AddressValidator()
validated = validator.validate({"address": "123 Main", ...})
```

New code (same, but better type hints):
```python
from britecore_sdk.validators import AddressValidator

validator = AddressValidator()
validated = validator.validate({"address": "123 Main", ...})
# Type hints now work better in IDE
```

### Step 5: Enable Logging (Optional)

v2 includes structured logging:
```python
from britecore_sdk import configure_logging, LogCategory

# Enable SDK logging
logger = configure_logging(log_to_file=True)

# Logging now includes categories
from britecore_sdk.base_logger import log_with_category
log_with_category(logger, logging.DEBUG, "My message", LogCategory.AUTH)
```

## Breaking Changes

### 1. Lazy Client Initialization

**What changed:** Clients now initialize on first use instead of immediately.

**Migration:** If you rely on immediate client initialization:
```python
# Old - expects immediate error if config is missing
client = BritecoreAPIClient("production")
client.init_client()  # Errors here if config missing

# New - errors on first request
client = get_api_client()  # Returns immediately
policy = client.do_request(...)  # Errors here if config missing
```

**Fix:** Use `init_api_client()` for eager initialization:
```python
client = init_api_client("production").init_client()  # Still eager
```

### 2. Exception Hierarchy

**What changed:** Exception names are now available at top level.

**Migration:** Update import statements:
```python
# Old
from britecore_sdk.exceptions import BritecoreError
except BritecoreError.NotFoundError:

# New (still works, but preferred is)
from britecore_sdk.exceptions import NotFoundError
except NotFoundError:
```

### 3. Module Removal: britecore_sdk.classes

**What changed:** The `britecore_sdk.classes` module has been removed.

**Migration:**
```python
# Old (no longer works)
from britecore_sdk.classes import BritecoreContact

# New
from britecore_sdk.models import BritecoreContact
```

## Compatibility Notes

### v1 Endpoints Still Supported

For backward compatibility, v1 endpoint wrappers are still available:
```python
# Still works in v2
from britecore_sdk.api.api_calls.v1 import policies
result = policies.retrieve_policy(policy_number="POL-123")
```

**However:** v2 endpoints have better type hints and documentation, so migration is recommended.

### Configuration

Configuration format hasn't changed. Existing `settings.toml` files work as-is:
```toml
[production]
base_url = "https://api.example.com"
api_key = "your_key_here"
```

## Testing Migration

### Before (v1 Tests):
```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from unittest.mock import Mock

mock_client = Mock(spec=BritecoreAPIClient)
mock_client.do_request.return_value = {"data": {...}}
```

### After (v2 Tests - Using New Fixtures):
```python
# Use the new test fixtures library
from tests.fixtures import mock_api_client, mock_policy_response

def test_something(mock_api_client, mock_policy_response):
    # Fixtures handle setup
    pass
```

## Troubleshooting Migration Issues

### Issue: "ImportError: cannot import name 'X' from britecore_sdk.classes"

**Solution:** Use the new module paths:
```python
# Instead of: from britecore_sdk.classes import BritecoreContact
from britecore_sdk.models import BritecoreContact
```

### Issue: "Client not initialized" on first request

**Solution:** You may have caught initialization errors. Check your error handling.

### Issue: Type hints not working in IDE

**Solution:** Make sure you're using v2 endpoints:
```python
# Use v2 for better type hints
from britecore_sdk.api.api_calls.v2 import policies  # Better
# Not: from britecore_sdk.api.api_calls.v1 import policies
```

## Performance Improvements in v2

- **Lazy initialization**: Clients don't initialize until first use
- **Better rate limiting**: Improved exponential backoff and adaptive strategies
- **Async support**: Use async/await for non-blocking operations
- **Request caching**: Optional response caching for repeated queries
- **Structured logging**: Filter logs by category for better performance monitoring

## Timeline for Deprecations

- **v2.0-2.x**: v1 endpoints available for backward compatibility
- **v3.0**: v1 endpoints will be removed
- **v3.0**: `britecore_sdk.classes` will be removed

Start migrating to v2 imports now to prepare for v3.

## Migration Checklist

- [ ] Update all imports from `v1` to `v2`
- [ ] Update `britecore_sdk.classes` imports to `britecore_sdk.models`
- [ ] Update exception imports to use flat names
- [ ] Update client initialization if using `BritecoreAPIClient` directly
- [ ] Review error handling to use new exception hints
- [ ] Enable logging if needed
- [ ] Run existing tests with new code
- [ ] Add new tests using test fixtures library
- [ ] Test async operations if applicable

## Getting Help

If you encounter migration issues:

1. Check [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) for common issues
2. Review [COMMON_PATTERNS.md](COMMON_PATTERNS.md) for migration examples
3. Check your local settings with `britecore-quick-check --full`
4. Review error messages - v2 errors include helpful hints
5. Enable debug logging: `configure_logging("DEBUG")`

## See Also

- [Common Patterns](COMMON_PATTERNS.md)
- [Configuration Guide](./CONFIGURATION.md)
- [API Reference](../api_reference.rst)
- [Error Handling](../TROUBLESHOOTING.md)
