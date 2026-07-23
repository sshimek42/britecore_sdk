# britecore_sdk

*Last updated: July 21, 2026*
*Document type: Living guide*

A professional **Python SDK for the BriteCore API** — complete endpoint coverage, async support, OAuth/API key authentication, and type hints.

> No existing BriteCore client library? Look no further. This SDK provides spec-aligned wrappers, domain models, validators, and clean async helpers.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/pypi/v/britecore_sdk.svg)](https://pypi.org/project/britecore_sdk/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![Tests](https://github.com/sshimek42/britecore_sdk/actions/workflows/tests.yml/badge.svg)](https://github.com/sshimek42/britecore_sdk/actions)
[![codecov](https://codecov.io/gh/sshimek42/britecore_sdk/graph/badge.svg)](https://codecov.io/gh/sshimek42/britecore_sdk)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![ReadTheDocs](https://app.readthedocs.org/projects/britecore-sdk/badge/?version=latest)](https://britecore-sdk.readthedocs.io/en/latest/)

**Status:** Stable (v2.0.5+) | **License:** Apache-2.0 | **Python:** 3.11+

---

## Quick Start

### 1. Install

**Windows (PowerShell):**

```powershell
pip install britecore_sdk
```

**Linux/macOS (bash):**

```bash
pip install britecore_sdk
```

### 2. Configure

Set `target_site` and credentials via config files or environment variables. The SDK discovers
config files automatically from several locations. For the canonical precedence table, see
[`CONFIG_MANAGEMENT.md`](./CONFIG_MANAGEMENT.md#config-file-search-hierarchy).

> **Note:** Hostnames under `example.com` in this repository are placeholders. Replace with your
> real BriteCore API host values.

**Recommended for most users: user-level config (`~/.britecore/`)**

Works across all your projects without touching SDK package files:

```toml
# ~/.britecore/settings.toml
[default]
target_site = "production"
```

```toml
# ~/.britecore/.secrets.toml
[production]
base_url = "https://api.britecore.example.com"
api_key = "your_api_key_here"
```

For full API key/OAuth examples, project-local files, and env-var-only setup, use
[`CONFIG_MANAGEMENT.md`](./CONFIG_MANAGEMENT.md) and [`GETTING_STARTED.md`](./GETTING_STARTED.md).

### 3. Use

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Recommended: Use the lazy-initialized client (auto-loads config on first use)
client = get_api_client()

# Retrieve a policy
result = policies.retrieve_policy(policy_number="POL001")
print(result)
```

See [examples/basic_api_usage.py](examples/basic_api_usage.py) for more detailed examples.

---

### About API Client Initialization

The `api_client` proxy (from `api.api_calls`) initializes lazily on first use, avoiding import-time failures if config is missing. Use `get_api_client()` for explicit control over the shared lazy client. Use `init_api_client()` for advanced/manual initialization scenarios (for example explicit credentials or multi-site binding).

If you need to verify selected auth mode during initialization, enable SDK debug logging before client init. The client emits `Auth mode selected during init_client: api_key` or `Auth mode selected during init_client: oauth` at debug level.

Pattern A (app-owned logging, preferred for host apps):

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)
```

Pattern B (SDK-managed handler, opt-in):

```python
import logging
from britecore_sdk import configure_logging

configure_logging(level="INFO")
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)
```

You can also log directly through the package logger:

```python
from britecore_sdk import logger

logger.info("SDK logger is configured")
```

---

## Features

- ✅ **Spec-aligned API coverage** — wrapper/spec alignment checks against `api_specs/current/britecore.json`
- ✅ **Async-ready** — Cache-aware async wrappers for high-concurrency workflows
- ✅ **Flexible auth** — Automatic API key or OAuth2 token management
- ✅ **Type hints** — Full PEP 561 type information for IDE support
- ✅ **Validators** — Email, phone, address, and name validation utilities
- ✅ **Models** — Domain classes for Contact, Policy, and Quote payloads
- ✅ **Config-first** — Dynaconf-based environment and secrets management
- ✅ **Production-ready** — Stable API, comprehensive tests, security-focused
- ✅ **Context manager** — `with BritecoreAPIClient("site").init_client() as client:`
- ✅ **Flat exceptions** — `from britecore_sdk import NotFoundError, AuthenticationError`
- ✅ **CLI commands** — `britecore-healthcheck`, `britecore-check-config`, `britecore-run-checks`
- ✅ **Debug dry-run** — per-call `dry_run=True` or client default `init_api_client(client_dry_run=True)`
- ✅ **Rate limiting** — Optional token bucket with adaptive backoff on 429 responses
- ✅ **Batch operations** — workflow helpers for parallel quote/contact/policy/risk creation

---

## Documentation

| Topic | Link |
| --- | --- |
| **Setup & examples** | [GETTING_STARTED.md](./GETTING_STARTED.md) |
| **API reference** | [API.md](./API.md) |
| **Async & caching** | [docs/ASYNC_CACHING.md](./docs/ASYNC_CACHING.md) |
| **Rate limiting** | [docs/RATE_LIMITING.md](./docs/RATE_LIMITING.md) |
| **Batch operations** | [docs/BATCH_QUOTE_CREATION.md](./docs/BATCH_QUOTE_CREATION.md) |
| **Architecture** | [ARCHITECTURE.md](./ARCHITECTURE.md) |
| **Python compatibility** | [PYTHON_COMPATIBILITY.md](./PYTHON_COMPATIBILITY.md) |
| **Contributing** | [CONTRIBUTING.md](./CONTRIBUTING.md) |
| **Code of Conduct** | [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md) |
| **Troubleshooting** | [TROUBLESHOOTING.md](./TROUBLESHOOTING.md) |
| **Security policy** | [SECURITY.md](./SECURITY.md) |

## Installation & Configuration

### Requirements

- Python `>=3.11`

### Install

**Windows (PowerShell):**

```powershell
# Base install (API client + wrappers)
pip install britecore_sdk

# With optional extras
pip install britecore_sdk[all]         # All extras
pip install britecore_sdk[dev]         # Development (tests, linting, type checking)
```

**Linux/macOS (bash):**

```bash
# Base install (API client + wrappers)
pip install britecore_sdk

# With optional extras
pip install britecore_sdk[all]         # All extras
pip install britecore_sdk[dev]         # Development (tests, linting, type checking)
```

### Configuration

The SDK loads settings from multiple locations in priority order — later sources override earlier ones.
`BRITECORE_SDK_*` environment variables always win over any file. See the canonical precedence
table in [`CONFIG_MANAGEMENT.md`](./CONFIG_MANAGEMENT.md#config-file-search-hierarchy).

Use one of these setup paths:

- **User-level config (recommended):** `~/.britecore/settings.toml` + `~/.britecore/.secrets.toml`
- **Project-local config:** `./britecore.toml` + `./.britecore_secrets.toml`
- **Explicit credentials in code:** `init_api_client(base_url=..., api_key=...)`
- **Environment variables:** `BRITECORE_SDK_*` values override all file-based settings

> **Note:** Hostnames under `example.com` in this repository are placeholders.
> In standard file/env mode, `target_site` is required.
> In explicit mode (`init_api_client(base_url=..., ...)`), `target_site` is optional and defaults to `"explicit"`.

See [`GETTING_STARTED.md`](./GETTING_STARTED.md) and [`CONFIG_MANAGEMENT.md`](./CONFIG_MANAGEMENT.md) for full configuration examples.

Validate configured sites before first API calls:

```sh
# As an installed command (after pip install) — works in bash and PowerShell:
britecore-check-config

# Or via python -m:
python -m britecore_sdk.utils.check_site_configs
```

Check whether the checked-in local API spec is current and whether upstream has a newer version:

```sh
python -m britecore_sdk.utils.check_api_spec_sync
```

Run an end-user readiness check (config + auth + safe API ping):

```sh
# As an installed command:
britecore-healthcheck --site production

# Or via python -m:
python -m britecore_sdk.utils.healthcheck --site production
```

Validation rule: each site needs `base_url` and either a full OAuth pair
(`client_id` + `client_secret`) or an `api_key`.

---

## What This Package Provides

### API Wrappers

- **Endpoint modules:** broad v2 domain coverage plus supported v1 wrapper modules where the upstream API still uses `v1` paths (see `API.md` for current module inventory)
- **Async wrappers:** Cache-aware async versions of key endpoint workflows

### Utilities

- **Models:** `BritecoreContact`, `BritecorePolicy`, `BritecoreQuote` with type hints
- **Validators:** Email, phone, address, and name validation
- **Auth:** Automatic OAuth2 or API key selection based on config
- **Config:** Dynaconf-based environment/secrets management
- **Logging:** Structured logging with standard Python logging module

### Optional Extras

- **Interactive:** Menu-driven CLI utilities (`questionary`)

---

## Using Async Wrappers

The `v2` package exports async-aware wrappers (e.g., `aget_quote`, `aget_contact`, `aretrieve_policy`) with built-in caching for read operations.

```python
import asyncio
from britecore_sdk.api.api_calls.v2 import async_policies

async def main():
    policy = await async_policies.aretrieve_policy(policy_number="POL001")
    print(policy)

asyncio.run(main())
```

See [docs/ASYNC_CACHING.md](./docs/ASYNC_CACHING.md) for cache configuration and invalidation.

---

## Development

### Install for Development

**Windows (PowerShell):**

```powershell
pip install -e ".[dev]"
```

**Linux/macOS (bash):**

```bash
pip install -e ".[dev]"
```

### Run Tests

**Windows (PowerShell):**

```powershell
# All tests
pytest tests/ -v

# By category
pytest tests/unit -m unit -v
pytest tests/integration -m integration -v

# Core client changes
pytest tests/unit/test_api_client.py tests/unit/test_core_client_coverage.py -v
```

**Linux/macOS (bash):**

```bash
# All tests
pytest tests/ -v

# By category
pytest tests/unit -m unit -v
pytest tests/integration -m integration -v

# Core client changes
pytest tests/unit/test_api_client.py tests/unit/test_core_client_coverage.py -v
```

### Linting & Type Checking

**Windows (PowerShell):**

```powershell
ruff check src/
black --check src/
mypy src/britecore_sdk/api/britecore_api_client.py
```

**Linux/macOS (bash):**

```bash
ruff check src/
black --check src/
mypy src/britecore_sdk/api/britecore_api_client.py
```

### Release Publishing (GitHub Actions)

- TestPyPI dry-run workflow: `.github/workflows/publish-testpypi.yml` (**manual trigger only** via `workflow_dispatch`)
- Production PyPI workflow: `.github/workflows/publish.yml` (**automatic** after `.github/workflows/release.yml` completes successfully, and also **manually runnable** via `workflow_dispatch`)

Both workflows use OIDC trusted publishing and include build + publish + install smoke tests. Depending on your GitHub environment protection rules, the publish job may still pause for environment approval even when the workflow itself was triggered automatically.

1. Create GitHub environments: `testpypi` and `pypi`.
2. In TestPyPI, add a Trusted Publisher entry for:
   - Repository: `sshimek42/britecore_sdk`
   - Workflow: `.github/workflows/publish-testpypi.yml`
   - Environment: `testpypi`
3. In PyPI, add a Trusted Publisher entry for:
   - Repository: `sshimek42/britecore_sdk`
   - Workflow: `.github/workflows/publish.yml`
   - Environment: `pypi`
4. Run `Publish to TestPyPI` from the Actions tab before cutting a production release.
5. Push a version tag (for example `v2.0.5`) to trigger `.github/workflows/release.yml`, which builds artifacts and creates the GitHub Release automatically.
6. After `.github/workflows/release.yml` completes successfully, `.github/workflows/publish.yml` runs automatically and publishes to PyPI. You can also run `Publish to PyPI` manually from the Actions tab when needed.

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:

- Workflow and branch conventions
- Endpoint wrapper patterns
- Code quality expectations
- Repository-specific guidance in [AGENTS.md](./AGENTS.md)

## Architecture

- **`BritecoreAPIClient`** — Core HTTP transport and response processing
- **Context manager** — `with client:` pattern closes the connection pool on exit
- **Fluent init** — `client = BritecoreAPIClient("site").init_client()` (one-liner)
- **Endpoint modules** — Build request JSON → call `do_request()` → return `process_result()`
- **Auth modes** — Automatic: API key (when `client_id`/`client_secret` blank) or OAuth2 (when both provided)
- **Config** — Dynaconf-based layered config: SDK defaults → `~/.britecore/` → `./britecore.toml` → `BRITECORE_SDK_SETTINGS_FILE` → env vars
- **Lazy initialization** — API client initializes on first use to avoid import-time failures (see "About API Client Initialization" above)
- **Flat exceptions** — Import `NotFoundError`, `AuthenticationError` etc. directly from `britecore_sdk`

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed design.

---

## Support & Links

- **Issues & feedback:** [GitHub Issues](https://github.com/sshimek42/britecore_sdk/issues)
- **Security concerns:** See [SECURITY.md](SECURITY.md)
- **Roadmap & stability:** See [STABILITY.md](./STABILITY.md)
- **External API docs:** [api.britecore.com](https://api.britecore.com/) (supplemental reference)
