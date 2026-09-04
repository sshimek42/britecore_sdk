# Documentation Release Checklist

*Last updated: September 4, 2026*
*Document type: Integration guide*

Use this checklist for every SDK release (`vX.Y.Z`, including prereleases) to keep docs accurate, linked, and version-consistent.

---

## Release Docs Checklist

### 1) Confirm release inputs

- [ ] Confirm target version in `pyproject.toml` (`project.version`) matches the release you are cutting.
- [ ] Confirm `CHANGELOG.md` includes `## [X.Y.Z] - YYYY-MM-DD` for this release.
- [ ] Confirm the release date used in docs updates is the same date used in `CHANGELOG.md`.

### 2) Update release-facing docs

- [ ] Update root `README.md` sections that mention the latest release/features.
- [ ] Update `GETTING_STARTED.md` if install/setup guidance changed.
- [ ] Update `CONFIG_MANAGEMENT.md` when env vars, settings files, or defaults changed.
- [ ] Update any affected guide in `docs/` (for example `docs/MULTI_TENANCY.md`, `docs/DEPLOYMENT.md`, `docs/RATE_LIMITING.md`).

### 3) Verify version mentions and compatibility ranges

- [ ] Search for stale version mentions in docs and update them when they are intended to track latest release.
- [ ] Confirm deprecation timelines in `DEPRECATION.md` still match the current roadmap and release plan.
- [ ] Confirm migration guidance (for example `docs/MIGRATION_v1_to_v2.md`) still reflects current behavior.

Suggested search command (PowerShell):

```powershell
Get-ChildItem -Path . -Recurse -Filter *.md |
    Select-String -Pattern '\bv?\d+\.\d+\.\d+\b' |
    Select-Object Path, LineNumber, Line
```

### 4) Validate internal docs links

- [ ] Run strict Sphinx build (warnings treated as errors).
- [ ] Run Sphinx linkcheck and resolve broken links before release.
- [ ] For external links that redirect, keep them only if destination is stable and intentional.

```powershell
python -m sphinx -W --keep-going -b html .\docs .\docs\_build\html-strict
python -m sphinx -b linkcheck .\docs .\docs\_build\linkcheck
```

### 5) Verify release discoverability

- [ ] Ensure `docs/index.md` navigation still points to the right guides.
- [ ] Ensure release notes are discoverable from repository docs (`CHANGELOG.md` and GitHub Releases).
- [ ] Ensure new/renamed docs pages are included in a `toctree` so they render on RTD.

### 6) Final release doc sign-off

- [ ] Confirm docs changes are included in the release PR.
- [ ] Confirm CI docs jobs pass (`docs.yml` including linkcheck artifact upload).
- [ ] Add a short PR note: "Docs checklist completed for `vX.Y.Z`."

### 7) Role-based review ownership

- [ ] **Release maintainer** signs off sections 1, 3, and 6.
- [ ] **Docs maintainer** signs off sections 2, 4, and 5.
- [ ] If no dedicated docs maintainer is assigned, release maintainer explicitly notes single-owner review in the PR.

Use this PR sign-off template:

```text
Docs release checklist sign-off for vX.Y.Z
- Release maintainer: @<name> (sections 1, 3, 6)
- Docs maintainer: @<name> (sections 2, 4, 5)
- Notes: <exceptions or N/A>
```

---

## Minimal Release-Day Commands (PowerShell)

```powershell
python -m sphinx -W --keep-going -b html .\docs .\docs\_build\html-strict
python -m sphinx -b linkcheck .\docs .\docs\_build\linkcheck
python scripts\docs_qa.py
```

---

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md) - Maintainer release checklist
- [RELEASE_OPERATIONS_CHECKLIST](./RELEASE_OPERATIONS_CHECKLIST.md) - Non-doc release readiness checks
- [CHANGELOG.md](../CHANGELOG.md) - Release notes and version history
- [DEPRECATION.md](../DEPRECATION.md) - Deprecation policy and timing
- [DOCUMENTATION_BUILD_TROUBLESHOOTING](./DOCUMENTATION_BUILD_TROUBLESHOOTING.md) - Build/linkcheck troubleshooting
