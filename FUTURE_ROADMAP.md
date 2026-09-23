# BriteCore SDK Future Roadmap (Beyond Configuration)

*Last updated: September 23, 2026*
*Audience: Maintainers and contributors planning `3.1+` work*
*Scope: Product and SDK improvements beyond configuration, with a companion section for proposed config evolution notes*

## Purpose

This roadmap captures recommended post-`3.0.0` improvements outside configuration management. It is intended to help maintainers prioritize compatibility-safe improvements in `3.1` and `3.2`, then plan cleanup removals for `4.0`.

For shipped history, use `CHANGELOG.md`.
For deprecation/removal commitments, use `DEPRECATION.md`.
For config-specific evolution, use `CONFIG_MANAGEMENT.md` and related migration docs.

## Companion Notes: Proposed Configuration Changes (`3.1+`)

These notes are additive guidance for future releases. They are intentionally scoped as non-breaking for `3.1.x` and `3.2.x`.

### Proposed `3.1.x` Additions

- Add `schema_version` to config files (default to `1` when omitted).
- Add explicit `auth.mode` (`api_key` or `oauth`) while preserving existing top-level auth keys as compatibility aliases.
- Add strict config validation mode that detects conflicting auth fields, missing required fields, and invalid URL formats.
- Document deterministic precedence: explicit kwargs > environment variables > profile values > file defaults.

### Proposed `3.2.x` Additions

- Add profile-aware configuration blocks (`profiles.dev`, `profiles.stage`, `profiles.prod`) with `default_profile` selection.
- Add secret indirection support (`env:VAR_NAME`) so config files can reference environment variables instead of storing secrets directly.
- Add richer validation diagnostics with fix hints for common auth and site configuration mistakes.

### `4.0` Candidate Cleanup (Data-Driven)

- Remove legacy alias fields only after telemetry and migration data confirm broad adoption of canonical schema fields.
- Keep migration tooling and docs available through at least one major-version boundary.

---

## Guiding Principles

- Keep `3.x` focused on additive improvements and migration-safe defaults.
- Prefer explicit, typed, and observable behavior over implicit magic.
- Document behavior changes in release notes with runnable examples.
- Avoid introducing new global state patterns.

---

## Priority Framework

### Must

#### 1) Stable Exception Hierarchy

**Why:** Consumers need predictable, typed failures instead of parsing response payloads.

**Scope:**
- Introduce SDK exception base class and categorized subclasses:
  - `BritecoreSDKError`
  - `AuthenticationError`
  - `AuthorizationError`
  - `RateLimitError`
  - `ValidationError`
  - `TransportError`
  - `TimeoutError`
- Map sync/async paths to the same exception categories.

**Acceptance Criteria:**
- All public request paths raise only documented exception types.
- Error objects expose standardized fields (`status_code`, `error_code`, `message`, `request_id` where available).
- Migration notes include old-to-new error mapping examples.

**Target:** `3.1.x`

#### 2) First-Class Retry and Timeout Policy

**Why:** Current consumers need resilient defaults without custom wrappers.

**Scope:**
- Add retry/backoff/jitter controls with safe defaults.
- Respect idempotency boundaries for write operations.
- Add per-request overrides for timeout/retry behavior.

**Acceptance Criteria:**
- Retry policy can be configured globally and per request.
- Retries occur only for documented status/transport failures.
- Integration tests validate retry decisions for read and write routes.

**Target:** `3.1.x`

#### 3) Consistent Sync/Async API Surface

**Why:** Teams often mix sync and async usage and need identical semantics.

**Scope:**
- Normalize method signatures and return shape conventions where practical.
- Align pagination/batch helper behavior between sync and async modules.

**Acceptance Criteria:**
- Public sync and async counterparts document equivalent parameters and behavior.
- Batch and pagination helpers provide matching canonical output contracts.
- Mismatch list is tracked and reduced to zero for targeted modules.

**Target:** Start `3.1.x`, complete `3.2.x`

### Should

#### 4) Typed Response Contracts for High-Traffic Endpoints

**Why:** Stronger typing improves reliability and autocomplete for integrators.

**Scope:**
- Define typed response objects for common domains (policy, quote, contact, claim).
- Keep compatibility by allowing opt-in typed wrappers before full adoption.

**Acceptance Criteria:**
- Typed contracts published for the selected endpoint set.
- Type-check tests cover common response paths.
- Docs show side-by-side raw JSON and typed usage.

**Target:** `3.2.x`

#### 5) Observability Hooks and Correlation IDs

**Why:** Operators need traceable request diagnostics without patching internals.

**Scope:**
- Standardize structured logging fields for request lifecycle events.
- Surface correlation/request IDs consistently in logs/errors when provided.
- Add lightweight hooks for metrics/tracing integration.

**Acceptance Criteria:**
- Log field contract is documented and stable.
- Request correlation identifiers are exposed in both sync/async failure paths.
- Example integration snippets exist for basic telemetry wiring.

**Target:** `3.1.x`

#### 6) Public API Surface Governance

**Why:** Prevent accidental breaking changes from leaked internals.

**Scope:**
- Audit exported symbols and lock down intended public modules.
- Add API-surface tests that detect unintentional public additions/removals.

**Acceptance Criteria:**
- Public export list is documented and test-enforced.
- Private/internal modules are clearly marked and excluded from support guarantees.

**Target:** `3.2.x`

### Could

#### 7) Developer Experience Utilities

**Why:** Reduce repetitive integration code in downstream projects.

**Scope:**
- Optional convenience helpers for common workflow orchestration.
- Additional example scripts for end-to-end policy/quote/contact flows.

**Acceptance Criteria:**
- New utilities are additive and do not obscure core SDK behavior.
- Examples run under CI and stay versioned with API changes.

**Target:** Opportunistic in `3.2.x+`

#### 8) Performance Bench Harness

**Why:** Track latency and regression trends across releases.

**Scope:**
- Add benchmark scripts for representative endpoint mix.
- Capture baseline and p50/p95 latency trends per release train.

**Acceptance Criteria:**
- Bench harness can run locally and in CI on demand.
- Results are stored or summarized in release engineering notes.

**Target:** Opportunistic in `3.2.x+`

---

## Suggested Release Sequencing

### `3.1.x`
- Must: exception hierarchy, retry/timeout policy, sync/async consistency kickoff.
- Should: observability hooks and correlation ID contract.

### `3.2.x`
- Must completion: sync/async consistency and canonical helper behavior.
- Should: typed response contracts, API surface governance tests.
- Could: optional DX utilities and benchmark harness.

### `4.0.0` (only if adoption data supports it)
- Remove compatibility shims introduced for phased `3.x` adoption.
- Keep only final canonical contracts that were proven in `3.1/3.2`.

---

## Tracking and Exit Criteria

- Open an issue per roadmap item with the same naming used in this file.
- Attach tests and docs to each item before marking complete.
- For any behavior change, include migration snippets in release notes.
- Do not mark `3.1` or `3.2` tracks complete until acceptance criteria are met.
