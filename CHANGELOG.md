# Changelog

All notable changes to `britecore_sdk` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added

- Planned for `2.4.7`: add an error-hint layer that attaches actionable remediation guidance to common configuration/authentication failures.

- Planned for `2.4.7`: add a lightweight `britecore-quick-check` CLI mode set (`--syntax`, `--connectivity`, `--full`) for one-command environment readiness checks.

- Planned for `2.4.7`: add response helper utilities for common API payload patterns (data extraction, pagination envelopes, and batch result normalization).

### Changed

- Planned for `2.4.7`: expand structured logging categories to make auth, HTTP, rate-limit, cache, and configuration events easier to filter in production logs.

- Planned for `2.4.7`: add request-timing observability hooks to surface slow endpoints and improve performance triage.

### Fixed

- Planned for `2.4.7`: remove remaining high-confidence `type: ignore` suppressions by tightening type signatures and overload coverage in shared API entry points.

### Deprecated

- Planned for `2.4.7`: implicit wrapper client fallback (calling wrappers without explicit `client=` and relying on module-level client state). Use explicit `client=` or `use_api_client(...)`. Planned removal in `v3.0.0`.

- Planned for `2.4.7`: global client lifecycle helpers as the primary usage pattern (`init_api_client(...)`, `init_async_api_client(...)`, `reset_api_client()`) in favor of explicit client construction and scoped client passing. Planned removal in `v3.0.0`.

- Planned for `2.4.7`: legacy batch result alias keys (`quote_id`/`quote_data`, `contact_id`/`contact_data`) in favor of canonical `id`/`data` keys. Planned removal in `v3.0.0`.

---

## [2.4.6] - 2026-09-02

### Added

- Added first-class payload models for `BritecorePaymentMethod`, `BritecoreVehicle`, `BritecoreCoverage`, `BritecoreDriver`, and `BritecoreLineDefinition`.

- Added claim mapper support for named insured handling as a contact-role mapping (`named_insured`) via `src/britecore_sdk/mappers/claims.py`.

### Changed

- Extended v2 wrappers and claim-related wrappers to accept model-like payload objects that expose `to_dict()`, including list payload coercion support where applicable.

- Exposed new data-layer helpers for script-first payload normalization: `normalize_payment_method_payload`, `normalize_vehicle_payload`, `normalize_coverage_payload`, `normalize_driver_payload`, and `normalize_line_definition_payload`.

### Fixed

- Hardened `britecore-normalize-json` to avoid clear-text payload output to stdout; normalization mode now requires `--output` for payload writes while schema output remains stdout-safe.

- Updated example scripts to avoid printing raw payload bodies and instead emit summary-safe output.

### Deprecated

---

## [2.4.5] - 2026-09-01

### Added

- Added configurable write-safety controls to the sync client request pipeline using middleware (`write_policy=allow|warn|block`), including `ReadOnlyViolation` for blocked write attempts.

- Added `AuditMiddleware` support with config-driven enablement and optional callback/log-level tuning to emit structured request audit events.

- Added a script-first `britecore_sdk.data_layer` module exposing standalone normalization helpers for contact, policy, and quote payload shaping without API transport setup.

- Added a new normalization CLI command `britecore-normalize-json` (and `scripts/normalize_json.py` wrapper) for file-based payload normalization, including `--schema` introspection mode.

### Changed

- Integrated request/response/error middleware hooks into `BritecoreAPIClient.do_request(...)`, centralizing guardrails and observability behavior.

- Extended configuration surfaces (`settings` loaders, defaults, sample settings) to include write-policy and audit middleware options.

- Updated user-facing documentation across README/API/getting-started/configuration/observability guides to document write guard, audit middleware, and script-only data layer workflows.

### Fixed

- Added focused unit coverage for new exception formatting branches, lazy package export/error paths, and configuration loader branches that were previously under-covered in patch coverage checks.

### Deprecated

---

