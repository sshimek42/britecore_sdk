# Getting Started

*Last updated: April 8, 2026*
*Document type: Living guide*

Use this guide for the fastest path from clone to first successful API call.

## Start here

- Install the package in editable mode.
- Set `target_site` and `system` for runtime behavior.
- Configure site credentials in Dynaconf config files.
- Run a smoke check to confirm imports and version.

Related docs:

- [README.md](README.md) for a high-level overview
- [API.md](API.md) for endpoint reference
- [docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md) for async wrapper cache behavior
- [PYTHON_COMPATIBILITY.md](PYTHON_COMPATIBILITY.md) for supported Python versions and stability commitments
- [ARCHITECTURE.md](ARCHITECTURE.md) for design details
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common errors

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

### Step 1: Copy Example Configuration Files

Example files are provided to show you the correct format:

```powershell
Copy-Item src\britecore_sdk\settings\.secrets.toml.example src\britecore_sdk\settings\.secrets.toml
Copy-Item src\britecore_sdk\settings\settings.toml.example src\britecore_sdk\settings\settings.toml
```

```bash
cp src/britecore_sdk/settings/.secrets.toml.example src/britecore_sdk/settings/.secrets.toml
cp src/britecore_sdk/settings/settings.toml.example src/britecore_sdk/settings/settings.toml
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

See [CONFIG_MANAGEMENT.md](CONFIG_MANAGEMENT.md) for complete setup instructions.

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

### Authentication Behavior

The SDK automatically selects authentication mode based on configured credentials:

- **API Key Auth:** Use when `client_id` and `client_secret` are blank/missing
- **OAuth Auth:** Use when both `client_id` AND `client_secret` are provided

Required keys in `.secrets.toml` for each site:

- `base_url` — API endpoint URL (always required)
- Either `api_key` (for API key auth) or both `client_id` + `client_secret` (for OAuth)

## Smoke checks

```powershell
python -c "import britecore_sdk; print(britecore_sdk.__version__)"
python -c "from britecore_sdk.api.api_calls import init_api_client; print(type(init_api_client('your_site')).__name__)"
```

```bash
python -c "import britecore_sdk; print(britecore_sdk.__version__)"
python -c "from britecore_sdk.api.api_calls import init_api_client; print(type(init_api_client('your_site')).__name__)"
```

Readiness checks:

```powershell
python -m britecore_sdk.utils.check_site_configs
python -m britecore_sdk.utils.healthcheck --site your_site
```

```bash
python -m britecore_sdk.utils.check_site_configs
python -m britecore_sdk.utils.healthcheck --site your_site
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

## Async cached wrappers

Use async wrappers from `britecore_sdk.api.api_calls.v2` for non-blocking API calls.
Read wrappers are cache-aware by default and mutation wrappers invalidate related namespaces.
For exact behavior, supported cache kwargs, and invalidation examples, use
[docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md).

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

- The `api_client` proxy initializes lazily on first use. Use `get_api_client()` for explicit initialization or to force config reload. Use `init_api_client()` only for advanced/manual re-initialization scenarios.
- API client initialization failures usually indicate missing `target_site` or site config.
- Endpoint wrappers expect response normalization through `process_result(...)`; prefer using provided `v2` modules.
- If policy name mapping behaves unexpectedly, verify `system` is set for regex map selection.
