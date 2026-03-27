# britecore_libraries

[![Documentation Status](https://readthedocs.org/projects/britecore-libraries/badge/?version=latest)](https://britecore-libraries.readthedocs.io/en/latest/)

Python utilities and API wrappers for working with BriteCore services.

## Start here

- Use the library: install, configure, and call a `v2` endpoint.
- Contribute to the library: use editable install, run tests, follow project conventions.

Key docs:

- [Hosted docs (Read the Docs)](https://britecore-libraries.readthedocs.io/en/latest/)
- [GETTING_STARTED.md](GETTING_STARTED.md) for broader setup and examples
- [API.md](API.md) for endpoint reference and coverage details
- [docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md) for async wrapper cache behavior and tuning
- [ARCHITECTURE.md](ARCHITECTURE.md) for component-level design
- [CONTRIBUTING.md](CONTRIBUTING.md) for contribution workflow
- [AGENTS.md](AGENTS.md) for repository-specific coding guidance
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

## What this package provides

- Domain models in `src/britecore_libraries/models/` for contact, policy, and quote payloads
- Data validators in `src/britecore_libraries/validators/` for names, email, phone, and addresses
- Versioned endpoint wrappers in `src/britecore_libraries/api/api_calls/v1` and `src/britecore_libraries/api/api_calls/v2`
- Shared API transport in `src/britecore_libraries/api/britecore_api_client.py`
- Utilities in `src/britecore_libraries/utils/` for ODBC, Selenium helpers, and ZIP lookup

## Use the library

Requirements:

- Python `>=3.14` (from `pyproject.toml`)

Install:

```powershell
python -m pip install -e .
```

Configure runtime environment variables:

```powershell
$env:target_site = "your_site"
$env:system = "your_system"
```

Set site values in `src/britecore_libraries/config/settings.toml` and `src/britecore_libraries/config/.secrets.toml`.
Required site keys: `base_url`, `client_id`, `client_secret`, `api_key`.

Quick smoke check:

```powershell
python -c "import britecore_libraries; from britecore_libraries.api.britecore_api_client import BritecoreAPIClient; print(britecore_libraries.__version__)"
```

Minimal API call example:

```python
from britecore_libraries.api.api_calls.v2 import policies

result = policies.retrieve_policy(policy_number="POL001")
print(result)
```

## Use async cached wrappers

The `v2` package now exports async wrappers directly (for example `aget_quote`,
`aget_contact`, `aretrieve_policy`) with cache-aware defaults for read calls.
Use [docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md) for exact defaults, kwargs,
and invalidation behavior.



## Contribute to the library

Install with development dependencies:

```powershell
python -m pip install -e ".[dev]"
```

Run tests:

```powershell
python -m pytest tests/ -v
python -m pytest tests/unit -m unit -v
python -m pytest tests/integration -m integration -v
```

Follow repository conventions in `AGENTS.md`, especially around endpoint wrapper patterns and lazy API client usage via `get_api_client()`.

## Architecture notes

- `BritecoreAPIClient` handles transport and response processing
- Endpoint modules generally build request JSON, call `do_request(...)`, and return `process_result(...)`
- Auth mode is automatic: API key when `client_id`/`client_secret` are blank; OAuth when both are provided
- Config is Dynaconf-based in `src/britecore_libraries/config/config.py`
- API client access in wrapper modules is lazy through `src/britecore_libraries/api/api_calls/__init__.py`

