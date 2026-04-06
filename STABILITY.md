# Stability and Support Policy

*Last updated: April 6, 2026*

This document outlines the stability commitments, support expectations, and versioning practices for `britecore_libraries`.

## Version Policy

`britecore_libraries` follows [Semantic Versioning](https://semver.org/):

- **Major version** (e.g., `2.0.0`) — Breaking API changes
- **Minor version** (e.g., `1.1.0`) — New features, backward compatible
- **Patch version** (e.g., `1.0.1`) — Bug fixes, backward compatible

## Release Cycle

### Maintenance Windows

- **Active releases** (current major version) — Bug fixes, security patches, minor features
- **Previous major version** — Critical security fixes only, for 12 months after new major release
- **Older versions** — No support

Example:

```text

1.x.y (Active)          ← Bug fixes, minor features, security patches
0.x.y (Deprecated)      ← Critical security patches for 12 months from 1.0.0 release
older                   ← No support

```

### Release Schedule

- **Patch releases** — As needed (usually weekly for bug fixes)
- **Minor releases** — Monthly or as features accumulate
- **Major releases** — 6–12 months apart

## Backward Compatibility Guarantee

### Within a major version

✅ **Guaranteed compatible:**
- Bug fixes
- New optional parameters (with sensible defaults)
- New helper functions or utilities
- Performance improvements
- Internal implementation changes

❌ **Not guaranteed compatible:**
- Removing public functions or classes
- Changing function signatures (parameters, return types)
- Changing exception types or error messages
- Changing behavior of existing functionality
- Modifying `__all__` exports significantly

### Example

```python

# ✅ OK in minor release (e.g., 1.0.0 → 1.1.0)
def get_policy(policy_id, include_details=False):  # New optional param
    ...

# ❌ NOT OK in minor release (breaking change)
def get_policy(policy_id: str) -> dict:  # Changed return type
    ...  # Must wait for 2.0.0

```

## Deprecation Policy

When breaking changes are necessary:

1. **Deprecation warning** — Issue added in minor release with `DeprecationWarning`

   ```python

   import warnings
   warnings.warn(
       "old_function() is deprecated; use new_function() instead",
       DeprecationWarning,
       stacklevel=2
   )

   ```

2. **Documentation** — Add to `CHANGELOG.md` under **Deprecations** section
3. **Minimum notice** — At least **2 minor releases** before removal (usually 2–3 months)
4. **Removal** — Only in next major version

### Example Timeline

```text

1.0.0  → Introduce new API, start deprecating old API
         (Release notes: "old_api() deprecated; use new_api() instead")

1.1.0  → Still support old API with warning
         (Release notes: "old_api() deprecated; will remove in 2.0")

1.2.0  → Still support old API with warning

2.0.0  → Remove old API
         (Release notes: "Breaking: removed old_api(); use new_api() instead")

```

## Python Version Support

### Current Support Matrix

From `pyproject.toml`: `requires-python = ">=3.11"`

- **Actively tested** — Python 3.11, 3.12, 3.13, 3.14 (all versions in CI matrix)
- **Minimum supported** — Python 3.11
- **Drop schedule** — When upstream reaches end-of-life

### Version Bumps

When Python versions reach end-of-life, we may:

1. **Drop support** — In a new major release (e.g., when 3.11 reaches EOL in October 2027, drop in `2.0.0`)
2. **Announce** — In CHANGELOG and release notes at least 2 releases ahead

Current EOL dates (Python):
- 3.11: October 2027
- 3.12: October 2028
- 3.13: October 2029
- 3.14: October 2030

## Dependency Stability

### Pinning

Dependencies are pinned to compatible ranges:
- Core deps: `package~=X.Y.Z` (patch-compatible)
- Optional deps: Same approach
- Dev deps: Looser pinning for flexibility

Example:

```toml

[project]
dependencies = [
    "urllib3~=2.6.3",    # Allow 2.6.x, not 2.7.x
    "dynaconf~=3.2.13",  # Allow 3.2.x, not 3.3.x
]

```

### Major Dep Upgrades

When a major dependency upgrades:
- Evaluate compatibility
- Test thoroughly
- Document in CHANGELOG
- May require major version bump if breaking changes

## Support Channels

### Getting Help

- **Issues** — Bug reports, feature requests on GitHub
- **Discussions** — Questions and troubleshooting
- **Documentation** — See README.md, docs/, TROUBLESHOOTING.md

### Reporting Bugs

1. Check existing issues
2. Include:
   - Python version
   - Package version
   - Minimal reproducible example
   - Full error traceback

## What We Don't Guarantee

- **Performance** — Optimization may change
- **Internal APIs** — Private functions/classes (prefixed with `_`) can change at will
- **Error messages** — Text may change; catch exception types instead
- **Config file formats** — May evolve (with migration guidance)
- **Log output format** — Internal only, not a public API

## See Also

- [CHANGELOG.md](CHANGELOG.md) — All version history and changes
- [SECURITY.md](SECURITY.md) — Security reporting and patch timeline
- [PYTHON_COMPATIBILITY.md](PYTHON_COMPATIBILITY.md) — Detailed version matrix
