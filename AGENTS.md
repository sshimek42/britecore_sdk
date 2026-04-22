# AGENTS.md

For a compact version, see `AGENTS.quickstart.md`.

## Scope and source of truth

- Treat `src/britecore_sdk/` as the active codebase; ignore generated copies in `build/`, `dist/`, `env/`, and `*.egg-info/` unless packaging issues require them.
- Tests live under `tests/` (not under `src/`), so run targeted pytest for changed modules and keep focused import/smoke checks for config-sensitive paths.

## Repo layout contract

- Authored source lives in `src/britecore_sdk/`; authored tests live in `tests/`; authored docs live in root `*.md` files and `docs/`.
- Generated outputs are non-source and should not be edited directly: `build/`, `dist/`, `env/`, `.venv/`, `*.egg-info/`, `htmlcov/`, and `docs/_build/`.
- Canonical compatibility/backlog docs are root files: `PYTHON_COMPATIBILITY.md` and `UNIMPLEMENTED_API_STUBS.md`; files under `docs/` include them for documentation builds.

## Big-picture architecture

- API access centers on `BritecoreAPIClient` in `src/britecore_sdk/api/britecore_api_client.py`; endpoint wrappers call `do_request(...)` then `process_result(...)`.
- API module client access is lazy in `src/britecore_sdk/api/api_calls/__init__.py`: `api_client` is a proxy and initializes through `get_api_client()` on first use.
- Auth mode is selected in `BritecoreAPIClient.init_client()`: API key if `client_id`/`client_secret` are blank, otherwise OAuth via `OAuthToken` (`src/britecore_sdk/api/britecore_oauth_token_manager.py`).
- Domain shaping is separate from transport: models in `src/britecore_sdk/models/` and validators in `src/britecore_sdk/validators/` prepare payloads, API modules send them.
- Legacy compatibility layer exists in `src/britecore_sdk/classes/__init__.py` and raises `ImportError` directing consumers to `models`/`validators`; prefer imports from `models`/`validators`.

## API module pattern (copy this when adding endpoints)

- Follow `src/britecore_sdk/api/api_calls/v2/quotes.py`: build request dict, call `API_CLIENT.do_request(path=..., json=..., **kwargs)`, then return `API_CLIENT.process_result(...)`.
- Use `RequestParameters` (`TypedDict` in `britecore_api_client.py`) with `**kwargs: Unpack[RequestParameters]` for timeout/retry/header overrides.
- For mutually exclusive identifiers, reuse `API_CLIENT.multiple_parameter_verification(...)` (example: `retrieve_policy` in `v2/policies.py`).
- Keep endpoints under `api/api_calls/v2` for active SDK development; supported v1 wrappers remain where no v2 equivalent exists.

## Docstring source policy

- For endpoint wrapper functions, use `api_specs/current/britecore.json` as the primary source for summary, parameter intent, and response semantics.
- Treat files under `api_specs/legacy/` as archival/reference input only; use `api_specs/current/britecore.json` for wrapper docs and tests.
- Add SDK-specific context only where needed (for example: snake_case aliases, `RequestParameters`, or `process_result(...)` normalization behavior).
- If the spec and current wrapper behavior differ, prefer describing the documented API contract and call out SDK-specific differences explicitly and briefly.

## Configuration and integration points

- Runtime config is Dynaconf-based in `src/britecore_sdk/settings/config.py`, loading `src/britecore_sdk/settings/.secrets.toml` + `src/britecore_sdk/settings/settings.toml`.
- Required site keys are validated (`base_url`, `client_id`, `client_secret`, `api_key`) for configured environments.
- Important env vars used directly by code: `target_site` (client init) and `system` (regex map selection in `maps/britecore_policy_name_map.py`).
- External integrations: `urllib3` (HTTP), OAuth2 token endpoint `/api/auth/oauth2/token`, CSV-backed zip lookup in `utils/zip_code_lookup.py`.

## Developer workflow in this repo

- Python target in `pyproject.toml` is `>=3.11`; keep edits syntax-compatible with modern Python 3 and avoid introducing features that would unnecessarily raise the minimum version.
- **Single source of truth:** Use `pyproject.toml` for version and dependency specs. Both `setup.py` and all `requirements.txt` files are kept in sync automatically.
- Install editable package from repo root:

```powershell
python -m pip install -e .
```

```bash
python -m pip install -e .
```

- Minimal smoke check after changes (adjust module names to your edits):

```powershell
python -c "import britecore_sdk; from britecore_sdk.api.britecore_api_client import BritecoreAPIClient; print(britecore_sdk.__version__)"
```

```bash
python -c "import britecore_sdk; from britecore_sdk.api.britecore_api_client import BritecoreAPIClient; print(britecore_sdk.__version__)"

```

## Logging

- Logger is exposed as `britecore_sdk.logger` (standard Python `logging.Logger`).
- Use `logger.info()`, `logger.debug()`, `logger.error()`, etc. for logging.
- Logs are written to console and (by default) to `~/.britecore_logs/{package_name}.log`.
- Library users can configure logging via standard Python logging mechanisms:

```python
import logging
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)  # Module-level control
logging.basicConfig(level=logging.INFO)  # Global config
```

- Don't create new logger instances in modules; use the package logger or `logging.getLogger(__name__)`.

## Gotchas that affect agent changes

- API client initialization is now lazy: `api_client` is a proxy that initializes on first use, avoiding failures in contexts without config/env. Call `get_api_client()` for explicit control.
- `init_client()` returns `Self` — one-liner `client = BritecoreAPIClient("site").init_client()` is valid and preferred in examples.
- `BritecoreAPIClient` supports the context-manager protocol (`__enter__`/`__exit__`); prefer `with` blocks in examples that need clean teardown.
- `reset_api_client()` (from `api.api_calls`) clears the module-level client; use it in tests for site isolation instead of monkeypatching globals.
- `do_request(...)` accepts `dry_run=True` (part of `RequestParameters`) — logs request details without sending. Document this in any debugging section.
- Flat exception aliases are exported from `britecore_sdk.exceptions` and the top-level package (`NotFoundError`, `AuthenticationError`, etc.). Prefer these in new example code; the nested `BritecoreError.X` form still works.
- Every outbound request carries an `X-SDK-Request-ID` header (short hex correlation ID). The same ID appears in `[req_id] → METHOD /path` debug log lines.
- `process_result(...)` expects JSON responses shaped like `{success, data, message/messages}`; some v1 wrappers with no v2 equivalent may parse raw payloads directly.
- Keep public exports updated via `__all__` in package `__init__.py` files when adding new top-level functionality.
- CLI entry points (`britecore-healthcheck`, `britecore-check-config`, `britecore-run-checks`) are registered in `pyproject.toml [project.scripts]`; re-run `pip install -e .` after adding new ones.
