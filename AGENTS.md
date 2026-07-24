# AGENTS.md

*Last updated: July 21, 2026*
*Document type: Development workflow guide*

For developers working on the SDK: understand repository structure, coding patterns, and architectural decisions.

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
- Keep endpoints under `api/api_calls/v2` for active SDK development; v1 wrappers remain supported (not legacy) where no v2 equivalent exists in the reference API.

## Docstring source policy

- For endpoint wrapper functions, use `api_specs/current/britecore.json` as the primary source for summary, parameter intent, and response semantics.
- Treat files under `api_specs/legacy/` as archival/reference input only; use `api_specs/current/britecore.json` for wrapper docs and tests.
- Add SDK-specific context only where needed (for example: snake_case aliases, `RequestParameters`, or `process_result(...)` normalization behavior).
- If the spec and current wrapper behavior differ, prefer describing the documented API contract and call out SDK-specific differences explicitly and briefly.

## Configuration and integration points

- Runtime config uses a **layered file hierarchy** (lowest → highest priority):
  1. SDK package defaults (`src/britecore_sdk/settings/settings.toml` + `.secrets.toml`)
  2. User-level config (`~/.britecore/settings.toml` + `~/.britecore/.secrets.toml`)
  3. Project-local config (`./britecore.toml` + `./.britecore_secrets.toml` in CWD)
  4. Explicit file path (`BRITECORE_SDK_SETTINGS_FILE` env var)
  5. `BRITECORE_SDK_*` environment variables (always highest priority)
- `_discover_settings_files()` (in `config.py`) builds the Dynaconf `settings_files` list at import time; call `from britecore_sdk.settings import setting_files_full` to inspect what was resolved.
- `init_api_client()` and `BritecoreAPIClient.init_client()` accept explicit `base_url`, `api_key`, `client_id`, `client_secret` kwargs to bypass file-based lookup entirely. When `base_url` is given, `target_site` is optional (defaults to `"explicit"`).
- Required site keys are validated (`base_url`, `client_id`, `client_secret`, `api_key`) for configured environments.
- Important env vars used directly by code: `target_site` (client init) and `system` (regex map selection in `maps/britecore_policy_name_map.py`).
- External integrations: `urllib3` (HTTP sync transport), `httpx` (optional native async transport — `britecore_sdk[async-http]`), OAuth2 token endpoint `/api/auth/oauth2/token`, CSV-backed zip lookup in `utils/zip_code_lookup.py`.
- TOML I/O uses stdlib `tomllib` for parsing and `tomli-w` for writing via `britecore_sdk.utils.toml_compat`; the `toml` package is no longer a dependency.
- Optional `pydantic-settings` integration available via `get_typed_settings()` (install `britecore_sdk[typed-config]`); Dynaconf remains the runtime source of truth.

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

- When changing `docs/` content or root Markdown files included via docs wrappers, run a strict
  Sphinx build because `.readthedocs.yml` is configured with `fail_on_warning: true`:

```powershell
python -m sphinx -W --keep-going -b html .\docs .\docs\_build\html-strict
```

```bash
python -m sphinx -W --keep-going -b html ./docs ./docs/_build/html-strict
```

## Logging

- Logger is exposed as `britecore_sdk.logger` (standard Python `logging.Logger`).
- Use `logger.info()`, `logger.debug()`, `logger.error()`, etc. for logging.
- SDK import does not configure root/global logging; the default package logger uses a `NullHandler`.
- Use `britecore_sdk.configure_logging(...)` when you want SDK-managed console/file handlers.
- Library users can configure logging via standard Python logging mechanisms:

```python
import logging
logging.getLogger("britecore_sdk").setLevel(logging.DEBUG)  # Module-level control
logging.basicConfig(level=logging.INFO)  # Global config
```

- Don't create new logger instances in modules; use the package logger or `logging.getLogger(__name__)`.

## Pre-commit hooks and quality gates

**Pre-commit framework** (`pre-commit.com`) runs automated checks before commits/pushes. This is MANDATORY for preventing CI failures.

### Setup (first time only)

```bash
pip install pre-commit
pre-commit install
```

### What runs automatically on `git commit`

All hooks defined in `.pre-commit-config.yaml`:

1. **Code linters** (ruff, black) — code style and import ordering
2. **Type checker** (mypy) — type errors in key modules
3. **Unit smoke tests** (pytest) — quick validation before commit
4. **Markdown linter** (pymarkdown) — markdown syntax
5. **Markdown structure** — custom validation of headings, links, tables
6. **Sphinx documentation build** — build docs in strict mode (`-W`)

### What runs on `git push`

- **Release compliance check** — validates LICENSE, metadata, and legal docs

### Preventing the documentation build failures

The Sphinx hook validates documentation builds **before you commit**, matching the RTD `-W --keep-going` flags:

```bash
python -m sphinx -W --keep-going -b html ./docs ./docs/_build/html-strict
```

If this fails locally, it **will also fail in CI**. The solution is **always** visible in the pre-commit output. Common issues:

- Adjacent transitions (`---` markers too close together)
- Invalid MyST substitutions or syntax
- Malformed markdown tables
- Unknown Sphinx directives

See `docs/DOCUMENTATION_BUILD_TROUBLESHOOTING.md` for detailed remedies.

### Manual invocation (for debugging)

```bash
# Test all hooks on all files
pre-commit run --all-files

# Test specific hook
pre-commit run sphinx-build --all-files --verbose

# Dry run (no changes)
pre-commit run --all-files --dry-run
```

### Bypass (only when absolutely necessary)

```bash
git commit --no-verify  # Skip hooks for this commit ONLY
git push --no-verify    # Skip pre-push hooks ONLY
```

**Note:** Bypassing pre-commit leads to CI failures. If you bypass, you are responsible for fixing CI failures before merge.

## Gotchas that affect agent changes

- API client initialization is now lazy: `api_client` is a proxy that initializes on first use, avoiding failures in contexts without config/env. Call `get_api_client()` for explicit control.
- `init_client()` returns `Self` — one-liner `client = BritecoreAPIClient("site").init_client()` is valid and preferred in examples.
- `BritecoreAPIClient` supports the context-manager protocol (`__enter__`/`__exit__`); prefer `with` blocks in examples that need clean teardown.
- `reset_api_client()` (from `api.api_calls`) clears the module-level client; use it in tests for site isolation instead of monkeypatching globals.
- `do_request(...)` accepts `dry_run=True` (part of `RequestParameters`) — logs request details without sending. Document this in any debugging section.
- Flat exception aliases are exported from `britecore_sdk.exceptions` and the top-level package (`NotFoundError`, `AuthenticationError`, etc.). Prefer these in new example code; the nested `BritecoreError.X` form still works.
- Every outbound request carries an `X-SDK-Request-ID` header (short hex correlation ID). The same ID appears in `[req_id] → METHOD /path` debug log lines.
- `process_result(...)` expects JSON responses shaped like `{success, data, message/messages}`; some supported v1 wrappers with no v2 equivalent may parse raw payloads directly.
- Keep public exports updated via `__all__` in package `__init__.py` files when adding new top-level functionality.
- CLI entry points (`britecore-healthcheck`, `britecore-check-config`, `britecore-run-checks`) are registered in `pyproject.toml [project.scripts]`; re-run `pip install -e .` after adding new ones.
