# Solo Maintainer Strategy

**Project:** `britecore_sdk`
**Owner model:** Single internal maintainer
**Effective date:** 2026-09-24

## Purpose

This strategy keeps the SDK reliable for internal use while minimizing maintenance overhead.

## Default Operating Mode

Use **Internal-First Active (Mode B)** by default:
- Keep core workflows stable (auth, transport, retries, pagination, write safety).
- Accept targeted improvements that reduce operational/debug time.
- Defer broad ecosystem features unless there is clear demand.

## Alternate Modes

### Mode A - Maintenance-Only
- Bug fixes, security updates, compatibility patches.
- No major feature expansion.
- Use when internal value is steady but engineering time is constrained.

### Mode C - Sunset/Archive Prep
- Critical fixes only.
- Publish support window and end-of-life expectations.
- Use when internal usage/value is consistently low.

## 90-Day Execution Plan

### Days 0-30: Stabilize and Scope
- Lock roadmap to high-value items only.
- Standardize async guidance: use `httpx` transport for async callers; retain `urllib3` for sync path.
- Confirm tests for high-risk flows:
  - OAuth token refresh and fallback behavior
  - Retry/backoff behavior
  - Pagination helpers and edge envelopes
  - Write policy enforcement (`allow` / `warn` / `block`)

### Days 31-60: Lower Maintenance Cost
- Tighten deprecation messaging and migration examples.
- Remove or postpone low-value roadmap items.
- Address a small, focused set of high-confidence type debt in hot paths.

### Days 61-90: Decision Gate
- Continue Mode B if internal value and stability are strong.
- Shift to Mode A if value is stable but change demand is low.
- Shift to Mode C if value is low and maintenance cost is not justified.

## Quarterly Decision Criteria

Continue active investment only if most are true:
- SDK saves meaningful internal engineering time.
- Incident/debugging time trends down quarter-over-quarter.
- Release overhead is manageable for one maintainer.
- Planned changes directly support current internal workflows.

Reduce scope if most are true:
- Features are maintained without active use.
- External adoption remains near zero.
- Maintenance burden outweighs measurable internal value.

## Release Policy (Solo-Friendly)

- **Cadence:** Small, predictable releases (monthly or bi-monthly).
- **Versioning:** Keep semver strict; reserve breaking changes for planned major release windows.
- **Change budget:** Prefer 1-3 high-impact items per release.
- **Rollback plan:** Every release should have a clear rollback path.

## Current Commitments

- Treat `v3.0` as a cleanup/reliability milestone, not a broad feature expansion.
- Keep deprecations explicit and time-bound.
- Keep sync/async behavior consistent where feasible.

## Working Backlog Filters

Use these filters before accepting work:
1. Does this reduce internal operational pain in the next quarter?
2. Does this reduce long-term maintenance burden?
3. Can this be tested with targeted, reliable coverage?
4. Is this a better use of time than hardening existing critical paths?

If fewer than 2 answers are "yes", defer the work.

## Communication Notes

- Keep `README.md`, `CHANGELOG.md`, and roadmap docs aligned each release.
- Record deferrals explicitly to avoid hidden backlog growth.
- Prefer clear "no action required" notes for non-impacting internal changes.
