# Getting Started

*Last updated: July 21, 2026*
*Document type: Living guide*

Use this guide for the fastest path from clone to first successful API call.

## Start here

- Install the package in editable mode.
- Set `target_site` and `system` for runtime behavior.
- Configure site credentials in Dynaconf config files.
- Run a smoke check to confirm imports and version.

Related docs:

- [README.md](./README.md) for a high-level overview
- [API.md](./API.md) for endpoint reference
- [docs/ASYNC_CACHING.md](./docs/ASYNC_CACHING.md) for async wrapper cache behavior
- [PYTHON_COMPATIBILITY.md](./PYTHON_COMPATIBILITY.md) for supported Python versions and stability commitments
- [ARCHITECTURE.md](./ARCHITECTURE.md) for design details
- [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) for common errors

## Prerequisites

- Python `>=3.11`
- PowerShell (commands below use PowerShell syntax)

## Install

```powershell
python -m pip install -e .
```

```bash
python -m pip install -e .
```

API-only profile (recommended):

- If you are only calling BriteCore APIs, stop at the base install above.

Optional extras (only if your app explicitly uses those helpers):

```powershell
python -m pip install -e ".[all]"        # all optional extras
```

```bash
python -m pip install -e ".[all]"        # all optional extras
```

Install development tooling when you plan to run tests:

```powershell
python -m pip install -e ".[dev]"
```

```bash
python -m pip install -e ".[dev]"
```

## Configuration

The SDK automatically loads settings from several locations in priority order. Choose the approach
that best fits how you installed the SDK:

Use the canonical precedence table in
[`docs/CONFIGURATION.md`](./docs/CONFIGURATION.md#canonical-precedence-table).

### For pip-installed users (recommended): user-level config

Create `~/.britecore/settings.toml` and `~/.britecore/.secrets.toml`. These apply to all your
projects without touching SDK package files.

**`~/.britecore/settings.toml`:**

```toml
[default]
target_site = "production"
```

**`~/.britecore/.secrets.toml`:**

```toml
[production]
base_url = "https://api.britecore.example.com"
client_id = "your-actual-client-id"
client_secret = "your-actual-client-secret"
```

Then skip to [Step 3](#step-3-customize-settingstoml-optional) below.

### For repo clones: copy example files from source

### Step 1: Copy Example Configuration Files

Example files are provided to show you the correct format:

```powershell
Copy-Item src\britecore_sdk\settings\sample\.secrets.toml src\britecore_sdk\settings\.secrets.toml
Copy-Item src\britecore_sdk\settings\sample\settings.toml src\britecore_sdk\settings\settings.toml
```

```bash
cp src/britecore_sdk/settings/sample/.secrets.toml src/britecore_sdk/settings/.secrets.toml
cp src/britecore_sdk/settings/sample/settings.toml src/britecore_sdk/settings/settings.toml
```

### Step 2: Edit `.secrets.toml` with Your Credentials

Replace placeholder values with your actual BriteCore API credentials:

```toml
[production]
base_url = "https://api.britecore.example.com"
client_id = "your-actual-client-id"
client_secret = "your-actual-client-secret"
```

### Step 3: Customize `settings.toml` (Optional)

Override default timeouts and select your target site:

```toml
[default]
web_timeout = 10
target_site = 'production'
```

See [CONFIG_MANAGEMENT.md](./CONFIG_MANAGEMENT.md) for complete setup instructions.

### Step 4: Set Environment Variables (Optional)

Set environment variables for the current shell session:

```powershell
$env:target_site = "your_site"
$env:system = "your_system"
```

```bash
export target_site="your_site"
export system="your_system"
```

**Note:** `target_site` can also be set in `settings.toml` — environment variable takes precedence if both are set.
In standard initialization, a non-empty `target_site` is required. In explicit mode
(`init_api_client(base_url=..., ...)`), `target_site` is optional and defaults to `"explicit"`.

### Explicit inline credentials (no config files)

Pass credentials directly to `init_api_client()` or `BritecoreAPIClient.init_client()` to bypass the config file system entirely. This is ideal for serverless functions, containers, and test isolation:

#### API Key Authentication

```python
from britecore_sdk.api.api_calls import init_api_client

client = init_api_client(
    base_url="https://api.britecore.example.com",
    api_key="your-api-key",
)
```

#### OAuth Authentication

```python
from britecore_sdk.api.api_calls import init_api_client

client = init_api_client(
    base_url="https://api.britecore.example.com",
    client_id="your-client-id",
    client_secret="your-client-secret",
)
```

#### Using context manager (v1.1+)

```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import policies

with BritecoreAPIClient("production").init_client(
    base_url="https://api.britecore.example.com",
    api_key="your-api-key"
) as client:
    result = policies.retrieve_policy(policy_number="POL001")
    print(result)
# urllib3 PoolManager auto-closed on exit
```

### Authentication Behavior

The SDK automatically selects authentication mode based on configured credentials:

- **API Key Auth:** Use when `client_id` and `client_secret` are blank/missing
- **OAuth Auth:** Use when both `client_id` AND `client_secret` are provided

Required keys in `.secrets.toml` for each site:

- `base_url` — API endpoint URL (always required)
- Either `api_key` (for API key auth) or both `client_id` + `client_secret` (for OAuth)

To see which auth mode was selected at init time, enable debug logs before calling `get_api_client()` or `init_api_client()`.

Two supported patterns:

#### Pattern A: App-owned logging configuration

Use this when your application already controls logging for all dependencies.

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)
```

#### Pattern B: SDK-managed handler (opt-in)

Use this when you want a quick SDK console formatter without configuring root logging.

```python
import logging
from britecore_sdk import configure_logging

configure_logging(level="INFO")
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)
```

Direct logger access is also available:

```python
from britecore_sdk import logger

