# Migration Guide: SDK v1 -> v2 (Historical)

*Last updated: September 2, 2026*
*Document type: Historical migration note*

This document is retained for historical context only.

## Important Clarification

SDK major versions and API endpoint versions are different:

- `britecore_sdk` versioning (`1.x`, `2.x`, future `3.x`) is package lifecycle.
- `api_calls/v1` and `api_calls/v2` are upstream endpoint path versions.

Supported `api_calls/v1` wrappers are not legacy by default; some upstream endpoints still use `v1` paths.

## Current Guidance

Use these documents instead of this historical guide:

- `CHANGELOG.md` for shipped version history and deprecation announcements.
- `DEPRECATION.md` for active deprecation policy and planned removals.
- `API.md` for current wrapper usage patterns and endpoint guidance.
- `GETTING_STARTED.md` for recommended initialization and integration patterns.

## Historical Note

The original v1-to-v2 migration content has been retired to reduce confusion with endpoint path versioning.
