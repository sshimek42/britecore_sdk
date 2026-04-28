# Multi-Tenancy Guide

*Last updated: April 28, 2026*
*Document type: Integration guide*

This guide covers patterns for using the BriteCore SDK across multiple sites/tenants in a single application or service.

---

## Overview

The SDK is designed to support multi-tenancy through:

1. **Module-level `api_client` proxy** — Lazy-initialized singleton
2. **`use_api_client(client)` context manager** — Bind wrapper calls to a specific client
3. **`reset_api_client()` function** — Clear the module-level client (for site switching)
4. **Explicit client instantiation** — Create independent `BritecoreAPIClient` instances per site
5. **Thread-safe initialization** — Each site gets its own HTTP connection pool

---

## Pattern 1: Module-Level Client with Reset (Simplest)

Use the shared module-level client and reset it when switching sites. Best for sequential site operations.

```python
from britecore_sdk.api.api_calls import get_api_client, reset_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Site 1: Initialize client for production
api_client = get_api_client()  # Auto-loads config for 'production' from settings
result1 = policies.retrieve_policy(policy_number="POL001")
print(f"Production: {result1['data']['policy_number']}")

# Switch to staging
reset_api_client()  # Clear the module-level client
import os
os.environ["target_site"] = "staging"  # Change site
api_client = get_api_client()  # Reinitialize for new site
result2 = policies.retrieve_policy(policy_number="POL002")
print(f"Staging: {result2['data']['policy_number']}")

# Back to production
reset_api_client()
del os.environ["target_site"]  # or restore original value
api_client = get_api_client()  # Back to production
```

**Pros:**
- Simplest pattern
- Reuses lazy initialization
- Works for script-like operations

**Cons:**
- Environmental coupling (requires env var changes or file rewrites)
- Not ideal for concurrent operations
- Manual reset management

---

## Pattern 2: Explicit Inline Credentials + `use_api_client` (Recommended)

Pass credentials directly to `init_api_client()` — each call creates a new configured client. Best for concurrent multi-site operations.

```python
from britecore_sdk.api.api_calls import init_api_client, use_api_client
from britecore_sdk.api.api_calls.v2 import policies, contacts

# Function to get a client for any site
def get_site_client(site_name: str, base_url: str, api_key: str):
    """Initialize a client for a specific site with inline credentials."""
    return init_api_client(
        site_name,
        base_url=base_url,
        api_key=api_key
    )

# Configuration for multiple sites
sites = {
    "production": {
        "base_url": "https://api.britecore.prod.example.com",
        "api_key": "prod-api-key-xxx",
    },
    "staging": {
        "base_url": "https://api.britecore.staging.example.com",
        "api_key": "staging-api-key-yyy",
    },
    "qa": {
        "base_url": "https://api.britecore.qa.example.com",
        "api_key": "qa-api-key-zzz",
    },
}

# Process policies across all sites (sequential)
for site_name, creds in sites.items():
    client = get_site_client(site_name, creds["base_url"], creds["api_key"])
    with use_api_client(client):
        result = policies.retrieve_policy(policy_number="POL001")
    print(f"{site_name}: {result['data']['policy_number']}")
```

**Pros:**
- No config file coupling
- Each client is independent
- Clean separation per site
- Easy to test

**Cons:**
- Credentials passed in code (use env vars or secure vaults)
- Credentials not in config files

---

## Pattern 3: Context Manager for Isolated Operations

Use `BritecoreAPIClient` context manager for guaranteed resource cleanup. Best for long-running services.

```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import policies

sites = {
    "production": ("https://api.prod.example.com", "prod-key"),
    "staging": ("https://api.staging.example.com", "staging-key"),
}

# Process each site in isolation
for site_name, (base_url, api_key) in sites.items():
    with BritecoreAPIClient(site_name).init_client(
        base_url=base_url,
        api_key=api_key
    ) as client:
        result = policies.retrieve_policy(policy_number="POL001")
        print(f"{site_name} (via context manager): {result}")
    # urllib3 PoolManager auto-closed on exit
```

**Pros:**
- Guaranteed resource cleanup
- No connection leaks
- Very testable
- Clear site isolation

**Cons:**
- Slightly more verbose

---

## Pattern 4: Long-Lived Clients in a Service Registry

For background services/workers, maintain a registry of pre-initialized clients.

