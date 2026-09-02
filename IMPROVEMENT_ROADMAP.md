# BriteCore SDK Improvement Roadmap

*Last updated: September 2, 2026*
*Status: Active roadmap aligned to `v2.4.6` and `v3.0.0` deprecation planning*
*Audience: Maintainers and contributors*

## Executive Summary

`britecore_sdk` is stable and release-ready at `v2.4.6`. The near-term roadmap focuses on developer experience and migration safety: ship `2.4.7` improvements, introduce runtime deprecation signaling in `2.5.x`, provide strict-mode migration validation in `2.6.x`, and remove deprecated surfaces in `v3.0.0`.

This document is planning-oriented. For shipped history, use `CHANGELOG.md`. For deprecation policy and removal commitments, use `DEPRECATION.md`.

---

## Baseline: Recently Completed

### `v2.4.6` (September 2, 2026)

- Added payload models for payment methods, vehicles, coverages, drivers, and line definitions.
- Added claim mapper support for named insured contact-role mapping.
- Added model-aware payload coercion in selected wrappers and data-layer helpers.
- Hardened CLI/example output handling to avoid clear-text payload output to stdout.

### `v2.4.5` (September 1, 2026)

- Added write-safety controls (`allow`, `warn`, `block`) and `ReadOnlyViolation`.
- Added `AuditMiddleware` for request audit events.
- Added script-first `data_layer` normalization helpers and `britecore-normalize-json` CLI.

---

## Near-Term Delivery Plan

### Phase A: `2.4.7` (2 to 3 weeks)

**Goal:** Improve troubleshooting and observability while keeping behavior backward-compatible.

- Add error-hint guidance for common configuration/authentication failures.
- Add response helper utilities for common data extraction and pagination patterns.
- Expand structured logging categories for better operational filtering.
- Add request-timing observability hooks for slow endpoint triage.
- Remove remaining high-confidence `type: ignore` suppressions where feasible.

**Deprecation announcements (no removals in this phase):**

- Implicit wrapper client fallback without explicit `client=`.
- Global lifecycle helpers as the primary app pattern.
- Legacy batch alias keys (`quote_id`/`quote_data`, `contact_id`/`contact_data`).

### Phase B: `2.5.x` (4 to 6 weeks after `2.4.7`)

**Goal:** Start migration enablement for `v3.0.0`.

- Emit `DeprecationWarning` on deprecated runtime paths by default.
- Publish migration guidance for explicit client usage patterns.
- Expand troubleshooting docs for deprecation-related diagnostics.
- Add tests that assert warning behavior and migration-safe alternatives.

### Phase C: `2.6.x` (8 to 10 weeks after `2.5.x`)

**Goal:** Let integrators validate readiness before major-version removals.

- Add strict-mode toggle to convert selected deprecation warnings into errors.
- Provide compatibility test scenarios for explicit-client-only workflows.
- Expand integration tests for common policy/contact/quote workflow paths.
- Add pre-removal checklist for maintainers and downstream consumers.

### Phase D: `v3.0.0` (target window: Q1 2027)

**Goal:** Remove deprecated surfaces and simplify long-term API usage patterns.

- Remove implicit client fallback path.
- Remove global lifecycle helpers as application-facing pattern.
- Remove legacy batch alias keys; retain canonical `id`/`data` keys.
- Publish `docs/migrations/V3.0.0-MIGRATION.md` before release.

---

## Backlog (Post-`2.6.x` / Opportunistic)

- Reusable fixtures library for faster unit test authoring.
- Additional integration workflow templates.
- Optional webhook helper framework expansion.
- Advanced benchmarking and latency percentile reporting.

---

## Success Metrics

| Objective | Target | Planned Phase |
| --- | --- | --- |
| Explicit-client adoption readiness | Warning coverage on deprecated paths | `2.5.x` |
| Migration confidence before major release | Strict-mode compatibility checks | `2.6.x` |
| Type-check cleanliness | Remove remaining high-confidence suppressions | `2.4.7` |
| Observability for API performance | Timing hooks available in client path | `2.4.7` |

---

## Contribution Guidance

- For immediate contributions, prioritize `2.4.7` items.
- For migration-focused work, coordinate changes under `2.5.x` and `2.6.x` phases.
- Before implementing deprecation-affecting changes, ensure `CHANGELOG.md` and `DEPRECATION.md` remain synchronized.