logger.info("SDK logging is active")
```

When debug logging is enabled, init emits either `Auth mode selected during init_client: api_key` or `Auth mode selected during init_client: oauth`.

## Smoke checks

```powershell
python -c "import britecore_sdk; print(britecore_sdk.__version__)"
# Fluent one-liner init (new in v1.1)
python -c "from britecore_sdk.api.api_calls import init_api_client; print(repr(init_api_client('your_site')))"
```

```bash
python -c "import britecore_sdk; print(britecore_sdk.__version__)"
python -c "from britecore_sdk.api.api_calls import init_api_client; print(repr(init_api_client('your_site')))"
```

Readiness checks — via installed CLI commands (works in both bash and PowerShell):

```sh
britecore-check-config
britecore-healthcheck --site your_site
```

Or via `python -m` (works in both bash and PowerShell):

```sh
python -m britecore_sdk.utils.check_site_configs
python -m britecore_sdk.utils.healthcheck --site your_site
python -m britecore_sdk.utils.check_api_spec_sync
```

## First API call

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Recommended: Use the lazy-initialized client (auto-loads config on first use)
client = get_api_client()

result = policies.retrieve_policy(policy_number="POL001")
print(result)
```

### Alternative: fluent one-liner + context manager (new in v1.1)

```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import policies

with BritecoreAPIClient("your_site").init_client() as client:
    result = policies.retrieve_policy(policy_number="POL001")
    print(result)
# urllib3 PoolManager closed automatically on exit
```

### Flat exception imports (new in v1.1)

```python
from britecore_sdk import NotFoundError, AuthenticationError, RateLimitError
from britecore_sdk.api.api_calls.v2 import policies

try:
    result = policies.retrieve_policy(policy_number="POL001")
except NotFoundError as e:
    print(f"Policy not found: {e}")
except AuthenticationError as e:
    print(f"Auth error: {e}")
```

### Dry-run flow testing without a live request (new in v1.1)

```python
from britecore_sdk.api.api_calls import init_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Inherit dry-run for all requests made through this client.
# For OAuth sites, this skips token acquisition unless you explicitly pass headers.
init_api_client(client_dry_run=True)

result = policies.retrieve_policy(policy_number="POL001")
print(result["dry_run"])        # True
print(result["auth_skipped"])   # True for OAuth dry-run without caller auth headers
print(result["headers"])        # Redacted by default
```

## Async cached wrappers

Use async wrappers from `britecore_sdk.api.api_calls.v2` for non-blocking API calls.
Read wrappers are cache-aware by default and mutation wrappers invalidate related namespaces.
For exact behavior, supported cache kwargs, and invalidation examples, use
[docs/ASYNC_CACHING.md](./docs/ASYNC_CACHING.md).

