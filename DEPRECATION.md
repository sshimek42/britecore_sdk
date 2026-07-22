# Deprecation Policy

*Last updated: July 21, 2026*
*Document type: Governance policy*

For SDK users and maintainers: understand deprecation timelines, version support, and breaking change policies.

This document outlines how `britecore_sdk` manages API deprecation, feature removal, and migration paths.

---

## Overview

The BriteCore SDK follows **semantic versioning**. Breaking changes (removals, major signature changes) only occur in major version releases (e.g., 1.0.0 → 2.0.0).

This policy ensures that:

- Gradual, non-breaking deprecation paths are offered
- Users have clear migration guidance
- Library stability is maintained between major versions

---

## Deprecation Timeline

### Phase 1: Announcement (N releases warning)

A feature is marked `@deprecated` in code and documented:

```python
import warnings

@deprecated(version="1.1.0", removal_version="2.0.0", reason="Use new_function() instead")
def old_function():
    warnings.warn(
        "old_function() is deprecated and will be removed in v2.0.0. Use new_function() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    # ... implementation continues ...
```

- **Duration:** Minimum 2 minor version releases (e.g., 1.1 → 1.2 → 1.3)
- **Visibility:** Clear messages in docstrings and changelogs
- **Guidance:** Migration instructions provided in deprecation note

### Phase 2: Removal (Major version)

In a major release, deprecated features are removed:

```python
# In v2.0.0: removed entirely
# old_function() no longer exists
```

---

## What Can Be Deprecated

- ✅ **Functions & methods** — Replaced with better alternatives

```python
# Earlier releases: Available
def get_policy_by_id_v1(policy_id):
    pass

# Deprecation notice added
@deprecated("Use get_policy_by_id_v2() instead")
def get_policy_by_id_v1(policy_id):
    pass

# v2.0: Removed
# get_policy_by_id_v1 no longer exists
```

- ✅ **Parameters** — Moved, renamed, or replaced

```python
# Earlier releases
def retrieve_policy(policy_number, timeout=5):
    pass

# Deprecation notice for `timeout` parameter
def retrieve_policy(policy_number, timeout=None, **kwargs):
    if timeout is not None:
        # Issue deprecation warning
        kwargs['request_timeout'] = timeout
    return _retrieve_policy_impl(policy_number, **kwargs)

# v2.0: `timeout` parameter removed, use `request_timeout` only
def retrieve_policy(policy_number, request_timeout=5):
    pass
```

- ✅ **Exception types** — Unified or replaced

```python
# Earlier releases: Multiple exception types
class BritecoreAuthError(BritecoreError):
    pass

class OAuthTokenError(BritecoreError):
    pass

# OAuthTokenError marked deprecated
@deprecated("Catch AuthenticationError instead")
class OAuthTokenError(AuthenticationError):
    pass

# v2.0: OAuthTokenError removed
# All auth errors throw AuthenticationError
```

- ✅ **Module locations** — Code moved to a new namespace when a true replacement exists

```python
# Old location
from britecore_sdk.api.api_calls.v2.contacts import get_contact

# Still importable but deprecated
from britecore_sdk.api.api_calls.v2.contacts import get_contact
# DeprecationWarning: Use britecore_sdk.api.api_calls.v2.insured.get_contact

# v2.0: Old location removed
# from britecore_sdk.api.api_calls.v2.contacts import get_contact  # ❌ ImportError
from britecore_sdk.api.api_calls.v2.insured import get_contact  # ✅ Correct
```

**Important SDK rule:** `api_calls/v1` modules are not considered legacy by default.
Some BriteCore endpoints are versioned as `v1` in their URL and have no `v2`
equivalent yet. Those wrappers remain supported and should not be deprecated
just because the path contains `v1`.

Likewise, do not describe the initial 2.x stable release as a blanket SDK-wide
"v1 to v2" migration unless an actual deprecated SDK surface has a direct,
documented replacement.

---

## What Cannot Be Deprecated (Breaking Only in Major)

### Public method signatures — Can only change in major

Changing parameter order, removing required params without deprecation → Major version bump.

### Built-in class names — Can only remove in major

Removing or renaming core exception types (e.g., `BritecoreError`) → Major version bump.

### Supported Python versions — Dropping support → Major version bump

Supporting Python 3.11+ now. Dropping 3.11 support → Major version bump.

---

## Deprecation Notice Template

Use this format for all deprecation notices:

```text
\"\"\"
.. deprecated:: 1.2.0
    Use :func:`new_function` instead. This function will be removed in v2.0.0.

    Migration:

    .. code-block:: python

        # Before (deprecated)
        result = old_function(param1, param2)

        # After (recommended)
        result = new_function(param1, param2, new_param=True)
\"\"\"
```

In docstrings:

```python
def deprecated_function(param1: str) -> dict:
    """
    Retrieve data from the API (DEPRECATED).

    .. deprecated:: 1.2.0
        Use :func:`britecore_sdk.api.api_calls.v2.quotes.retrieve_quote` instead.
        This function will be removed in v2.0.0.

    :param param1: Identifier
    :return: Data dictionary

    Migration Example:
        >>> # Old way (deprecated)
        >>> result = deprecated_function("id123")
        >>>
        >>> # New way (recommended)
        >>> result = retrieve_quote(quote_number="id123")
    """
```