## [2.4.4] - 2026-08-26

### Added

### Changed

### Fixed

- Corrected the report-download HTTP-status validation to use the supported public client API instead of a protected helper, avoiding the `PYL-W0212` lint warning while preserving the regression fix for 4xx/5xx error handling.
- Kept the regression test coverage for the 500-error response case in `tests/unit/test_v2_reports_download_parsing.py`.

### Deprecated

---

## [2.4.3] - 2026-08-26

### Added

### Changed

### Fixed

- Fixed a regression in `download_report_file(...)` in `src/britecore_sdk/api/api_calls/v2/reports.py` where HTTP 4xx/5xx responses were being treated as valid report payloads instead of raising the normal SDK exception flow.
- Added a focused regression test in `tests/unit/test_v2_reports_download_parsing.py` covering the 500-error response case.

### Deprecated

---

## [2.4.2] - 2026-08-03

### Added

### Changed

- Updated line export wrappers in `src/britecore_sdk/api/api_calls/v2/lines.py` and `src/britecore_sdk/api/api_calls/v2/async_lines.py` to accept explicit `curr_eff_date_id`, `curr_state_id`, and `curr_line_id` keyword arguments while preserving tuple-based compatibility input.

- Added compatibility alias helpers `get_line_export(...)` and `aget_line_export(...)` for callers using prior line-export call patterns.

- Extended selected wrappers to support doc-accurate argument aliases while preserving existing SDK aliases: `type` for payment method payloads in `src/britecore_sdk/api/api_calls/v2/payments.py`, and `id` for search index operations in `src/britecore_sdk/api/api_calls/v2/search.py`.

- Updated `get_contacts_by_ids(...)` in `src/britecore_sdk/api/api_calls/v2/contacts.py` to accept either a list of contact IDs or a comma-separated contact ID string.

### Fixed

- Added and updated unit tests in `tests/unit/test_interactive_menu.py`, `tests/unit/test_v2_coverage_gaps.py`, and `tests/unit/test_v2_new_endpoints.py` to validate backward-compatible input shapes and argument normalization.

### Deprecated

---

## [2.4.1] - 2026-07-30

### Added

### Changed

- Updated `download_report_file(...)` in `src/britecore_sdk/api/api_calls/v2/reports.py` to decode file responses directly instead of routing binary payloads through JSON parsing.

- Kept `download_report_file_decoded(...)` as a compatibility alias for callers that prefer an explicit decoded-file helper.

### Fixed

- Prevented `download_report_file(...)` from raising `NoDataReturned` on gzip/zip/raw binary report responses that are not valid JSON.

### Deprecated

---

## [2.4.0] - 2026-07-30

### Added

- Added `download_report_file_decoded(...)` and `parse_report_file_content(...)` in `src/britecore_sdk/api/api_calls/v2/reports.py` to safely decode JSON, gzip, zip, and raw binary report downloads.

- Added a `parameters` payload field to `run_report(...)` in `src/britecore_sdk/api/api_calls/v2/reports.py` for APIs that require parameterized report execution.

- Added a dedicated unit test module `tests/unit/test_v2_reports_download_parsing.py` covering JSON/gzip/zip/raw-bytes report decoding behavior.

### Changed

- Standardized multiple v2 wrappers (`accounting`, `claims`, `insured`, `lines`, `notes`, `policies`, `reports`) to send explicit `method="POST"` and pass the endpoint path into `process_result(...)` for consistent request/exception context.

- Added `search_policies(...)` to `src/britecore_sdk/api/api_calls/v2/policies.py` and updated policy-list helpers to reuse the shared search implementation.

### Fixed

- Added a compatibility fallback in `BritecoreAPIClient._parse_response_payload(...)` to accept legacy single-quoted Python-literal dict/list payloads when valid JSON decoding fails.

- Updated report wrappers that return file content to avoid JSON-only parsing assumptions and correctly handle binary responses.

### Deprecated

---