```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import policies
import threading
from typing import Dict

class SiteClientRegistry:
    """Thread-safe registry of per-site clients."""

    def __init__(self):
        self._clients: Dict[str, BritecoreAPIClient] = {}
        self._lock = threading.Lock()

    def get_or_create(self, site_name: str, base_url: str, api_key: str) -> BritecoreAPIClient:
        """Get or create a client for a site (thread-safe)."""
        if site_name in self._clients:
            return self._clients[site_name]

        with self._lock:
            if site_name not in self._clients:
                client = BritecoreAPIClient(site_name).init_client(
                    base_url=base_url,
                    api_key=api_key
                )
                self._clients[site_name] = client
            return self._clients[site_name]

    def cleanup(self, site_name: str = None):
        """Close a client or all clients."""
        with self._lock:
            if site_name:
                if site_name in self._clients:
                    self._clients[site_name].__exit__(None, None, None)
                    del self._clients[site_name]
            else:
                for client in self._clients.values():
                    client.__exit__(None, None, None)
                self._clients.clear()

# Usage in a background service
registry = SiteClientRegistry()

def process_policy_updates(site_name: str, base_url: str, api_key: str):
    """Background worker that periodically calls an API."""
    client = registry.get_or_create(site_name, base_url, api_key)
    result = policies.retrieve_policy(policy_number="POL001")
    print(f"Processed: {result['data']['policy_number']}")

# Cleanup on shutdown
def on_shutdown():
    registry.cleanup()
```

**Pros:**
- Efficient for long-running services
- Reuses connections per site
- Thread-safe
- Explicit lifecycle control

**Cons:**
- Manual cleanup required
- More complex

---

## Pattern 5: Configuration File per Environment

Store site configs in separate TOML files and switch via `BRITECORE_SDK_SETTINGS_FILE`.

**Directory structure:**

```text
config/
├── prod.toml
├── prod.secrets.toml
├── staging.toml
└── staging.secrets.toml
```

**prod.toml:**

```toml
[default]
target_site = "production"
web_timeout = 10

[production]
# Leave empty — credentials go in prod.secrets.toml
```

**prod.secrets.toml:**

```toml
[production]
base_url = "https://api.prod.example.com"
api_key = "prod-key-xxx"
```

**Python to switch:**

```python
import os
from britecore_sdk.api.api_calls import get_api_client, reset_api_client

# Switch to production
os.environ["BRITECORE_SDK_SETTINGS_FILE"] = "config/prod.toml"
reset_api_client()
client = get_api_client()

# Switch to staging
os.environ["BRITECORE_SDK_SETTINGS_FILE"] = "config/staging.toml"
reset_api_client()
client = get_api_client()
```

**Pros:**
- Environment-specific configs version-controlled
- Clean separation
- Easy to deploy

**Cons:**
- Still requires file I/O and `reset_api_client()`
- Not ideal for concurrent operations

---

## Best Practices

### 1. Use Explicit Credentials for Independent Sites

```python
# ✅ Good: Each site is independent
prod_client = init_api_client("prod", base_url="...", api_key="...")
staging_client = init_api_client("staging", base_url="...", api_key="...")

result1 = policies.retrieve_policy(policy_number="POL001")  # Uses prod_client
result2 = policies.retrieve_policy(policy_number="POL002")  # Uses staging_client
```

### 2. Store Credentials in Environment Variables or Secure Vaults

```python
import os

prod_client = init_api_client(
    "prod",
    base_url=os.environ["PROD_BASE_URL"],
    api_key=os.environ["PROD_API_KEY"],
)
```

### 3. Use Context Manager for Request Isolation

```python
# ✅ Good: Guaranteed cleanup
with BritecoreAPIClient("prod").init_client(...) as client:
    result = policies.retrieve_policy(...)
# Pool closed, no leaks

# ❌ Avoid: Manual cleanup
client = init_api_client("prod", ...)
result = policies.retrieve_policy(...)
# No explicit cleanup
```

### 4. Don't Mix Module-Level and Explicit Initialization

```python
# ❌ Avoid: Confusing to read
from britecore_sdk.api.api_calls import get_api_client, init_api_client

api_client = get_api_client()  # Module-level
result1 = policies.retrieve_policy(...)

other_client = init_api_client("other_site", ...)  # Explicit
result2 = policies.retrieve_policy(...)  # Which client is used?
```

### 5. Include Site Name in Logs and Traces

