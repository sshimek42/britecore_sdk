# AGENTS.md

For a compact version, see `AGENTS.quickstart.md`.

## Scope and source of truth

- Treat `src/britecore_libraries/` as the active codebase; ignore generated copies in `build/`, `dist/`, `env/`, and `*.egg-info/` unless packaging issues require them.
- Tests live under `tests/` (not under `src/`), so run targeted pytest for changed modules and keep focused import/smoke checks for config-sensitive paths.

## Repo layout contract

- Authored source lives in `src/britecore_libraries/`; authored tests live in `tests/`; authored docs live in root `*.md` files and `docs/`.
- Generated outputs are non-source and should not be edited directly: `build/`, `dist/`, `env/`, `.venv/`, `*.egg-info/`, `htmlcov/`, and `docs/_build/`.
- Canonical compatibility/backlog docs are root files: `PYTHON_COMPATIBILITY.md` and `UNIMPLEMENTED_API_STUBS.md`; files under `docs/` include them for documentation builds.

## Big-picture architecture

- API access centers on `BritecoreAPIClient` in `src/britecore_libraries/api/britecore_api_client.py`; endpoint wrappers call `do_request(...)` then `process_result(...)`.
- API module client access is lazy in `src/britecore_libraries/api/api_calls/__init__.py`: `api_client` is a proxy and initializes through `get_api_client()` on first use.
- Auth mode is selected in `BritecoreAPIClient.init_client()`: API key if `client_id`/`client_secret` are blank, otherwise OAuth via `OAuthToken` (`src/britecore_libraries/api/britecore_oauth_token_manager.py`).
- Domain shaping is separate from transport: models in `src/britecore_libraries/models/` and validators in `src/britecore_libraries/validators/` prepare payloads, API modules send them.
- Legacy compatibility layer exists in `src/britecore_libraries/classes/__init__.py` and emits `DeprecationWarning`; prefer imports from `models`/`validators`.

## API module pattern (copy this when adding endpoints)

- Follow `src/britecore_libraries/api/api_calls/v2/quotes.py`: build request dict, call `API_CLIENT.do_request(path=..., json=..., **kwargs)`, then return `API_CLIENT.process_result(...)`.
- Use `RequestParameters` (`TypedDict` in `britecore_api_client.py`) with `**kwargs: Unpack[RequestParameters]` for timeout/retry/header overrides.
- For mutually exclusive identifiers, reuse `API_CLIENT.multiple_parameter_verification(...)` (example: `retrieve_policy` in `v2/policies.py`).
- Keep endpoints versioned under `api/api_calls/v1` and `api/api_calls/v2`; v2 is the primary surface.

## Docstring source policy

- For endpoint wrapper functions, use `api_specs/current/britecore.json` as the primary source for summary, parameter intent, and response semantics.
- Treat files under `api_specs/legacy/` as archival/reference input for backlog or migration work, not as the default enforcement target for wrapper docs or tests.
- Add SDK-specific context only where needed (for example: snake_case aliases, `RequestParameters`, or `process_result(...)` normalization behavior).
- If the spec and current wrapper behavior differ, prefer describing the documented API contract and call out SDK-specific differences explicitly and briefly.

## Configuration and integration points

- Runtime config is Dynaconf-based in `src/britecore_libraries/config/config.py`, loading `config/.secrets.toml` + `config/settings.toml`.
- Required site keys are validated (`base_url`, `client_id`, `client_secret`, `api_key`) for configured environments.
- Important env vars used directly by code: `target_site` (client init) and `system` (regex map selection in `maps/britecore_policy_name_map.py`).
- External integrations: `urllib3` (HTTP), OAuth2 token endpoint `/api/auth/oauth2/token`, `pyodbc` in `utils/britecore_odbc.py`, Selenium helpers in `utils/britecore_selenium.py`, CSV-backed zip lookup in `utils/zip_code_lookup.py`.

## Developer workflow in this repo

- Python target in `pyproject.toml` is `>=3.11`; keep edits syntax-compatible with modern Python 3 and avoid introducing features that would unnecessarily raise the minimum version.
- **Single source of truth:** Use `pyproject.toml` for version and dependency specs. Both `setup.py` and all `requirements.txt` files are kept in sync automatically.
- Install editable package from repo root:

```powershell

python -m pip install -e .

```

- Minimal smoke check after changes (adjust module names to your edits):

```powershell

python -c "import britecore_libraries; from britecore_libraries.api.britecore_api_client import BritecoreAPIClient; print(britecore_libraries.__version__)"

```

## Logging

- Logger is exposed as `britecore_libraries.logger` (standard Python `logging.Logger`).
- Use `logger.info()`, `logger.debug()`, `logger.error()`, etc. for logging.
- Logs are written to console and (by default) to `~/.britecore_logs/{package_name}.log`.
- Library users can configure logging via standard Python logging mechanisms:

```python
import logging
logging.getLogger("britecore_libraries").setLevel(logging.DEBUG)  # Module-level control
logging.basicConfig(level=logging.INFO)  # Global config
```

- Don't create new logger instances in modules; use the package logger or `logging.getLogger(__name__)`.

## Gotchas that affect agent changes

- API client initialization is now lazy: `api_client` is a proxy that initializes on first use, avoiding failures in contexts without config/env. Call `get_api_client()` for explicit control.
- `process_result(...)` expects JSON responses shaped like `{success, data, message/messages}`; wrappers that bypass it (some v1 modules) handle raw payloads differently.
- Keep public exports updated via `__all__` in package `__init__.py` files when adding new top-level functionality.
