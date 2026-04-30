# Changelog

All notable changes to `britecore_sdk` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

---

## [1.4.0] — 2026-04-30

### Added

- New workflow batch helper modules for contacts and policies/risks:
  - `britecore_sdk.api.workflows.batch_contacts`
  - `britecore_sdk.api.workflows.async_batch_contacts`
  - `britecore_sdk.api.workflows.batch_policies`
  - `britecore_sdk.api.workflows.async_batch_policies`
- New client convenience methods for workflow batch operations:
  - `BritecoreAPIClient.create_contacts_batch(...)`
  - `BritecoreAPIClient.create_policies_batch(...)`
  - `BritecoreAPIClient.create_risks_batch(...)`
  - `AsyncBritecoreAPIClient.acreate_contacts_batch(...)`
  - `AsyncBritecoreAPIClient.acreate_policies_batch(...)`
  - `AsyncBritecoreAPIClient.acreate_risks_batch(...)`
- Typed batch result contracts are now reusable across sync/async modules:
  `BatchContactCreateResult`, `BatchPolicyCreateResult`,
  `BatchRiskCreateResult`, and `BatchQuoteCreateResult`.

### Changed

- Batch workflow helpers are now consistently housed under
  `britecore_sdk.api.workflows` (quotes, contacts, policies, and risks).
- `britecore_sdk.api.api_calls.v2` continues to re-export batch helpers for
  backwards compatibility, while single-item endpoint wrappers remain in domain
  modules.
- Documentation and tests now reference workflow-first imports for batch helper
  usage.

---

## [1.3.1] — 2026-04-29

### Added

- Rate limiter options now available in `init_api_client()` for feature parity with `init_client()`:
  - `enable_rate_limiter` (bool)
  - `rate_limiter_requests_per_second` (float)
  - `rate_limiter_burst_size` (int)
  - `rate_limiter_adaptive_backoff` (bool)
  - `rate_limiter_backoff_timeout_seconds` (float)

### Fixed

- Updated `BritecoreAPIClient.process_result()` to properly support instance method calls
  (changed from classmethod to instance method to support rate limiter state updates).
  All existing tests updated to reflect this change.
- Added defensive `getattr()` check for `rate_limiter` attribute to handle clients
  created via `__new__` that bypass `__init__`.

---

## [1.3.0] — 2026-04-28

### Added

- **Client-side token bucket rate limiter** — optional rate limiting integrated into
  `BritecoreAPIClient` to throttle requests at configurable rates (default: 10 req/s,
  20-request burst):
  - Per-client instance (independent limits per site/environment).
  - Opt-in via `enable_rate_limiter=True` in `init_client()`.
  - Configurable via `rate_limiter_*` parameters or `settings.toml`.
  - Adaptive backoff on HTTP 429 responses (respects `Retry-After` header).
  - Integrated into `do_request()` with optional per-call bypass via `rate_limiter_bypass=True`.
  - Full unit test coverage and `docs/RATE_LIMITING.md` guide.
  - Examples in `examples/rate_limiting_example.py`.

- **Batch quote creation functions** — high-throughput quote generation:
  - Sync: `create_full_quotes_batch(quotes, max_workers=5, fail_fast=False)`.
  - Async: `acreate_full_quotes_batch(quotes, max_concurrent=5, fail_fast=False)`.
  - Configurable parallelism and fail-fast mode.
  - Per-item result tracking with summary statistics.
  - Full unit test coverage and `docs/BATCH_QUOTE_CREATION.md` guide.
  - Examples in `examples/batch_quote_creation.py`.

- **Comprehensive error logging** — `BritecoreAPIClient.init_client()` now logs:
  - ERROR level for all configuration validation failures (missing base_url, api_key, OAuth errors, rate limiter config errors).
  - INFO level on successful initialization showing auth mode and rate limiting status.
  - DEBUG level throughout configuration discovery and authentication selection.
  - Stack traces (`exc_info=True`) for easier troubleshooting in logs/APM systems.

- `use_api_client(client)` context manager in `api.api_calls` to bind
  endpoint wrapper calls to an explicit `BritecoreAPIClient` instance without
  mutating module-global client state.
- Top-level `britecore_sdk.use_api_client` export for convenience.
- Multi-site and operations documentation:
  `docs/MULTI_TENANCY.md`, `docs/OBSERVABILITY.md`, `docs/DEPLOYMENT.md`, and
  `DEPRECATION.md`.

