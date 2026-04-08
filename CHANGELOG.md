# Changelog

All notable changes to `britecore_libraries` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Added

- `tests/unit/test_api_spec_alignment.py` — validates wrapper paths against
  the canonical `api_specs/current/britecore.json` specification.
- `tests/unit/test_v1_endpoint_routing.py` — unit tests for v1 custom_ui,
  payments, and printing endpoints.
- `tests/unit/test_zip_code_lookup.py` — tests for US zip code lookup utility.
- `examples/basic_api_usage.py` — runnable example demonstrating OAuth and
  API key initialization flows.

### Changed

- **Code quality improvements:**
  - Reduced cyclomatic complexity in `BritecoreAPIClient.process_result` by
    extracting helper methods (`_raise_for_http_status`, `_load_json_payload`,
    `_extract_success_data`).
  - Converted logging f-strings to lazy `%s` formatting in API modules,
    validators, and utilities (DeepSource PYL-W1203).
  - Collapsed nested `with` statements in tests (PTC-W0062).
  - Removed Python built-in shadowing (`type` → `note_type`, `type` →
    `payment_method_type`) with backward-compatible kwargs extraction.
- **Documentation polish:**
  - Added `api_specs/README.md` and normalized checked-in API spec layout to
    `api_specs/current/` and `api_specs/legacy/`.
  - Split archived legacy specs into `api_specs/legacy/britecore/` and
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

### Fixed

- MyPy `TypedDict` compatibility in `payments.py` via explicit casting for
  backward-compatible kwargs extraction.
- DeepSource findings (D202, W1203, PTC-W0048, PTC-W0062, PY-R1000,
  PY-D0003, E1121) addressed via targeted refactoring and configuration.
- Markdown lint formatting (MD012, MD031, MD032, MD040, MD060) across all
  docs.

---

## [1.1.0] — 2026-04-06

### Added

- `src/britecore_libraries/py.typed` marker (PEP 561) — downstream mypy users
  now get inline type information automatically.
- `src/britecore_libraries/api/types.py` — shared `TypedDict` response shapes
  (`BritecoreResponse`, `PolicyData`, `ContactData`, `QuoteData`,
  `InvoiceData`, `RevisionData`, `AddressData`, `PhoneData`, `EmailData`).
- `get_api_client` and `get_async_api_client` are now exported from the
  top-level `britecore_libraries` namespace.
- v2 `__init__.py` now re-exports all 30 sync domain modules so IDEs can
  discover them via `from britecore_libraries.api.api_calls.v2 import <module>`.
- Full implementations for all previously-stubbed v2 API domains:
  `attachments` (11), `custom_ui` (4), `dashboards` (8), `data` (2),
  `errors` (1), `intacct` (5), `nightly_jobs` (4), `notifications` (2),
  `printing` (5), `return_premium` (1), `search` (2), `settings` (11),
  `signatures` (6), `uploads` (1), `vendors` (16) — **374/374 endpoints
  now covered**.
- `tests/unit/test_v2_new_endpoints.py` — parametrized unit tests for all
  newly implemented domain modules.
- `tests/unit/test_logging_tokens.py` — regression tests that assert no
  legacy SCLogging color-format tokens remain in the source tree and that
  runtime log output is plain text.
- CI workflow (`.github/workflows/ci.yml`) now covers Python 3.11–3.14,
  runs ruff, black, mypy, and pytest with a 60% coverage gate.
- `docs/MAP_FILES.md` — policy and sample structures for sensitive
  `*_map.py` files that must not be committed to version control.
- `maps/__init__.py` runtime fallback pattern: `britecore_libraries.maps`
  now re-exports `agency`, `policy_map`, `britecore_policy_type_map`,
  `field_map_to_britecore`, `field_map_to_named_insured`, and
  `field_map_to_risk_location` with graceful `ImportError` fallbacks to
  empty dicts, and `load_regexes` falls back to a built-in implementation
  when the private `britecore_policy_name_map.py` is absent.

### Changed

- `pyodbc`, `selenium`, and `pyinputplus` moved from hard dependencies to
  optional extras (`[database]`, `[browser]`, `[interactive]`). Existing
  consumers who use these utilities should add the relevant extra:
  `pip install "britecore_libraries[database]"`.
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
  re-addition. The runtime fallback in `maps/__init__.py` ensures the
  package still imports cleanly in environments without these files.
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
