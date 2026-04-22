# AGENTS Quickstart

For full guidance, see `AGENTS.md`.

- Work in `src/britecore_sdk/`; ignore `build/`, `dist/`, `env/`, and `*.egg-info/` unless packaging is the task.
- API client initialization is now lazy: `api_client` (from `api.api_calls`) is a proxy that initializes on first use. Call `get_api_client()` for explicit init.
- `init_client()` returns `Self` — one-liner `client = BritecoreAPIClient("site").init_client()` is valid. `BritecoreAPIClient` also supports context manager (`with`) for clean teardown.
- `target_site` must be set (or passed) for `BritecoreAPIClient.init_client()`; missing site raises a configuration error.
- Auth auto-selects: API key mode if `client_id`/`client_secret` are blank; otherwise OAuth token flow (`/api/auth/oauth2/token`).
- Endpoint wrappers should follow v2 pattern: build payload -> `API_CLIENT.do_request(...)` -> `API_CLIENT.process_result(...)`.
- Use `RequestParameters` + `**kwargs: Unpack[RequestParameters]` for timeout/retry/header overrides. `dry_run=True` is part of `RequestParameters` — logs request without sending.
- `process_result(...)` expects `{success, data, message/messages}` JSON; some supported v1 wrappers parse raw payloads differently.
- Keep endpoint modules under `api/api_calls/v2`; supported v1 wrappers remain where no v2 equivalent exists.
- Config comes from Dynaconf in `src/britecore_sdk/settings/.secrets.toml` + `src/britecore_sdk/settings/settings.toml`; validated site keys include `base_url`, `client_id`, `client_secret`, `api_key`.
- Important env vars in code paths: `target_site` (client init) and `system` (regex selection in maps, with sensible defaults if unset).
- Prefer imports from `models`/`validators`; `classes` import paths are removed.
- Flat exception aliases: `from britecore_sdk import NotFoundError, AuthenticationError` etc. — use these in new example code.
- `reset_api_client()` clears the module-level client — use in tests for isolation instead of patching globals.
- CLI entry points registered in `pyproject.toml`: `britecore-healthcheck`, `britecore-check-config`, `britecore-run-checks`.
- Tests are under `tests/` (not `src/`); run targeted pytest for changed modules, then focused import/smoke checks when config-sensitive paths are involved.

## Repo layout contract

- Edit authored code in `src/britecore_sdk/` and tests in `tests/`; avoid direct edits in generated paths like `build/`, `dist/`, `.venv/`, `htmlcov/`, and `docs/_build/`.
- Keep root docs as canonical when mirrored by docs includes (currently `PYTHON_COMPATIBILITY.md` and `UNIMPLEMENTED_API_STUBS.md`), and let `docs/*.md` include those files.
- Keep dependency/version definitions in `pyproject.toml` as the single source of truth.