```python
import logging

logger = logging.getLogger(__name__)

for site_name, creds in sites.items():
    client = init_api_client(site_name, ...)
    logger.info(f"Processing site: {site_name}", extra={"site": site_name})
    result = policies.retrieve_policy(...)
    logger.info(f"Result for {site_name}: {result['data']}", extra={"site": site_name})
```

---

## Concurrent Multi-Tenancy with Async

For concurrent operations across sites, use async wrappers with independent clients:

```python
import asyncio
from britecore_sdk.api.britecore_async_api_client import AsyncBritecoreAPIClient
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy

async def fetch_policy_for_site(site_name: str, base_url: str, api_key: str, policy_num: str):
    """Fetch a policy from one site (concurrent-safe)."""
    async with AsyncBritecoreAPIClient(site_name).init_client(
        base_url=base_url,
        api_key=api_key
    ) as client:
        result = await aretrieve_policy(policy_number=policy_num)
        return site_name, result

async def main():
    """Concurrently fetch from multiple sites."""
    sites = {
        "prod": ("https://api.prod.example.com", "prod-key"),
        "staging": ("https://api.staging.example.com", "staging-key"),
    }

    tasks = [
        fetch_policy_for_site(site_name, url, key, "POL001")
        for site_name, (url, key) in sites.items()
    ]

    results = await asyncio.gather(*tasks)
    for site_name, result in results:
        print(f"{site_name}: {result['data']['policy_number']}")

asyncio.run(main())
```

---

## Testing Multi-Tenancy

```python
import pytest
from britecore_sdk.api.api_calls import init_api_client

@pytest.fixture
def prod_client():
    """Fixture for production site client (dry-run mode)."""
    return init_api_client(
        "prod",
        base_url="https://api.prod.example.com",
        api_key="test-key",
        client_dry_run=True,
    )

@pytest.fixture
def staging_client():
    """Fixture for staging site client (dry-run mode)."""
    return init_api_client(
        "staging",
        base_url="https://api.staging.example.com",
        api_key="test-key",
        client_dry_run=True,
    )

def test_policy_lookup_across_sites(prod_client, staging_client):
    """Test that policy lookup works on both sites."""
    from britecore_sdk.api.api_calls.v2 import policies

    # Dry-run calls — no network, just payload shapes
    prod_result = policies.retrieve_policy(policy_number="POL001")
    staging_result = policies.retrieve_policy(policy_number="POL001")

    assert prod_result["dry_run"] is True
    assert staging_result["dry_run"] is True
```

---

## Common Patterns by Use Case

| Use Case | Pattern | Why |
|----------|---------|-----|
| **Script processing multiple sites sequentially** | Pattern 1 (Module + Reset) | Simple, no file overhead |
| **Microservice with multiple tenants** | Pattern 4 (Service Registry) | Reuses connections, thread-safe |
| **Background worker** | Pattern 3 (Context Manager) | Clean resource lifecycle |
| **Serverless function (AWS Lambda, etc)** | Pattern 2 (Explicit Creds) | Stateless, no file I/O |
| **Long-running API server** | Pattern 4 (Registry) or Pattern 3 | Connection pooling |
| **Test suite** | Pattern 2 (Explicit Creds) + dry-run | Isolation per test |

---

## Troubleshooting

### "Different sites returning same data"

**Cause:** Module-level client not reset between site switches

**Solution:**

```python
from britecore_sdk.api.api_calls import reset_api_client
reset_api_client()  # Clear before switching sites
```

### "Connection pool exhausted"

**Cause:** Too many long-lived clients without cleanup

**Solution:**

```python
# Use context manager for cleanup
with BritecoreAPIClient("site").init_client(...) as client:
    result = policies.retrieve_policy(...)
# Cleanup happens automatically
```

### "Site config not found"

**Cause:** `target_site` mismatches config section name

**Solution:**

```python
# Ensure target_site matches a section in settings.toml / .secrets.toml
[staging]  # This is the section name
base_url = "..."
api_key = "..."

# Set target_site to match
os.environ["target_site"] = "staging"
```

---

## See Also

- [CONFIG_MANAGEMENT.md](../CONFIG_MANAGEMENT.md) — Configuration file hierarchy
- [docs/OBSERVABILITY.md](OBSERVABILITY.md) — Logging across multiple sites
- [GETTING_STARTED.md](../GETTING_STARTED.md) — Initial setup