## [2.3.1] - 2026-07-27

### Added

### Changed

- Updated `alist_quotes(...)` typing to use `RequestParameters` and made placeholder pagination/client arguments intentionally consumed while quote-list endpoint support remains unavailable.

- Added compatibility notes in autogenerated wrapper sections to document why select API-shaped parameter names are preserved.

### Fixed

- Reworked async HTTP helper internals in `AsyncBritecoreAPIClient` to use class-qualified helper calls for header detection, timeout normalization, and dry-run body sanitization, eliminating protected-member lint findings without behavior changes.

- Added targeted lint suppressions on selected autogenerated wrappers that intentionally preserve API field names conflicting with Python built-ins (for keyword-call compatibility).

### Deprecated

---

## [2.3.0] - 2026-07-27

### Added

- Added `normalize_contact_search_results(...)` in `src/britecore_sdk/api/workflows/contact_search_normalization.py` to normalize common contact-search response envelopes to `list[dict]`.

- Added typed workflow result model `BatchItemResult` and legacy conversion helpers (`to_legacy_quote_result`, `to_legacy_contact_result`) in `src/britecore_sdk/models/workflow_results.py`.

### Changed

- Standardized sync and async quote/contact batch workflow result items around strict keys: `index`, `success`, `id`, `data`, `error`, and `error_type`.

- Added compatibility aliases to quote/contact batch result items by default (`quote_id`/`quote_data`, `contact_id`/`contact_data`) with opt-out via `include_legacy_keys=False`.

- Added explicit `client=` support across staged and batch workflow helpers (sync + async) and supporting endpoint wrappers (`new_contact`/`anew_contact`, `create_policy`/`acreate_policy`, `create_risk`/`acreate_risk`, `create_full_quote`/`acreate_full_quote`).

- Updated sync/async client batch convenience methods to expose `include_legacy_keys` and `client` passthrough parameters.

- Added a README migration note documenting canonical batch keys (`id`/`data`/`error_type`), compatibility aliases, and `include_legacy_keys=False` opt-out guidance for importer consumers.

### Fixed

### Deprecated

---

## [2.2.0] - 2026-07-24

### Added

- **Optional native async HTTP transport** — `AsyncBritecoreAPIClient` now accepts
  `async_transport="httpx"` (default: `"threaded"`). When set to `"httpx"`, requests
  are executed natively via `httpx.AsyncClient` instead of wrapping the sync client in
  `asyncio.to_thread`. An optional `httpx_client` kwarg allows injecting a pre-built
  client (e.g., for shared connection pools or testing). Install the new optional extra
  to enable: `pip install britecore_sdk[async-http]`.

- **Optional pydantic-validated settings view** — `get_typed_settings(site_names=[...])`
  is now exported from `britecore_sdk.settings`. It returns a strongly-typed pydantic
  model built from the live Dynaconf config, providing IDE autocompletion and runtime
  field validation without changing SDK initialization behavior. Requires:
  `pip install britecore_sdk[typed-config]`.

- **New `toml_compat` wrapper** (`britecore_sdk.utils.toml_compat`) — thin adapter that
  exposes a `toml`-like API (`load` / `dump` / `loads` / `dumps`) backed by stdlib
  `tomllib` for parsing and `tomli-w` for serialization. Internal SDK utilities now use
  this wrapper, removing the dependency on the untyped `toml` package.

- **New optional dependency extras** in `pyproject.toml`:
  - `britecore_sdk[async-http]` — pulls in `httpx` for native async transport.
  - `britecore_sdk[typed-config]` — pulls in `pydantic` and `pydantic-settings`.
  - `britecore_sdk[all]` — now includes both new extras in addition to `interactive`.

### Changed

- **Removed `typing-extensions` from core runtime dependencies** — the project targets
  Python `>=3.11`, where `TypedDict` is part of stdlib `typing`. The only consumer
  (`api/types.py`) now imports from `typing` directly.

