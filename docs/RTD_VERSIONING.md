# ReadTheDocs Versioning and Release Management

*Last updated: July 22, 2026*
*Document type: Operations guide*

For maintainers: understand how ReadTheDocs automatically builds and manages documentation versions across releases.

---

## Overview

ReadTheDocs (RTD) automatically tracks and builds documentation for different versions of the SDK based on git tags and branches. This allows users to view documentation for the specific version they're using.

### Current configuration

The `.readthedocs.yml` configuration enables docs builds on RTD, but version visibility is controlled by RTD project state:

1. **`master` branch** is typically available as `latest`.
2. **Git tags** are discovered by RTD as version candidates.
3. Versions appear in the selector only when they are **active** and **built** in RTD.
4. `stable` is an alias managed in RTD (commonly the latest release tag).

---

## How versioning works

### Release versions (git tags)

When you tag a commit with a version number (e.g., `v2.0.5`), RTD:

1. Detects the tag as a version candidate.
2. Builds and exposes it only if that version is active and built (manually or via automation rules).
3. Serves docs at `https://britecore-sdk.readthedocs.io/en/v2.0.5/` once built.

Users can then select that version from the RTD version switcher (bottom-left of documentation).

### Branch tracking

- **`master` branch** → Latest development docs
- **Other branches** → Not built by default

### Release matrix

After several releases, RTD shows:

| Version | URL | Status |
|---------|-----|--------|
| 2.0.5 | `/en/v2.0.5/` | stable (highest tag) |
| 2.0.4 | `/en/v2.0.4/` | old release |
| 2.0.3 | `/en/v2.0.3/` | old release |
| Latest | `/en/latest/` | master branch |

---

## Creating a new release

### Step 1: Create a git tag

```bash
git tag v2.0.6 -m "Release version 2.0.6"
git push origin v2.0.6
```

### Step 2: Update version in `pyproject.toml`

```toml
[project]
version = "2.0.6"
```

Commit and push:

```bash
git add pyproject.toml
git commit -m "Bump version to 2.0.6"
git push origin master
```

### Step 3: RTD build and activation

After pushing the tag, RTD detects it. To ensure it appears in the version selector:

1. Confirm the tag version is **active** in **Admin -> Versions**.
2. Trigger/retry a build for the tag if it is not already built.
3. Optionally add/update **Automation Rules** so future `v*` tags auto-activate and build.
4. Verify the docs URL exists (for example, `/en/v2.0.6/`).

---

## RTD web interface

### Viewing builds

1. Go to https://readthedocs.org/projects/britecore-sdk/
2. Navigate to **Builds** tab
3. See all recent builds (master branch and all tags)
4. Click any build to see logs and output

### Configuring versions

1. Go to **Admin** → **Versions**
2. Toggle versions on/off (hidden versions still accessible via direct URL)
3. Set "default version" (what loads when user visits root URL)
4. Mark which version is "stable"

**Current defaults:**
- Default version: "latest" (master branch)
- Stable version: highest tag (auto-selected)

---

## FAQ

### Q: Can users view docs for older releases?

**A:** Yes, as long as those versions are active and built in RTD. Users can:

1. Click the version switcher (bottom-left of any doc page)
2. Select any version from the list
3. Or visit the URL directly: `/en/v2.0.3/`

### Q: Will RTD build from all my branches?

**A:** No. By default, `master` maps to `latest`. Other branches/tags must be enabled in RTD project settings (or covered by automation rules) to be built and shown.

### Q: What if I want to hide an old version?

**A:** RTD provides version hiding:

1. Go to **Admin** → **Versions**
2. Toggle the version off ("Hidden")
3. The docs are still built and accessible via direct URL, but don't appear in the version switcher

This is useful for yanked releases or pre-releases.

### Q: Can I build docs for release candidates?

**A:** Yes, but you'll need a different naming scheme. Examples:

- `v2.1.0rc1` (release candidate) — tags matching this still work
- `v2.1.0a1` (alpha) — also supported

All follow semantic versioning patterns that RTD recognizes.

### Q: Why do I only see `latest` and `stable` in the selector?

**A:** This usually means tag versions are discovered but not active/built. Check **Admin -> Versions** and ensure each release tag is enabled and has a successful build.

### Q: How do I update docs for a released version?

**A:** Create a bug-fix tag:

```bash
# Create from existing tag (e.g., 2.0.5)
git checkout v2.0.5
git checkout -b hotfix-docs
# Make doc fixes
git add docs/
git commit -m "Fix docs for v2.0.5"
git tag v2.0.5.post1
git push origin v2.0.5.post1
```

RTD will build `v2.0.5.post1` as a new version.

---

## Related documentation

- [.readthedocs.yml](.readthedocs.yml) — RTD configuration
- [docs/conf.py](docs/conf.py) — Sphinx configuration
- [DEPLOYMENT.md](DEPLOYMENT.md) — Release and deployment guide
- ReadTheDocs official docs: https://docs.readthedocs.io/
