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

API-only profile (recommended):

- If you are only calling BriteCore APIs, stop at the base install above.
- You do **not** need database/browser utilities for API wrappers.

Optional extras (only if your app explicitly uses those helpers):

```powershell
python -m pip install -e ".[database]"   # pyodbc utilities
python -m pip install -e ".[browser]"    # selenium utilities
python -m pip install -e ".[all]"        # all optional extras
```

Install development tooling when you plan to run tests:

```powershell

python -m pip install -e ".[dev]"

```

## Configuration

Set environment variables for the current shell session:

```powershell

$env:target_site = "your_site"
$env:system = "your_system"

```

Configure site values in:

- `src/britecore_libraries/config/settings.toml` — default runtime settings (timeouts/retries/browser)
- `src/britecore_libraries/config/.secrets.toml` — credentials and optional utility keys (`base_url`, `client_id`, `client_secret`, `api_key`, `db_conn_string`, `db_conn_options`, `web_user`, `web_pass`, `web_browser`)

Required keys in `.secrets.toml`:

- `base_url`
- Either `api_key` (for API key auth) or both `client_id` + `client_secret` (for OAuth)

Authentication behavior is automatic:

- API key auth when `client_id` and `client_secret` are blank
- OAuth auth when both are provided

Optional utility notes:

- ODBC utility config is site-scoped and loaded only when calling `get_cursor(...)`.
- ODBC config lookup requires explicit `target_site` in the call when you do not pass `conn_string`/`conn_options` directly.
- Selenium uses flat keys from config (`web_browser`, `web_user`, `web_pass`) and lets `get_driver(browser=...)` override config browser.

## Smoke checks

```powershell

python -c "import britecore_libraries; print(britecore_libraries.__version__)"

python -c "from britecore_libraries.api.api_calls import get_api_client; print(type(get_api_client()).__name__)"

```

## First API call

```python

from britecore_libraries.api.api_calls import init_api_client
from britecore_libraries.api.api_calls.v2 import policies

# Explicitly initialize the shared client for your configured site.
init_api_client("your_site")

result = policies.retrieve_policy(policy_number="POL001")
print(result)

```

## Optional utility examples

```python
from britecore_libraries.utils.britecore_odbc import get_cursor
from britecore_libraries.utils.britecore_selenium import get_driver

# ODBC: load db_conn_string/db_conn_options from [your_site] in .secrets.toml
cursor = get_cursor(target_site="your_site")

# Selenium: explicit browser overrides configured web_browser
driver = get_driver(browser="Firefox")
```

## Async cached wrappers

Use async wrappers from `britecore_libraries.api.api_calls.v2` for non-blocking API calls.
Read wrappers are cache-aware by default and mutation wrappers invalidate related namespaces.
For exact behavior, supported cache kwargs, and invalidation examples, use
[docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md).

```python

import asyncio

from britecore_libraries.api.api_calls import init_async_api_client
from britecore_libraries.api.api_calls.v2 import aget_quote

async def main() -> None:
    # Explicitly initialize the shared async client for your configured site.
    init_async_api_client("your_site")
    quote = await aget_quote("quote_123")
    print(quote)

asyncio.run(main())

```

## Run tests

```powershell

python -m pytest tests/ -v
python -m pytest tests/unit -m unit -v
python -m pytest tests/integration -m integration -v

```

## Common issues

- API client initialization failures usually indicate missing `target_site` or site config.
- Endpoint wrappers expect response normalization through `process_result(...)`; prefer using provided `v2` modules.
- If policy name mapping behaves unexpectedly, verify `system` is set for regex map selection.
