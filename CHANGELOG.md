# Changelog

All notable changes to `britecore_libraries` are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Version numbers follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

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
- CI workflow (`.github/workflows/ci.yml`) now covers Python 3.11–3.14,
  runs ruff, black, mypy, and pytest with a 60% coverage gate.

### Changed
- `pyodbc`, `selenium`, and `pyinputplus` moved from hard dependencies to
  optional extras (`[database]`, `[browser]`, `[interactive]`). Existing
  consumers who use these utilities should add the relevant extra:
  `pip install "britecore_libraries[database]"`.
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

