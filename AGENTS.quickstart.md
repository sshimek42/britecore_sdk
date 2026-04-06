# AGENTS Quickstart

For full guidance, see `AGENTS.md`.

- Work in `src/britecore_libraries/`; ignore `build/`, `dist/`, `env/`, and `*.egg-info/` unless packaging is the task.
- API client initialization is now lazy: `api_client` (from `api.api_calls`) is a proxy that initializes on first use. Call `get_api_client()` for explicit init.
- `target_site` must be set (or passed) for `BritecoreAPIClient.init_client()`; missing site raises `NoSiteError`.
- Auth auto-selects: API key mode if `client_id`/`client_secret` are blank; otherwise OAuth token flow (`/api/auth/oauth2/token`).
- Endpoint wrappers should follow v2 pattern: build payload -> `API_CLIENT.do_request(...)` -> `API_CLIENT.process_result(...)`.
- Use `RequestParameters` + `**kwargs: Unpack[RequestParameters]` for timeout/retry/header overrides.
- `process_result(...)` expects `{success, data, message/messages}` JSON; some v1 modules parse raw payloads differently.
- Keep endpoint modules under `api/api_calls/v1` or `api/api_calls/v2` (prefer v2 for new work).
- Config comes from Dynaconf in `config/.secrets.toml` + `config/settings.toml`; validated site keys include `base_url`, `client_id`, `client_secret`, `api_key`.
- Important env vars in code paths: `target_site` (client init) and `system` (regex selection in maps, with sensible defaults if unset).
- Prefer imports from `models`/`validators`; `classes` is a deprecated compatibility shim.
- Tests are under `tests/` (not `src/`); run targeted pytest for changed modules, then focused import/smoke checks when config-sensitive paths are involved.
