# Getting Started

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
- [ARCHITECTURE.md](ARCHITECTURE.md) for design details
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common errors

## Prerequisites

- Python `>=3.14`
- PowerShell (commands below use PowerShell syntax)

## Install

```powershell
python -m pip install -e .
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

- `src/britecore_libraries/config/settings.toml`
- `src/britecore_libraries/config/.secrets.toml`

Required site keys:

- `base_url`
- `client_id`
- `client_secret`
- `api_key`

Authentication behavior is automatic:

- API key auth when `client_id` and `client_secret` are blank
- OAuth auth when both are provided

## Smoke checks

```powershell
python -c "import britecore_libraries; print(britecore_libraries.__version__)"

python -c "from britecore_libraries.api.api_calls import get_api_client; print(type(get_api_client()).__name__)"
```

## First API call

```python
from britecore_libraries.api.api_calls.v2 import policies

result = policies.retrieve_policy(policy_number="POL001")
print(result)
```

## Async cached wrappers

Use async wrappers from `britecore_libraries.api.api_calls.v2` for non-blocking API calls.
Read wrappers are cache-aware by default and mutation wrappers invalidate related namespaces.
For exact behavior, supported cache kwargs, and invalidation examples, use
[docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md).

```python
import asyncio

from britecore_libraries.api.api_calls.v2 import aget_quote


async def main() -> None:
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

- Import-time failures in API modules usually indicate missing `target_site` or site config.
- Endpoint wrappers expect response normalization through `process_result(...)`; prefer using provided `v2` modules.
- If policy name mapping behaves unexpectedly, verify `system` is set for regex map selection.