- **Replaced `toml` with `tomli-w`** in core runtime dependencies. `tomllib` (stdlib
  since Python 3.11) handles parsing; `tomli-w` provides the write path.
  If `tomli-w` is unavailable at runtime the wrapper transparently falls back to `toml`
  (backward compatible, no hard breakage).

### Migration notes

**`toml` → `tomli-w` (write path)**

No action required for most consumers. The internal TOML I/O used by config utilities
is fully backward-compatible. If you import `toml` from `check_site_configs.py` or
`_config_common` directly, switch to:

```python
from britecore_sdk.utils.toml_compat import toml
```

**Async transport**

Existing code that uses `AsyncBritecoreAPIClient` is unaffected; the default transport
remains `"threaded"`. To opt into native async I/O:

```python
from britecore_sdk.api import AsyncBritecoreAPIClient

client = AsyncBritecoreAPIClient(target_site="prod", async_transport="httpx")
```

**Typed settings (opt-in)**

```python
from britecore_sdk.settings import get_typed_settings

typed = get_typed_settings(site_names=["prod", "staging"])
print(typed.sites["prod"].base_url)
```

---

## [2.1.1] - 2026-07-23

### Changed

- Completed the v2.1.x quote-wrapper quality pass in `src/britecore_sdk/api/api_calls/v2/quotes.py` by expanding remaining endpoint docstrings to include parameter intent, return behavior, and error semantics.
- Added missing input validation to quote wrappers that accepted required identifiers without guardrails (`associate_agentcy_to_quote`, `prefill_loss_history`, `prefill_violations`, `summary`, `turn_quote_into_application`, and `update_e_delivery_enabled`).
- Continued policy lifecycle quality-of-life improvements in `src/britecore_sdk/api/api_calls/v2/policies.py` for `bind`, `cancel_policy`, `create_policy_from_britequote`, `evaluate_cancellation`, and `submit_quote`.

### Fixed

- Corrected silent validation behavior in policy creation/retrieval paths by ensuring `BritecoreError.MissingParameter` is raised where required parameters are missing.

### Documentation

- Added completion records for the v2.1.x effort:
  - `QUALITY_OF_LIFE_AUDIT_2026-07-23.md`
  - `V2.1.1_SESSION_STATUS_2026-07-23.md`
  - `V2.1.X_COMPLETION_2026-07-23.md`

---

## [2.0.5] - 2026-07-21

### Added

- Added `[project.urls]` metadata in `pyproject.toml` (Homepage, Documentation, Repository, Issues, Changelog) for richer package index/project link display.
- Added a "Project Links" section to `docs/index.md` and `docs/project_overview.md`.

### Changed

- Raised runtime minimums for `dynaconf` and `typing-extensions` in `pyproject.toml`.
- Refreshed dev/docs dependency minimums in `pyproject.toml` while preserving Python 3.11 compatibility (`sphinx>=9.0.4,<9.1`).
- Updated workflow action pins in release/publish workflows to current majors used in this repo (`softprops/action-gh-release@v3`, `actions/download-artifact@v5`).

---

## [2.0.4] - 2026-07-21

### Fixed

- **CI formatting parity**: normalized `tests/unit/test_config_wizard.py` formatting and line endings so local pre-commit and GitHub Actions `black --check` agree across platforms.
- **Release documentation drift**: aligned package version references and metadata dates in actively maintained root docs.

### Changed

- Bumped package version to **2.0.4** in `pyproject.toml`.

---

## [2.0.3] - 2026-07-20

### Added