### Changed

- Updated examples and guides to demonstrate explicit per-site client binding
  for multi-tenant workflows.

---

## [1.1.2] — 2026-04-27

### Added

- `check_site_configs` now supports `--json` output for CI/tooling, including
  config source precedence, resolved settings files, active config paths,
  warnings, and per-site validation results.
- New regression coverage for package-root logging exports and config
  diagnostics JSON/table behavior (`tests/unit/test_package_exports.py`,
  `tests/unit/test_base_logger.py`, `tests/utils/test_check_site_configs.py`).
- **10 quality-of-life enhancements** to the SDK core:
  1. `BritecoreAPIClient` context manager (`__enter__`/`__exit__`) — auto-closes
     the `urllib3.PoolManager` on exit (`with BritecoreAPIClient("site").init_client() as client:`).
  2. `reset_api_client()` in `api.api_calls` — clears module-level client for
     test isolation or multi-site swapping.
  3. `BritecoreAPIClient.__repr__` — shows `site`, `base_url`, `auth` mode,
     and `initialized` state for easy REPL/log debugging.
  4. `HealthcheckResult.__bool__` — enables `if result:` / `if not result:`
     idioms without accessing `.ok`.
  5. Flat exception aliases exported from `britecore_sdk.exceptions` (e.g.
     `from britecore_sdk import NotFoundError`) and from the top-level package
     (`AuthenticationError`, `ConfigurationError`, `NotFoundError`,
     `RateLimitError`, `RequestTimeoutError`, `ServerError`, `ValidationError`).
  6. Dry-run improvements — per-call `dry_run=True` and client-level
     `init_api_client(client_dry_run=True)` / `init_client(client_dry_run=True)`
     now return a synthetic successful payload without sending, include redacted
     request headers by default, and skip OAuth token acquisition unless caller
     headers are explicitly supplied.
     Async parity is now included via `init_async_api_client(client_dry_run=True)`
     and async wrapper/request support, with async dry-run bypassing cache reads,
     cache writes, and in-flight dedupe.
  7. `X-SDK-Request-ID` header — every outbound request carries a short
     correlation ID (already visible in `[req_id] → METHOD /path` debug logs)
     and now also propagates it as an HTTP header to the server.
  8. `zip_code_lookup.load_zip_codes` — documented thread-pool safety for use
     with `AsyncBritecoreAPIClient` (call via `run_in_executor`).
  9. CLI entry points registered in `pyproject.toml` — `britecore-healthcheck`,
     `britecore-check-config`, and `britecore-run-checks` are now installable
     shell commands.
  10. `BritecoreAPIClient.init_client()` returns `Self` — enables one-liner
      fluent initialization (`client = BritecoreAPIClient("site").init_client()`).
- `tests/unit/test_api_spec_alignment.py` — validates wrapper paths against
  the canonical `api_specs/current/britecore.json` specification.
- `tests/unit/test_v1_endpoint_routing.py` — unit tests for v1 custom_ui,
  payments, and printing endpoints.
- `tests/unit/test_zip_code_lookup.py` — tests for US zip code lookup utility.
- `examples/basic_api_usage.py` — runnable example demonstrating OAuth and
  API key initialization flows.

### Removed

- Removed `utils/britecore_odbc.py` (pyodbc wrapper) and `utils/britecore_selenium.py`
  (Selenium wrapper) — database connectivity and browser automation are out of scope
  for an API client library. Consumers requiring these capabilities should use
  `pyodbc` and `selenium` directly.
- Removed `utils/check_odbc_settings.py` helper script (no longer needed).
- Removed `database` and `browser` optional dependency extras from `pyproject.toml`.
- Removed `BritecoreError.DatabaseConnectionError` exception (only used by the removed
  ODBC wrapper).
- Removed `load_database_config` from `config/config.py`.
- Removed Selenium config keys (`web_retry`, `web_timeout`, `web_timeout_long`,
  `web_browser`) and ODBC config keys (`db_conn_string`, `db_conn_options`) from
  `LoadClientSettings.load_config`.

### Changed

