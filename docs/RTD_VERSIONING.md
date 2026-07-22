# ReadTheDocs Versioning and Release Management

*Last updated: July 22, 2026*
*Document type: Operations guide*

For maintainers: understand how ReadTheDocs automatically builds and manages documentation versions across releases.

---

## Overview

ReadTheDocs (RTD) automatically tracks and builds documentation for different versions of the SDK based on git tags and branches. This allows users to view documentation for the specific version they're using.

### Current configuration

The `.readthedocs.yml` configuration automatically:

1. **Builds from `master` branch** (displayed as "latest" release)
2. **Builds from every git tag** matching `v*.*.*` pattern (displayed as "2.0.5", "2.0.4", "2.1.0", etc.)
3. **Marks the highest tag** as the "stable" version

---

## How versioning works

### Release versions (git tags)

When you tag a commit with a version number (e.g., `v2.0.5`), RTD automatically:

1. Detects the tag
2. Builds documentation from that commit
3. Makes it available at `https://britecore-sdk.readthedocs.io/en/v2.0.5/`

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

### Step 3: RTD automatic build

RTD will detect the tag and automatically:

1. Build docs from the `v2.0.6` tag
2. Make it available at `/en/v2.0.6/`
3. Mark it as "stable" if it's the highest version
4. Show version switcher with all available versions

**No manual RTD configuration needed** — it's automatic!

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

**A:** Yes! RTD maintains all tagged versions indefinitely. Users can:

1. Click the version switcher (bottom-left of any doc page)
2. Select any version from the list
3. Or visit the URL directly: `/en/v2.0.3/`

### Q: Will RTD build from all my branches?

**A:** No, only:
- `master` (default) → "latest"
- Git tags matching `v*.*.*` → individual versions

Other branches require explicit configuration in RTD's **Admin** → **Versions** tab.

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