- **85 new always-on tests** replacing the fully-skipped `test_workflows_integration.py`
  template suite across 10 test classes:
  - `TestPhoneValidatorProperties` (15): format normalization, sentinel rejection (`"0"`, `"-"`),
    all type-map entries (`mobile→Cell`, `business→Work`, `office→Work`, `cellular→Cell`),
    multi-entry list processing
  - `TestEmailValidatorProperties` (12): lowercase normalization, `validate_email()`, type-map
    entries (`home→Personal`, `business→Work`), `InvalidEmailAddress` guard, silent empty-entry skip
  - `TestNameValidatorProperties` (6): apostrophe lowercasing, suffix handling (IV, III, Jr)
  - `TestBritecoreQuoteModel` (6): `to_dict()` field completeness, auto-generated description,
    explicit description preservation, inspection date include/exclude, `underwriting_questions` reset
  - `TestBritecoreContactModel` (5): `process_contact()` name normalization, type defaulting,
    organization type, policy number, key completeness
  - `TestPolicyWorkflows` (3): `retrieve_policy` path routing, payload building, `revision_state`
  - `TestContactWorkflows` (6): `new_contact` path, address/phone/email type normalization,
    `MissingParameter` guards for empty name and empty address list
  - `TestQuoteWorkflows` (6): `create_full_quote` tuple return, path routing, empty/`None` payload
    guards, `None` response `(None, None)` tuple, explicit-client override
  - `TestErrorHandlingWorkflows` (8): exception `status_code` metadata, flat-alias identity,
    `BritecoreError.Base` hierarchy, `request_id`/`error_code` in `__str__`
  - `TestMultiEnvironmentWorkflows` (4): `use_api_client` context manager, `init_api_client`,
    `get_api_client` with autouse mock

### Fixed

- **`test_live_create_quote_round_trip`**: replaced unconditional `pytest.skip()` with a real
  `create_full_quote` → `get_quote` round-trip test, gated on the new
  `BRITECORE_SANDBOX_POLICY_TYPE_ID` env var; preserves skip behaviour when the variable is absent
- **`test_interactive_menu_module_can_be_imported`**: removed catch-all `try/except pytest.skip()`;
  the module uses a lazy proxy (`_LazyAPIClient`) that never requires config at import time
- **black ↔ ruff-format formatting cycle** on `test_endpoints.py`: extracted long assertion
  message into a local variable so the statement fits on one line and both formatters agree
- **`post_probe_report.json` / `post_probe_report.md`**: fixed missing end-of-file newline and
  mixed Windows/Unix line endings

---

## [2.0.2] - 2026-07-20

### Fixed

- **Critical docstring gaps** — Added missing module-level docstring to `src/britecore_sdk/api/api_calls/v1/contacts.py`
- **Documentation quality improvements**:
  - Expanded `src/britecore_sdk/settings/config.py` module docstring from 2 words to comprehensive 18-line documentation explaining the layered configuration system
  - Corrected and expanded `src/britecore_sdk/models/quote.py` module docstring (was incorrectly labeled as "policy model")
- **API reference generation** — Ensures all module-level docstrings are present and properly formatted for Sphinx autodoc and IDE tooltips

### Verified

- All 560+ endpoint wrapper functions have comprehensive Google-style docstrings
- Zero autogenerated wrapper stubs remain without proper documentation
- 100% module-level docstring coverage across core modules
- No regressions; all 90 API module files compile successfully

---

## [2.0.1] - 2026-07-17

### Added

- **POST probe utility** (`src/britecore_sdk/utils/probe_post_requirements.py`): CLI tool that
  sends empty payloads to every undocumented POST endpoint in the OpenAPI spec and infers
  required field names from server validation-error responses.  Supports `--dry-run`,
  `--use-spec-empty-properties`, `--print-selected-paths`, `--export-selected-paths`, and
  `--log-level` flags.  Outputs structured JSON and Markdown reports.
- **Probe regression test generator** (`generate_probe_regression_tests.py`): Script that reads
  `post_probe_report.json` and produces `tests/unit/test_probe_endpoint_regression.py` — 209
  parametrized tests that verify every probe-confirmed wrapper routes to the correct API path.
  Re-run after future probe runs to keep the suite current.