- **Configuration loading and init ergonomics:**
  - Layered file discovery is now explicit and documented: SDK defaults →
    `~/.britecore` → CWD (`britecore.toml`, `.britecore_secrets.toml`) →
    `BRITECORE_SDK_SETTINGS_FILE`, with `BRITECORE_SDK_*` env vars highest.
  - `init_api_client(...)`, `init_async_api_client(...)`, and
    `BritecoreAPIClient.init_client(...)` support explicit inline credentials
    (`base_url`, `api_key`, `client_id`, `client_secret`) that bypass file lookup.
  - `target_site` guidance is normalized across docs: required for standard
    file/env init, optional in explicit `base_url` mode.
- **Logging contract refinements:**
  - Package import now uses a library-safe default logger (`NullHandler`,
    no root/global logging configuration).
  - Added opt-in `configure_logging(...)` for SDK-managed stream/file handlers
    and documented app-owned vs SDK-managed logging patterns.
- **Code quality improvements:**
  - Reduced cyclomatic complexity in `BritecoreAPIClient.process_result` by
    extracting helper methods (`_raise_for_http_status`, `_load_json_payload`,
    `_extract_success_data`).
  - Converted logging f-strings to lazy `%s` formatting in API modules,
    validators, and utilities (DeepSource PYL-W1203).
  - Collapsed nested `with` statements in tests (PTC-W0062).
  - Removed Python built-in shadowing (`type` → `note_type`, `type` →
    `payment_method_type`) and standardized wrapper kwargs.
- **Documentation polish:**
  - Added `api_specs/README.md` and normalized checked-in API spec layout to
    `api_specs/current/` and `api_specs/legacy/`.
  - Split archived specs into `api_specs/legacy/britecore/` and
    `api_specs/legacy/third_party/` for clearer ownership and scope.
  - Removed placeholder credential examples from `SECURITY.md` and
    `TROUBLESHOOTING.md` to avoid false positives from secrets scanners.
  - Unified private security contact wording in `SECURITY.md`.
  - Expanded `AGENTS.md` and `CONTRIBUTING.md` with repo layout contract
    guidance.
  - Repository About section configured with comprehensive topic tags and
    professional description.
- **Configuration:**
  - `.deepsource.toml` expanded to exclude test directories and increased
    `max_line_length` to 120 for practical line-length requirements.
  - ODBC utilities now require explicit `target_site` for config-backed
    DB resolution (`get_cursor(..., target_site="...")`); no implicit site
    resolution is used for DB config lookup.
  - Selenium utility now reads flat Dynaconf keys (`web_retry`,
    `web_timeout`, `web_timeout_long`, `web_browser`, `web_user`, `web_pass`),
    and `get_driver(browser=...)` explicitly overrides configured
    `web_browser` with validation for supported browser names.
  - Project documentation updated (`README.md`, `GETTING_STARTED.md`,
    `docs/CONFIGURATION.md`, `TROUBLESHOOTING.md`, `ARCHITECTURE.md`) to
    reflect optional utility settings and updated ODBC/Selenium behavior.

### Fixed

- Removed `"settings/*.toml"` from `pyproject.toml` package-data — those files
  are in `.gitignore` and must not be bundled with the distributed package.
  Tests that assumed SDK defaults always exist are now CI-safe (they check for
  file presence before asserting, so they pass both locally and in CI).
- `python -m britecore_sdk.utils.check_site_configs --json` now correctly emits
  JSON in module execution mode (instead of falling back to table output).
- MyPy `TypedDict` compatibility in `payments.py` via explicit casting for
  standardized kwargs handling.
- DeepSource findings (D202, W1203, PTC-W0048, PTC-W0062, PY-R1000,
  PY-D0003, E1121) addressed via targeted refactoring and configuration.
- Markdown lint formatting (MD012, MD031, MD032, MD040, MD060) across all
  docs.
- Added 'toml' as a required dependency in pyproject.toml for Python 3.11+ compatibility. This resolves CI failures due to missing toml when running utility scripts and tests that require it.

---

## [1.1.0] — 2026-04-06

### Added

- `src/britecore_sdk/py.typed` marker (PEP 561) — downstream mypy users
  now get inline type information automatically.
- `src/britecore_sdk/api/types.py` — shared `TypedDict` response shapes
  (`BritecoreResponse`, `PolicyData`, `ContactData`, `QuoteData`,
  `InvoiceData`, `RevisionData`, `AddressData`, `PhoneData`, `EmailData`).
- `get_api_client` and `get_async_api_client` are now exported from the
  top-level `britecore_sdk` namespace.
