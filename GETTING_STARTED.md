# Getting Started

*Last updated: July 22, 2026* (added "Getting credentials from BriteCore UI" section)
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
python -m pip install -e ".[interactive]"   # interactive CLI menu utilities (questionary)
python -m pip install -e ".[async-http]"    # native async httpx transport for AsyncBritecoreAPIClient
python -m pip install -e ".[typed-config]"  # pydantic-settings typed view via get_typed_settings()
python -m pip install -e ".[all]"           # all optional extras
```

```bash
python -m pip install -e ".[interactive]"   # interactive CLI menu utilities (questionary)
python -m pip install -e ".[async-http]"    # native async httpx transport for AsyncBritecoreAPIClient
python -m pip install -e ".[typed-config]"  # pydantic-settings typed view via get_typed_settings()
python -m pip install -e ".[all]"           # all optional extras
```

Install development tooling when you plan to run tests:

```powershell
python -m pip install -e ".[dev]"
```

```bash
python -m pip install -e ".[dev]"
```

## Getting credentials from BriteCore UI

Before configuring the SDK, you need to obtain API credentials from your BriteCore instance.

### For OAuth authentication (recommended)

1. Log in to your BriteCore administration interface as an administrator.
2. Navigate to **Administration** → **API Management** → **OAuth Clients**.
3. Click **Create New Client** or **Add New OAuth Application**.
4. Enter a descriptive name for your SDK integration (e.g., "Python SDK Integration").
5. Set the redirect URI (for server-to-server integrations, use `http://localhost:8000/callback` or your application's OAuth callback endpoint).
6. Save the client; BriteCore will generate:
   - **Client ID** — a unique identifier for your application
   - **Client Secret** — keep this secure and never commit to version control
   - **OAuth Token Endpoint** — typically `https://your-britecore-instance/api/auth/oauth2/token`
7. Copy the **Client ID** and **Client Secret** and store them securely (e.g., in `~/.britecore/.secrets.toml`).

### For API Key authentication

1. Log in to your BriteCore administration interface.
2. Navigate to **Administration** → **API Management** → **API Keys**.
3. Click **Generate New API Key**.
4. Provide a name and optional description for the key (e.g., "Python SDK").
5. BriteCore will generate an API Key; copy it immediately as it cannot be retrieved later.
6. Store the API Key securely in your configuration (`~/.britecore/.secrets.toml`).

### Obtaining your BriteCore API URL

1. In the BriteCore UI, go to **Administration** → **System Settings** or **API Management**.
2. Look for the **API Base URL** or **API Endpoint** setting (typically something like `https://api.britecore.example.com` or `https://your-company.britecore.com/api`).
3. Note the base URL (without trailing `/api/` if the wrapper endpoints already include it).
4. Use this URL as `base_url` in your configuration.

---

## Configuration

The SDK automatically loads settings from several locations in priority order. Choose the approach
that best fits how you installed the SDK:

Use the canonical precedence table in
[`CONFIG_MANAGEMENT.md`](./CONFIG_MANAGEMENT.md#config-file-search-hierarchy).

> **Note:** Hostnames under `example.com` in this repository are placeholders. Replace them with
> your real BriteCore API host values.

### Recommended setup: user-level config (`~/.britecore/`)

Create shared config files once for your machine:

```toml
# ~/.britecore/settings.toml
[default]
target_site = "production"
```

```toml
# ~/.britecore/.secrets.toml
[production]
base_url = "https://api.britecore.example.com"
client_id = "your-actual-client-id"
client_secret = "your-actual-client-secret"
```

### Repo-clone setup (optional)

If you work directly in a source clone, copy sample files into `src/britecore_sdk/settings/`:

```powershell
Copy-Item src\britecore_sdk\settings\sample\.secrets.toml src\britecore_sdk\settings\.secrets.toml
Copy-Item src\britecore_sdk\settings\sample\settings.toml src\britecore_sdk\settings\settings.toml
```

```bash
cp src/britecore_sdk/settings/sample/.secrets.toml src/britecore_sdk/settings/.secrets.toml
cp src/britecore_sdk/settings/sample/settings.toml src/britecore_sdk/settings/settings.toml
```

For project-local config files, env-var-only configuration, explicit inline credentials, and full
API key/OAuth examples, use [`CONFIG_MANAGEMENT.md`](./CONFIG_MANAGEMENT.md).

### Optional: set `target_site` and `system` in your shell

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

#### Using context manager

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

### Write safety and audit controls (recommended for admin API keys)

If your API key has broad permissions, configure a write policy to reduce accidental writes.

```toml
# ~/.britecore/settings.toml
[default]
write_policy = "warn"                 # allow | warn | block
write_allowlist = []
write_denylist = []
enable_audit_middleware = true
audit_only_writes = true
audit_log_level = "info"
```

Runtime overrides are also supported when you need stricter behavior for one script:

```python
from britecore_sdk.api.api_calls import init_api_client

client = init_api_client(
    "production",
    write_policy="block",
    enable_audit_middleware=True,
    audit_only_writes=True,
)
```

`write_policy="block"` raises `ReadOnlyViolation` before any write-like request is sent.

## Smoke checks

```powershell
python -c "import britecore_sdk; print(britecore_sdk.__version__)"
# Fluent one-liner init
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

## One-off script mode (no API client)

If you only need model shaping/normalization in small scripts, use the lightweight
data layer directly.

```python
from britecore_sdk.data_layer import normalize_name, normalize_phones

print(normalize_name("acme llc"))
print(normalize_phones([{"phone": "(920) 555-1234", "type": "mobile"}]))
```

This path does not require `get_api_client()` or endpoint wrappers.
Use `normalize_policy_payload(...)` and `normalize_quote_payload(...)` when you
need script-friendly payload shaping for those entities.

CLI alternative for JSON files:

```powershell
britecore-normalize-json --kind contact --input .\contact.raw.json --output .\contact.normalized.json --pretty
```

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Recommended: Use the lazy-initialized client (auto-loads config on first use)
client = get_api_client()

result = policies.retrieve_policy(policy_number="POL001")
print(result)
```

### Alternative: fluent one-liner + context manager

```python
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.api_calls.v2 import policies

with BritecoreAPIClient("your_site").init_client() as client:
    result = policies.retrieve_policy(policy_number="POL001")
    print(result)
# urllib3 PoolManager closed automatically on exit
```

### Flat exception imports

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

### Dry-run flow testing without a live request

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

## Rate limiting

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

## Batch quote creation

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

---

## Contributing code or documentation

### Set up pre-commit hooks (developers only)

If you plan to contribute code or documentation changes, install pre-commit hooks to catch issues before committing:

```powershell
pip install pre-commit
pre-commit install
```

```bash
pip install pre-commit
pre-commit install
```

After installation, pre-commit hooks automatically run before each commit and validate:

- **Code formatting** (ruff, black)
- **Type checking** (mypy)
- **Markdown structure** (syntax, tables)
- **Documentation build** (Sphinx in strict mode)
- **Quick tests** (pytest unit smoke checks)

If hooks fail, fix the issues and try committing again. To bypass (not recommended): `git commit --no-verify`

### Documentation build validation

For documentation changes, always test locally before pushing:

```sh
python -m sphinx -W --keep-going -b html ./docs ./docs/_build/html-strict
```

Common issues and fixes are documented in [`docs/DOCUMENTATION_BUILD_TROUBLESHOOTING.md`](docs/DOCUMENTATION_BUILD_TROUBLESHOOTING.md).

---

## API Client Initialization Notes

- The `api_client` proxy initializes lazily on first use. Use `get_api_client()` for explicit control over the shared lazy client. Use `init_api_client()` for advanced/manual initialization scenarios.
- `init_client()` now returns `Self`, so `BritecoreAPIClient("site").init_client()` is a valid one-liner.
- Use the context manager (`with BritecoreAPIClient("site").init_client() as client:`) to ensure the connection pool is closed on exit.
- For multi-site scripts, bind wrappers to a specific client with `use_api_client(client)` instead of repeatedly mutating global client state.
- Call `reset_api_client()` to clear the module-level client (useful in tests or multi-site scripts).
- API client initialization failures usually indicate missing `target_site`/site config in standard mode, or missing `base_url` in explicit mode.
- Endpoint wrappers expect response normalization through `process_result(...)`; prefer using provided `v2` modules.
- If policy name mapping behaves unexpectedly, verify `system` is set for regex map selection.