- **Probe endpoint regression tests** (`tests/unit/test_probe_endpoint_regression.py`): 209
  generated path-routing tests covering all `genuine_success` and `informative_error` probe
  results.  No live API required; runs fully mocked in ~1 second.

### Changed

- **136 autogenerated wrapper stubs updated** with probe-discovered required parameters.
  Functions that previously accepted only `**kwargs` now expose named parameters for their
  required fields (e.g. `return_premium_id`, `claim_contact`, `quote_id`).  All new parameters
  default to `None` and are filtered from the payload before sending, preserving backward
  compatibility.
- `claim_exposures.get_accounting_loss_details`, `get_accounting_overview`,
  `get_accounting_recoveries_data`: added `api_key` parameter to match OpenAPI spec.
- `test_autogenerated_wrapper_request_keys_match_spec`: updated to accept probe-discovered and
  manually-curated fields as valid additions to spec-defined keys (spec is intentionally
  incomplete for many endpoints).
- `test_claims_wrapper_requests`: configure `multiple_parameter_verification.return_value` so
  the `get_claim` parametrized case passes under the autouse `mock_api_client` fixture.

### Fixed

- `probe_post_requirements.py`: replaced adjacent `%s%s` logging format tokens that matched
  the legacy SCLogging token regex, resolving `test_no_legacy_logging_tokens_in_source_tree`.

---

## [2.0.0] - 2026-07-17

### Fixed

- `britecore_sdk.api.iterators`: replaced invalid `yield from` inside async generators with explicit `for … yield` to resolve `SyntaxError` that prevented import.

### v2.0.0 Release (✅ COMPLETE - 6/6 Phases)

**Phase 1: Client Lifecycle Redesign (✅ Complete)**

- **Explicit client parameter** now available on all endpoint wrappers for v2.0.0 pattern
- Added `resolve_client()` and `aresolve_client()` helpers

**Phase 2: Typed Response Models (✅ Complete)**

- New `britecore_sdk.api.responses` module with typed dataclasses:
  - `ResponseEnvelope` — Wraps API response metadata
  - `QuoteResponse`, `PolicyResponse`, `ContactResponse` — Domain models
  - `ListResponse` — Generic list wrapper with pagination
  - `BatchOperationResponse` — Batch operation results
- All response models include `.from_api()` factory pattern
- Replaces `Any` returns with type-safe models in endpoint wrappers
- Full IDE autocomplete support
- Raw API payload accessible via `.raw_data` field

**Phase 3: Standardized Error Model (✅ Complete)**

- All exceptions now include structured metadata:
  - `status_code` — HTTP status code (e.g., 404, 500)
  - `error_code` — BriteCore error code (e.g., "quote_not_found")
  - `request_id` — Request correlation ID for debugging
  - `detail` — Alias for human-readable message
  - `raw_payload` — Full server response dict
- `ValidationError` now includes `.validation_errors` dict with field-level errors
- Enhanced exception types:
  - `AuthenticationError` — status 401/403, code "authentication_failed"
  - `NotFoundError` — includes all metadata
  - `RateLimitError` — includes retry_after field
  - `ServerError` — status 500+, code "server_error"
  - `RequestTimeoutError` — status 408, code "request_timeout"
- Backwards compatible — existing exception patterns still work

**Phase 4: Transport Middleware System (✅ Complete)**

- New `britecore_sdk.api.middleware` module:
  - `Middleware` base class with `on_request()`, `on_response()`, `on_error()` hooks
  - `RequestContext` and `ResponseContext` for middleware data flow
  - Built-in middleware:
    - `RequestIdMiddleware` — Automatic X-Request-ID header
    - `LoggingMiddleware` — Request/response logging
    - `HeaderInjectionMiddleware` — Custom header injection
    - `TimeoutMiddleware` — Global timeout configuration
- Client methods: `add_middleware()`, `remove_middleware()`
- Middleware chain executed in registration order
- Extensible for custom logging, tracing (OpenTelemetry), retry logic, etc.