- v2 `__init__.py` now re-exports all 30 sync domain modules so IDEs can
  discover them via `from britecore_sdk.api.api_calls.v2 import <module>`.
- Full implementations for all previously-stubbed v2 API domains:
  `attachments` (11), `custom_ui` (4), `dashboards` (8), `data` (2),
  `errors` (1), `intacct` (5), `nightly_jobs` (4), `notifications` (2),
  `printing` (5), `return_premium` (1), `search` (2), `settings` (11),
  `signatures` (6), `uploads` (1), `vendors` (16) — **374/374 endpoints
  now covered**.
- `tests/unit/test_v2_new_endpoints.py` — parametrized unit tests for all
  newly implemented domain modules.
- `tests/unit/test_logging_tokens.py` — regression tests that assert no
  SCLogging color-format tokens remain in the source tree and that
  runtime log output is plain text.
- CI workflow (`.github/workflows/ci.yml`) now covers Python 3.11–3.14,
  runs ruff, black, mypy, and pytest with a 60% coverage gate.
- `docs/MAP_FILES.md` — policy and sample structures for sensitive
  `*_map.py` files that must not be committed to version control.
- `maps/__init__.py` map export pattern: `britecore_sdk.maps`
  re-exports `agency`, `policy_map`, `britecore_policy_type_map`,
  `field_map_to_britecore`, `field_map_to_named_insured`, and
  `field_map_to_risk_location`.

### Changed

- `pyodbc`, `selenium`, and `pyinputplus` moved from hard dependencies to
  optional extras (`[database]`, `[browser]`, `[interactive]`). Existing
  consumers who use these utilities should add the relevant extra:
  `pip install "britecore_sdk[database]"`.
- **`sclogging` dependency removed.** `base_logger.py` has been rewritten
  to use Python's built-in `logging` module. The `SCLogger` singleton class
  is gone; `get_logger()` now returns a standard `logging.Logger` directly.
  `britecore_odbc` and `britecore_selenium` have been updated to use the
  package-level logger instead.
- SCLogging color-format escape tokens (e.g. `%f.yellow%…%f%`) removed from
  all log-message strings across `contacts`, `async_contacts`, `deliverables`,
  `insured`, `lines`, `policies`, `async_policies`, `v1/printing`, and
  `address_validator`. Log output is now plain text and compatible with any
  standard Python logging handler.
- Private map files (`britecore_agency_map.py`, `britecore_field_map.py`,
  `britecore_policy_map.py`, `britecore_policy_name_map.py`) removed from
  git tracking. `.gitignore` pattern `maps/*_map.py` prevents accidental
  re-addition.
- Documentation dependencies now constrain `sphinx` to `>=8.2.3,<9.1` so the
  `docs` extra remains resolvable on Python 3.11, matching the supported
  project floor and CI verification range.
- `__version__` is now resolved at runtime via `importlib.metadata` so
  `pyproject.toml` remains the single source of truth.
- `vendors.get_wtw_score`: renamed parameter `property` → `property_descriptor`
  to avoid shadowing the Python built-in. The JSON request key remains
  `"property"` for API compatibility.
- CI coverage threshold raised from 25 % to 60 %.

### Fixed

- `UNIMPLEMENTED_API_STUBS.md` and `API_COVERAGE_ANALYSIS.md` updated to
  reflect 100 % endpoint coverage.

---

## [1.0.0] — 2026-03-26

### Added

- Initial public release.
- Complete v2 wrappers for: `accounting`, `billing`, `claims`,
  `commissions`, `contacts`, `deliverables`, `inspections`, `insured`,
  `lines`, `notes`, `payments`, `policies`, `quotes`, `reports`, `utils`.
- Async cache-aware wrappers (`async_contacts`, `async_policies`,
  `async_quotes`).
- Domain models: `BritecoreContact`, `BritecorePolicy`, `BritecoreQuote`.
- Validators: `AddressValidator`, `EmailValidator`, `NameValidator`,
  `PhoneValidator`.
- Dynaconf-based configuration with API-key and OAuth2 auth modes.
- Lazy `_LazyAPIClient` proxy to avoid import-time failures when config
  is absent.
- Singleton logger via `sclogging`.
- `BritecoreError` exception hierarchy.
- Comprehensive unit test suite (236 tests).