```python
import asyncio

from britecore_sdk.api.api_calls import init_async_api_client
from britecore_sdk.api.api_calls.v2 import aget_quote

async def main() -> None:
    # Explicitly initialize the shared async client for your configured site (rarely needed; see docs for lazy pattern).
    init_async_api_client("your_site")
    quote = await aget_quote("quote_123")
    print(quote)

asyncio.run(main())
```

Async dry-run flow testing is also supported:

```python
import asyncio

from britecore_sdk.api.api_calls import init_async_api_client
from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy

async def main() -> None:
    init_async_api_client(client_dry_run=True)
    preview = await aretrieve_policy(policy_number="POL001")
    print(preview["dry_run"])
    print(preview["auth_skipped"])

asyncio.run(main())
```

---

## Rate limiting (new in v1.3.0)

Enable optional client-side rate limiting to prevent overwhelming the API or account rate limits:

```python
from britecore_sdk.api.api_calls import init_api_client

# Enable rate limiting with defaults (10 req/s, 20-request burst)
client = init_api_client("production", enable_rate_limiter=True)

# Or customize parameters
client = init_api_client(
    "production",
    enable_rate_limiter=True,
    rate_limiter_requests_per_second=5.0,     # 5 requests per second
    rate_limiter_burst_size=10,               # allow bursts up to 10 requests
    rate_limiter_adaptive_backoff=True,       # automatic backoff on 429s
    rate_limiter_backoff_timeout_seconds=60.0 # back off for 60 seconds
)
```

The rate limiter is **per-client instance**, so different sites or environments can have different limits.
See [docs/RATE_LIMITING.md](./docs/RATE_LIMITING.md) for complete examples and behavior details.

---

## Batch quote creation (new in v1.3.0)

For workloads creating many entities, use workflow batch helpers to parallelize
creates (quotes, contacts, policies, and risks).

```python
from britecore_sdk.api.workflows import create_full_quotes_batch

quotes_data = [
    {"insured_name": "Alice", ...},
    {"insured_name": "Bob", ...},
    # ... 100+ more
]

# Sync batch with default 5 workers
result = create_full_quotes_batch(
    quotes_data,
    max_workers=5,           # parallel workers
    fail_fast=False          # collect all results even on error
)

print(f"Created: {result['succeeded']}/{result['total']}")
print(f"Failed: {result['failed']}")
```

For async workloads:

```python
import asyncio
from britecore_sdk.api.workflows import acreate_full_quotes_batch

async def main():
    result = await acreate_full_quotes_batch(quotes_data, max_concurrent=5)
    print(f"Created: {result['succeeded']}/{result['total']}")

asyncio.run(main())
```

See [docs/BATCH_QUOTE_CREATION.md](./docs/BATCH_QUOTE_CREATION.md) for advanced options and real-world examples.

---

## Run tests

```powershell
python -m pytest tests/ -v
python -m pytest tests/unit -m unit -v
python -m pytest tests/integration -m integration -v
```

```bash
python -m pytest tests/ -v
python -m pytest tests/unit -m unit -v
python -m pytest tests/integration -m integration -v
```

## API Client Initialization Notes

- The `api_client` proxy initializes lazily on first use. Use `get_api_client()` for explicit control over the shared lazy client. Use `init_api_client()` for advanced/manual initialization scenarios.
- `init_client()` now returns `Self`, so `BritecoreAPIClient("site").init_client()` is a valid one-liner.
- Use the context manager (`with BritecoreAPIClient("site").init_client() as client:`) to ensure the connection pool is closed on exit.
- For multi-site scripts, bind wrappers to a specific client with `use_api_client(client)` instead of repeatedly mutating global client state.
- Call `reset_api_client()` to clear the module-level client (useful in tests or multi-site scripts).
- API client initialization failures usually indicate missing `target_site`/site config in standard mode, or missing `base_url` in explicit mode.
- Endpoint wrappers expect response normalization through `process_result(...)`; prefer using provided `v2` modules.
- If policy name mapping behaves unexpectedly, verify `system` is set for regex map selection.