**Phase 5: Pagination Iterators (✅ Complete)**

- New `britecore_sdk.api.iterators` module:
  - `iter_quotes()`, `aiter_quotes()` — Iterate quotes with auto-pagination
  - `iter_policies()`, `aiter_policies()` — Iterate policies
  - `iter_contacts()`, `aiter_contacts()` — Iterate contacts
- Automatic page management (no manual page/limit plumbing)
- Lazy-loading: pages fetched on-demand
- Pythonic async/await support
- Works seamlessly with typed response models

**Phase 6: Legacy Cleanup (✅ Complete)**

- Enhanced `britecore_sdk.classes.__init__.py` with comprehensive deprecation guidance
- New `britecore_sdk.api._compat` module for migration helpers:
  - `get_v2_path()` — Get a direct v2 import path when one exists for a selected wrapper
  - `V1_TO_V2_ROUTING` — Mapping dictionary for selected wrapper-path cleanup cases
  - `import_v1_class_with_warning()` — Load compatibility class aliases with guidance
  - `use_implicit_client_with_warning()` — Guide implicit client users
- Archived v2.0.0 adoption notes: `docs/migrations/V2.0.0-COMPLETE-MIGRATION.md`
  - Historical examples for explicit clients, pagination, error handling, testing, and multi-site usage
  - Adoption checklist for optional modernization work
  - Compatibility notes and common questions
- Deprecated patterns that have true replacements now point to their current equivalents without implying blanket removal of supported `api_calls/v1` wrappers

---

## [1.5.4] - 2026-07-17

### Changed

- Fixed `.github/workflows/docs.yml` validation by moving the Read the Docs hook secret to job-level `env`.
- Tightened packaging dependency metadata:
  - `typing_extensions>=4.15.0,<5.0.0`
  - `toml>=0.10.2,<0.11.0`
  - Kept `setuptools>=83.0.0` in `dev` extras so CI audits run against a non-vulnerable build toolchain.
- Aligned docs packaging requirements with `pyproject.toml`:
  - `docs/requirements.txt` now matches the `docs` extra Sphinx constraint.

### Deprecated

- Implicit module-level client usage (legacy pattern) — Use explicit `client=` parameter
- Manual pagination loop pattern — Use `iter_*()` iterators instead
- Raw dict returns — Use typed response models for better type safety
- `britecore_sdk.classes` module — Import from `models` and `validators` instead

### Documentation

- `V2_ROADMAP.md` — Complete 6-phase roadmap with acceptance criteria
- `docs/migrations/PHASE1-CLIENT-LIFECYCLE.md` — Phase 1 client lifecycle design notes
- `docs/migrations/PHASES2-5-FEATURES.md` — Phases 2-5 comprehensive guide
- `docs/migrations/V2.0.0-COMPLETE-MIGRATION.md` — **Phase 6 archived adoption notes with historical examples and support guidance**
- `V2-PROGRESS-REPORT.md` — v2.0.0 beta readiness status and metrics
- `docs/migrations/PHASES2-5-FEATURES.md` — Phases 2-5 comprehensive guide
- Module docstrings updated with examples for all new features

## [1.5.3] - 2026-07-17

### Changed

- Packaging metadata now marks the project as stable in `pyproject.toml`:
  - `Development Status :: 4 - Beta` -> `Development Status :: 5 - Production/Stable`
- Updated docs to reflect current exception diagnostics and security behavior:
  - `API.md` now documents exception `request_id` and `sanitized_body` fields.
  - `docs/OBSERVABILITY.md` now includes exception-based request correlation examples.
  - `SECURITY.md` now clarifies redacted exception request context via `sanitized_body`.

---

## [1.5.2] - 2026-07-16

- Public-readiness cleanup:
  - Removed tenant-specific docstring examples in `utils/config_manager.py`
    and replaced them with neutral environment naming.
  - Added `.readthedocs.yml` for Read the Docs project builds.
  - Updated docs workflow to optionally trigger Read the Docs via
    `READTHEDOCS_BUILD_HOOK_URL` secret on `main`/`master` pushes.

