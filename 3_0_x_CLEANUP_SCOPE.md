# 3.0.x Cleanup Scope Analysis

**Target Release Window:** Q1 2027 (post-2.6.x)
**Primary Goal:** API initialization and auth handling simplification

---

## Core Removals (Already Planned)

### ✅ 1. Implicit Client Fallback
- Remove `resolve_client()` implicit state logic
- Require explicit `client=` parameter everywhere
- Impact: Sync and async wrappers across all API calls

### ✅ 2. Global Lifecycle Helpers
- Remove `init_api_client()` / `init_async_api_client()` / `reset_api_client()`
- Users construct explicit client instances
- Impact: All entry points, examples, docs

### ✅ 3. Legacy Batch Alias Keys
- Remove `quote_id`/`quote_data`, `contact_id`/`contact_data`
- Retain canonical `id`/`data` only
- Impact: Batch workflow results

---

## Recommended Additional Scope

### Type System Hardening
**Recommended:** Remove remaining `type: ignore` suppressions (deferred from 2.4.7)
- High-confidence suppressions identified in analysis
- Tighten overloads and union types in shared entry points
- Expected: 10-15 suppressions eliminated

**Files to Address:**
- `src/britecore_sdk/api/api_calls/__init__.py`
- `src/britecore_sdk/api/britecore_api_client.py`
- `src/britecore_sdk/api/britecore_async_api_client.py`

### OAuth/API Key Consolidation
**Consider:** Simplify auth mode selection logic
- Current: Complex branching for `use_api_key` vs OAuth
- Proposed: Streamlined conditional based on credential presence
- Benefit: Easier testing, clearer error messages

**Code Areas:**
- `BritecoreAPIClient.init_client()` auth selection logic
- `BritecoreAPIClient.do_request()` token vs API-key header injection
- `AsyncBritecoreAPIClient._perform_request_httpx()` auth header setup

### Module Structure Cleanup
**Consider:** Flatten import paths for cleaner entry points
- Current: `britecore_sdk.api.api_calls.v2.contacts`
- Could simplify to: `britecore_sdk.contacts` (optional, lower priority)
- Only if true v1 deprecation makes sense (most don't)

### Public API Surface Audit
**Recommended:** Remove truly private exports from public interfaces
- Review what's exposed from `britecore_sdk.api.__init__.py`
- Remove internal implementation details
- Clarify public vs implementation-only helpers

### Config/Settings Cleanup
**Consider:** Simplify settings resolution for explicit clients
- Current: Automatic file search and environment override
- With explicit clients: Could make settings more explicit
- No breaking change, but cleaner mental model

---

## Release Checklist for 3.0.0

- [ ] All deprecated surfaces removed
- [ ] `type: ignore` reduction pass complete
- [ ] Auth selection logic streamlined
- [ ] Public API audit completed
- [ ] Migration guide written: `docs/migrations/V3.0.0-MIGRATION.md`
- [ ] Release notes highlight simplifications
- [ ] All examples updated to explicit-client pattern
- [ ] All docs reference new patterns only

---

## Success Criteria

**3.0.x is successful when:**
1. Users can fully migrate from 2.5.x with zero deprecation warnings
2. Code is measurably simpler (lines removed > lines added)
3. Type checking passes with zero suppressions in core paths
4. Examples and docs are cleaner and more uniform
5. New users find initialization pattern obvious from README

---

## Timeline Notes

**2.5.x:** ✅ Complete (current)
**2.6.x:** Strict-mode validation (8-10 weeks after 2.5.x)
**3.0.x:** Major cleanup & removal (Q1 2027, ~24+ weeks from now)

This gives integrators 6+ months of warning and 2 minor versions (2.6.x hotfixes) to validate before 3.0.0 lands.
