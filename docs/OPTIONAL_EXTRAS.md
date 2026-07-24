# Optional Extras

The base `britecore_sdk` install is kept intentionally lightweight. Three optional
extras add enhanced capabilities without imposing dependencies on users who don't need
them.

---

## `async-http` — native async HTTP transport

```bash
pip install britecore_sdk[async-http]
```

Adds `httpx` as a dependency, enabling true non-blocking async I/O in
`AsyncBritecoreAPIClient`. Without this extra the async client wraps the sync
`urllib3` transport in `asyncio.to_thread` (fully functional, but not natively async).

### Usage

```python
from britecore_sdk.api import AsyncBritecoreAPIClient

# Default — threaded transport (no extra required)
client = AsyncBritecoreAPIClient(target_site="prod")

# Native async transport (requires britecore_sdk[async-http])
client = AsyncBritecoreAPIClient(target_site="prod", async_transport="httpx")
```

You can inject a pre-built `httpx.AsyncClient` for connection pool sharing or testing:

```python
import httpx
from britecore_sdk.api import AsyncBritecoreAPIClient

shared_httpx = httpx.AsyncClient(timeout=30)
client = AsyncBritecoreAPIClient(
    target_site="prod",
    async_transport="httpx",
    httpx_client=shared_httpx,
)
```

> **Note:** Dry-run mode always uses the threaded path (no real request is sent
> regardless of transport selection).

See [ASYNC_CACHING](ASYNC_CACHING) for cache configuration and transport-mode
comparison.

---

## `typed-config` — pydantic-validated settings view

```bash
pip install britecore_sdk[typed-config]
```

Adds `pydantic` and `pydantic-settings` as dependencies, providing a strongly-typed,
IDE-friendly view of the active Dynaconf configuration.

> **Important:** This is additive. Dynaconf remains the runtime source of truth.
> `get_typed_settings()` reads from the live Dynaconf instance and returns a
> validated snapshot — it does not replace or bypass the configuration system.

### Usage

```python
from britecore_sdk.settings import get_typed_settings

# Get a typed view of selected site configs
typed = get_typed_settings(site_names=["prod", "staging"])

# Strongly-typed access with IDE autocompletion
print(typed.sites["prod"].base_url)
print(typed.sites["prod"].api_key)
print(typed.default_web_timeout)
```

The returned object is a `pydantic-settings` model with the following shape:

| Field | Type | Notes |
| --- | --- | --- |
| `target_site` | `str \| None` | Active target site from settings |
| `default_web_timeout` | `int \| None` | Default HTTP timeout |
| `default_web_retry` | `int \| None` | Default retry count |
| `sites` | `dict[str, TypedSiteSettings]` | Per-site typed configs |

Each entry in `sites` exposes: `base_url`, `client_id`, `client_secret`, `api_key`,
`web_timeout`, `web_retry`, `web_timeout_long`.

---

## `interactive` — menu-driven CLI utilities

```bash
pip install britecore_sdk[interactive]
```

Adds `questionary` as a dependency, enabling the interactive `britecore-config-wizard`
and menu-driven config management CLI.

---

## Installing multiple extras

```bash
# All optional extras
pip install britecore_sdk[all]

# Specific combination
pip install britecore_sdk[async-http,typed-config]
```

The `all` extra is equivalent to `britecore_sdk[interactive,async-http,typed-config]`.