---

## [1.5.1] - 2026-07-10

- **mypy / DeepSource Python analyzer findings** (6 files, 12 errors):
  - `utils/_config_common.py`: removed stale `# type: ignore[import-untyped]` for
    `toml` — the package now ships type stubs.
  - `api/api_calls/__init__.py`: replaced stale `type: ignore[assignment]` comments
    with proper `cast(str, ...)` where `target_site`'s `str | None | object` union
    was not narrowed, and direct assignment where `isinstance` already narrowed it;
    removed unused `type: ignore[arg-type]` on `init_client` call.
  - `api/api_calls/v2/contacts.py` + `async_contacts.py`: corrected return type of
    `new_contact` / `anew_contact` from `tuple[str | None, str | None]` to
    `tuple[Any, str | None]` — the first element is the raw `process_result()` /
    `aprocess_result()` payload, which is typed `Any`.
  - `utils/config_manager.py`: added explicit `value: Any` annotation in the
    JSON-parse helper to allow mixed `bool | None | str | Any` assignments without
    mypy narrowing errors.
  - `api/workflows/async_staged_creation.py`: removed stale
    `type: ignore[assignment]` on `asyncio.gather(..., return_exceptions=True)` call.

- **BAN-B310 (#215)** — `utils/check_api_spec_sync.py`: added URL scheme validation
  (`http`/`https` only) before calling `urlopen`, eliminating the `ftp://` /
  `file://` attack surface; simplified except clause to `(OSError, ...)`.

- **PYL-W0404 (#216)** — 295 occurrences across 71 files: removed redundant inline
  `from britecore_sdk.api.api_calls import api_client as _api_client` inside every
  autogenerated function body; all calls now use the module-level `API_CLIENT` alias.
  Added the missing `API_CLIENT: BritecoreAPIClient = api_client` alias to 55
  additional files that only declared `RequestParameters`.

- **PYL-R1705 (#217)** — `utils/interactive_menu.py`: removed unnecessary `else`
  clause after a `return` statement.

- **PYL-W0714 (#218)** — `utils/check_api_spec_sync.py`: collapsed
  `except (URLError, TimeoutError, OSError, ...)` to `except (OSError, ...)` —
  `URLError` and `TimeoutError` are both subclasses of `OSError`.

- **PYL-W0622 (#219)** — 12 occurrences across 11 files: renamed parameters that
  shadowed Python builtins (JSON request keys are unchanged for API compatibility):
  - `id` → `entity_id` (`notes.retrieve_notes`)
  - `id` → `quote_id` (`quotes.get_quote`, `async_quotes.aget_quote`)
  - `id` → `document_id` (`search.add_to_index`, `search.remove_from_index`)
  - `id` → `id_`, `all` → `all_`, `zip` → `zip_code` (contacts, v1/contacts,
    custom_data, quote, settings autogenerated wrappers)
  - `type` → `exposure_type` (`claim_exposures.get_broken_limits`),
    `description_type` (`policies.store_revision_description`)

---

## [1.5.0] - 2026-07-10

### Added

- `britecore_sdk.utils.check_api_spec_sync` now performs upstream spec-version
  checks against
  `https://api.britecore.com/specifications/BriteCore/2.0.0/openapi.json`
  in addition to local freshness checks.
- Added unit-test coverage for local/remote API spec version parsing and version
  comparison behavior in `tests/unit/test_check_api_spec_sync.py`.

### Changed

- Expanded and refreshed API wrapper documentation to reflect July 2026
  wrapper-domain additions:
  - `API.md`
  - `docs/api_reference.md`
  - `README.md`
  - `GETTING_STARTED.md`
  - `TROUBLESHOOTING.md`
  - `UNIMPLEMENTED_API_STUBS.md`
  - `api_specs/README.md`

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
