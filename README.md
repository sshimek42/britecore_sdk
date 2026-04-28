# britecore_sdk

A professional **Python SDK for the BriteCore API** — complete endpoint coverage, async support, OAuth/API key authentication, and type hints.

> No existing BriteCore client library? Look no further. This SDK provides everything you need: 374+ endpoints, domain models, validators, and clean async wrappers.

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache--2.0-green.svg)](https://opensource.org/licenses/Apache-2.0)
[![codecov](https://codecov.io/gh/sshimek42/britecore_sdk/graph/badge.svg?token=BVRUP1ROTF)](https://codecov.io/gh/sshimek42/britecore_sdk)

**Status:** Stable (v1.2.0) | **License:** Apache-2.0 | **Python:** 3.11+

---

## Quick Start

### 1. Install

```bash
pip install britecore_sdk
```

### 2. Configure

Set `target_site` and credentials via config files or environment variables. The SDK discovers
config files automatically from several locations (later sources override earlier ones):

| Priority | Location | File(s) |
|---|---|---|
| 1 (lowest) | SDK package defaults | `<sdk>/settings/settings.toml`, `<sdk>/settings/.secrets.toml` |
| 2 | User-level (all projects on machine) | `~/.britecore/settings.toml`, `~/.britecore/.secrets.toml` |
| 3 | Project-local (current directory) | `./britecore.toml`, `./.britecore_secrets.toml` |
| 4 | Explicit file override | Path pointed to by `BRITECORE_SDK_SETTINGS_FILE` |
| 5 (highest) | Environment variables | `BRITECORE_SDK_BASE_URL`, `BRITECORE_SDK_API_KEY`, … |

**Recommended for most users: user-level config (`~/.britecore/`)**

Works across all your projects without touching the SDK package files:

`~/.britecore/settings.toml`:

```toml
[default]
target_site = "production"
```

`~/.britecore/.secrets.toml`:

```toml
[production]
base_url = "https://your-britecore-instance.com"
api_key = "your_api_key_here"
```

**Alternative: project-local config (current working directory)**

Place `britecore.toml` and `.britecore_secrets.toml` in your project root. Add
`.britecore_secrets.toml` to `.gitignore` to keep secrets out of version control:

```toml
# britecore.toml (safe to commit)
[default]
target_site = "production"
```

```toml
# .britecore_secrets.toml (add to .gitignore!)
[production]
base_url = "https://your-britecore-instance.com"
api_key = "your_api_key_here"
```

**Alternative: Environment variables**

> **Note:** `target_site` is required for file/environment-driven initialization (the standard mode).
> In explicit mode (`init_api_client(base_url=..., ...)`), `target_site` is optional and defaults
> to `"explicit"`. When credentials are set via
> `BRITECORE_SDK_*` environment variables, `target_site` is still required but its value
> does not affect which credentials are loaded when **all** required credentials are supplied as
> env vars — they take precedence over `.secrets.toml` values regardless of the site name. If any
> required credential is missing from env vars, the client falls back to the `.secrets.toml`
> section matching the `target_site` value, so the name must correspond to a real section in that
> case. You can also pass `target_site` explicitly to `init_api_client()` instead of setting it
> as an env var.

**Linux/macOS (bash):**

```bash
export BRITECORE_SDK_BASE_URL="https://your-britecore-instance.com"
export BRITECORE_SDK_API_KEY="your_api_key_here"
export target_site="production"  # selects .secrets.toml section; any name works when all creds are set via env vars
```

**Windows (PowerShell):**

```powershell
$env:BRITECORE_SDK_BASE_URL="https://your-britecore-instance.com"
$env:BRITECORE_SDK_API_KEY="your_api_key_here"
$env:target_site="production"  # selects .secrets.toml section; any name works when all creds are set via env vars
```

Or for OAuth:

**Linux/macOS (bash):**

```bash
export BRITECORE_SDK_BASE_URL="https://your-britecore-instance.com"
export BRITECORE_SDK_CLIENT_ID="your_client_id"
export BRITECORE_SDK_CLIENT_SECRET="your_client_secret"
export target_site="production"  # selects .secrets.toml section; any name works when all creds are set via env vars
```

**Windows (PowerShell):**

```powershell
$env:BRITECORE_SDK_BASE_URL="https://your-britecore-instance.com"
$env:BRITECORE_SDK_CLIENT_ID="your_client_id"
$env:BRITECORE_SDK_CLIENT_SECRET="your_client_secret"
$env:target_site="production"  # selects .secrets.toml section; any name works when all creds are set via env vars
```

### 3. Use

```python
from britecore_sdk.api.api_calls import get_api_client
from britecore_sdk.api.api_calls.v2 import policies

# Recommended: Use the lazy-initialized client (auto-loads config on first use)
client = get_api_client()

# Retrieve a policy
result = policies.retrieve_policy(policy_number="POL001")
print(result)

See [examples/basic_api_usage.py](examples/basic_api_usage.py) for more detailed examples.

---

### About API Client Initialization

The `api_client` proxy (from `api.api_calls`) initializes lazily on first use, avoiding import-time failures if config is missing. Use `get_api_client()` for explicit initialization or to force config reload. Use `init_api_client()` only for advanced/manual re-initialization scenarios.

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

---

## Features

✅ **Complete API coverage** — 374/374 endpoints across v1 and v2
✅ **Async-ready** — Cache-aware async wrappers for high-concurrency workflows
✅ **Flexible auth** — Automatic API key or OAuth2 token management
✅ **Type hints** — Full PEP 561 type information for IDE support
✅ **Validators** — Email, phone, address, and name validation utilities
✅ **Models** — Domain classes for Contact, Policy, and Quote payloads
✅ **Config-first** — Dynaconf-based environment and secrets management
✅ **Production-ready** — Stable API, comprehensive tests, security-focused
✅ **Context manager** — `with BritecoreAPIClient("site").init_client() as client:`
✅ **Flat exceptions** — `from britecore_sdk import NotFoundError, AuthenticationError`
✅ **CLI commands** — `britecore-healthcheck`, `britecore-check-config`, `britecore-run-checks`
✅ **Debug dry-run** — per-call `dry_run=True` or client default `init_api_client(client_dry_run=True)`

---

## Documentation

| Topic | Link |
| --- | --- |
| **Setup & examples** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **API reference** | [API.md](API.md) |
| **Async & caching** | [docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md) |
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Python compatibility** | [PYTHON_COMPATIBILITY.md](PYTHON_COMPATIBILITY.md) |
| **Contributing** | [CONTRIBUTING.md](CONTRIBUTING.md) |
| **Troubleshooting** | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| **Security policy** | [SECURITY.md](SECURITY.md) |

## Installation & Configuration

### Requirements

- Python `>=3.11`

### Install

```bash
# Base install (API client + wrappers)
pip install britecore_sdk

# With optional extras
pip install britecore_sdk[all]         # All extras
pip install britecore_sdk[dev]         # Development (tests, linting, type checking)
```

### Configuration

The SDK loads settings from multiple locations in priority order — later sources override earlier ones.
`BRITECORE_SDK_*` environment variables always win over any file:

| Priority | Location | File(s) |
|---|---|---|
| 1 (lowest) | SDK package defaults | `<sdk>/settings/settings.toml`, `<sdk>/settings/.secrets.toml` |
| 2 | User-level (all projects on machine) | `~/.britecore/settings.toml`, `~/.britecore/.secrets.toml` |
| 3 | Project-local (current directory) | `./britecore.toml`, `./.britecore_secrets.toml` |
| 4 | Explicit file override | Path pointed to by `BRITECORE_SDK_SETTINGS_FILE` |
| 5 (highest) | Environment variables | `BRITECORE_SDK_BASE_URL`, `BRITECORE_SDK_API_KEY`, … |

#### Option A: User-level config (recommended for pip-installed users)

Create `~/.britecore/settings.toml` and `~/.britecore/.secrets.toml`. Settings here apply to all
projects on the machine without touching SDK package files:

**`~/.britecore/settings.toml`** (example):

```toml
[default]
target_site = "production"
```

**`~/.britecore/.secrets.toml`** (never commit):

API key authentication:

```toml
[production]
base_url = "https://api.britecore.example.com"
api_key = "your_real_api_key"

[staging]
base_url = "https://api-staging.britecore.example.com"
api_key = "your_staging_api_key"
```

Or OAuth authentication:

```toml
[production]
base_url = "https://api.britecore.example.com"
client_id = "your_real_client_id"
client_secret = "your_real_client_secret"

[staging]
base_url = "https://api-staging.britecore.example.com"
client_id = "your_staging_client_id"
client_secret = "your_staging_client_secret"
```

#### Option B: Project-local config

Place `britecore.toml` and `.britecore_secrets.toml` in your project's working directory.
Add `.britecore_secrets.toml` to `.gitignore` to keep secrets out of version control:

**`britecore.toml`** (safe to commit):

```toml
[default]
target_site = "production"
```

**`.britecore_secrets.toml`** (add to `.gitignore`!):

```toml
[production]
base_url = "https://api.britecore.example.com"
api_key = "your_real_api_key"
```

#### Option C: SDK package defaults (repo clones only)

If you have cloned the repo and are working directly from source, you can copy the sample files:

**Linux/macOS (bash):**

```bash
cp src/britecore_sdk/settings/sample/settings.toml src/britecore_sdk/settings/settings.toml
cp src/britecore_sdk/settings/sample/.secrets.toml src/britecore_sdk/settings/.secrets.toml
```

**Windows (PowerShell):**

```powershell
Copy-Item src\britecore_sdk\settings\sample\settings.toml src\britecore_sdk\settings\settings.toml
Copy-Item src\britecore_sdk\settings\sample\.secrets.toml src\britecore_sdk\settings\.secrets.toml
```

#### Option D: Environment variables (highest priority, overrides all files)

> **Note on `target_site` with env vars:** In standard init mode, `target_site` selects which section of `.secrets.toml`
> to use for credentials. When **all** required credentials are supplied via `BRITECORE_SDK_*`
> environment variables, the specific `target_site` value does not affect which credentials are
> loaded — env vars take precedence regardless. If any credential is missing from env vars, the
> client falls back to the `.secrets.toml` section matching `target_site`. Either way, `target_site`
> is required unless you use explicit mode (`init_api_client(base_url=..., ...)`).

API key authentication:

**Linux/macOS (bash):**

```bash
export BRITECORE_SDK_BASE_URL="https://api.britecore.example.com"
export BRITECORE_SDK_API_KEY="your_api_key"
export target_site="production"  # required; selects .secrets.toml section (any name works when all creds are in env vars)
```

**Windows (PowerShell):**

```powershell
$env:BRITECORE_SDK_BASE_URL="https://api.britecore.example.com"
$env:BRITECORE_SDK_API_KEY="your_api_key"
$env:target_site="production"  # required; selects .secrets.toml section (any name works when all creds are in env vars)
```

Or OAuth authentication:

**Linux/macOS (bash):**

```bash
export BRITECORE_SDK_BASE_URL="https://api.britecore.example.com"
export BRITECORE_SDK_CLIENT_ID="your_client_id"
export BRITECORE_SDK_CLIENT_SECRET="your_client_secret"
export target_site="production"  # required; selects .secrets.toml section (any name works when all creds are in env vars)
```

**Windows (PowerShell):**

```powershell
$env:BRITECORE_SDK_BASE_URL="https://api.britecore.example.com"
$env:BRITECORE_SDK_CLIENT_ID="your_client_id"
$env:BRITECORE_SDK_CLIENT_SECRET="your_client_secret"
$env:target_site="production"  # required; selects .secrets.toml section (any name works when all creds are in env vars)
```

See [GETTING_STARTED.md](GETTING_STARTED.md) and [docs/CONFIGURATION.md](docs/CONFIGURATION.md) for detailed setup.

Validate configured sites before first API calls:

```sh
# As an installed command (after pip install) — works in bash and PowerShell:
britecore-check-config

# Or via python -m:
python -m britecore_sdk.utils.check_site_configs
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

- **Endpoint modules:** 30 modules covering policies, contacts, quotes, payments, and more (374+ endpoints)
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

See [docs/ASYNC_CACHING.md](docs/ASYNC_CACHING.md) for cache configuration and invalidation.

---

## Development

### Install for Development

```bash
pip install -e ".[dev]"
```

### Run Tests

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

```bash
ruff check src/
black --check src/
mypy src/britecore_sdk/api/britecore_api_client.py
```

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for:
- Workflow and branch conventions
- Endpoint wrapper patterns
- Code quality expectations
- Repository-specific guidance in [AGENTS.md](AGENTS.md)

## Architecture

- **`BritecoreAPIClient`** — Core HTTP transport and response processing
- **Context manager** — `with client:` pattern closes the connection pool on exit
- **Fluent init** — `client = BritecoreAPIClient("site").init_client()` (one-liner)
- **Endpoint modules** — Build request JSON → call `do_request()` → return `process_result()`
- **Auth modes** — Automatic: API key (when `client_id`/`client_secret` blank) or OAuth2 (when both provided)
- **Config** — Dynaconf-based layered config: SDK defaults → `~/.britecore/` → `./britecore.toml` → `BRITECORE_SDK_SETTINGS_FILE` → env vars
- **Lazy initialization** — API client initializes on first use to avoid import-time failures (see "About API Client Initialization" above)
- **Flat exceptions** — Import `NotFoundError`, `AuthenticationError` etc. directly from `britecore_sdk`

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed design.

---

## Support & Links

- **Issues & feedback:** [GitHub Issues](https://github.com/sshimek42/britecore_sdk/issues)
- **Security concerns:** See [SECURITY.md](SECURITY.md)
- **Roadmap & stability:** See [STABILITY.md](STABILITY.md)
- **External API docs:** [api.britecore.com](https://api.britecore.com/) (supplemental reference)