---

## CHANGELOG Entry Format

When deprecating a feature, add to `CHANGELOG.md` under `[Unreleased]` or the next version:

```markdown
### Deprecated

- `old_module.old_function()` — Use `new_module.new_function()` instead. Will be removed in v2.0.0.
- `RequestParameters.timeout` parameter — Use `RequestParameters.request_timeout` instead. Will be removed in v2.0.0.
```

When removing in a major version:

```markdown
### Removed

- `old_module.old_function()` — Removed as planned in an earlier deprecation notice. Use `new_module.new_function()`.
- `RequestParameters.timeout` parameter — Removed. Use `RequestParameters.request_timeout` instead.
```

---

## Migration Guides

Create migration guides for major deprecations. Store in `docs/migrations/`:

**File: `docs/migrations/<release>-migration.md`**

````markdown
# Migration Guide for <release>

## Breaking Changes

### 1. Module restructuring

Only wrappers with a direct successor moved to the new import path.
Versioned endpoint wrappers under `api_calls/v1` may remain supported when
the upstream API has no `v2` equivalent.

**Before:**

```python
from britecore_sdk.api.api_calls.v2.contacts import get_contact
```

**After:**

```python
from britecore_sdk.api.api_calls.v2.insured import get_contact
```

````

### 2. Exception types unified

Multiple exception types consolidated into `BritecoreError` hierarchy.

**Before (legacy pattern):**

```python
try:
    result = retrieve_policy()
except (AuthError, OAuthTokenError, ConfigError) as e:
    handle_error(e)
```

**After (v2.0):**

```python
try:
    result = retrieve_policy()
except (AuthenticationError, ConfigurationError) as e:
    handle_error(e)
```

## Deprecation Removals

Features deprecated in prior releases that are now removed:

- `old_function()` — Use `new_function()` instead
- `RequestParameters.timeout` — Use `request_timeout` instead

---

## Best Practices for Feature Deprecation

### 1. Provide a Clear Path Forward

```python
@deprecated("Use retrieve_policy_v2() with new_param=True")
def retrieve_policy_v1(policy_number: str):
    """..."""
    pass
```

- ❌ **Bad:** "This is deprecated" (no guidance)

- ✅ **Good:** "Use `retrieve_policy_v2()` with `new_param=True` instead" (clear migration)

### 2. Version the Deprecation Notice

```python
@deprecated(
    version="1.2.0",  # When deprecated
    removal_version="2.0.0",  # When removed
    reason="Use new_function() instead"
)
def old_function():
    pass
```

### 3. Document in Multiple Places

- **Code:** `@deprecated` decorator + docstring
- **CHANGELOG.md:** List under "Deprecated" section
- **Docs:** Migration guide if multiple items deprecated
- **Tests:** Include deprecation warning assertions

```python
import pytest

def test_old_function_warns():
    with pytest.warns(DeprecationWarning, match="old_function"):
        result = old_function()
    assert result is not None
```

### 4. Provide Sufficient Warning Time

- Announce in minor version (1.2.0)
- Keep available for ≥2 minor releases (1.2, 1.3, …)
- Remove in next major version (2.0.0)

**Example timeline:**

- 1.1.0: Feature works
- 1.2.0: Deprecation announced
- 1.3.0: Still available (recommended upgrade)
- 1.4.0: Still available (final notice: "Remove in v2")
- v2.0.0: Removed

---

## Version Bump Rules

| Change | Version Rule | Example |
|--------|--------------|---------|
| **Add deprecation notice** | Minor (1.x.**0**) | 1.1.0 → 1.2.0 |
| **Remove deprecated feature** | Major (**X**.0.0) | 1.0.0 → 2.0.0 |
| **Fix deprecated feature** | Patch (1.Y.**z**) | 1.2.0 → 1.2.1 |

---

## Exceptions to the Policy

### Security Fixes

If a deprecated feature has a security vulnerability, it may be removed earlier:

```markdown
### Removed

- `unsafe_auth_mode()` — SECURITY: Removed early due to authentication bypass vulnerability.
  Use `secure_auth_mode()` immediately. Affected versions: 1.0-1.2.
```

### Critical Bugs in Deprecated Features

If a deprecated feature's bug fix is expensive, it may be marked "no longer supported":

```markdown
### Deprecated

- `legacy_payment_processor()` — Known issue with currency conversion.
  No fixes planned. Migrate to `modern_payment_processor()`.
```

---

## Communication Strategy

### When Deprecating

1. **Add to CHANGELOG.md** under `[Unreleased]`
2. **Add to docs/migrations/** if major change
3. **Update docstrings** with deprecation notice
4. **Announce in PR description**
5. **Update CONTRIBUTING.md** if guidance affects maintainers

### When Removing

1. **Add to CHANGELOG.md** under `### Removed`
2. **Reference the deprecation announcement** from earlier version
3. **Link to migration guide** in PR description

---

## See Also

- [CHANGELOG.md](CHANGELOG.md) — Release history and feature status
- [PYTHON_COMPATIBILITY.md](PYTHON_COMPATIBILITY.md) — Version support policy
- [CONTRIBUTING.md](CONTRIBUTING.md) — For maintainers on deprecation process
