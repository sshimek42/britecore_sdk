# Release Operations Checklist

*Last updated: September 4, 2026*
*Document type: Integration guide*

Use this checklist for each release candidate and final release to reduce non-doc regressions in packaging, runtime behavior, and release automation.

---

## Scope

This checklist is intentionally complementary to:

- `docs/DOCUMENTATION_RELEASE_CHECKLIST.md` for docs/version-link quality
- `CONTRIBUTING.md` maintainer release steps for tags, GitHub release flow, and PyPI publish

---

## PR Policy by Release Type

- **Major (`X+1.0.0`), minor (`X.Y+1.0`), and patch (`X.Y.Z+1`) releases:** require a merged PR before tagging.
- **Break-glass patch exception:** direct patch tag is only for urgent production incidents.
- **Explicit break-glass marker:** use an **annotated tag** with `[break-glass]` in the tag message for no-PR emergency patch releases.
- **Audit trail requirement:** record incident context using `docs/RELEASE_HOTFIX_TEMPLATE.md` and open a follow-up PR for auditability.

---

## GitHub Admin Runbook: Branch Protection

Use this when configuring or auditing protection for the default branch (`master` in this repo at time of writing; use `main` if renamed).

1. Open repository settings: **Settings -> Branches -> Add branch protection rule**.
2. Set branch name pattern to the default branch (`master` currently).
3. Enable and save the following controls:
   - **Require a pull request before merging**
   - **Require approvals** (minimum: 1)
   - **Dismiss stale pull request approvals when new commits are pushed**
   - **Require status checks to pass before merging**
   - **Require branches to be up to date before merging**
   - **Restrict who can push to matching branches** (or disable direct pushes)
   - **Do not allow force pushes**
   - **Do not allow deletions**

Recommended required checks (current status context names):

- `build-docs`
- `Docs-only QA`
- `Release smoke checks`
- `test (3.11, false)`
- `quality (3.11)`
- `lint`

> **Note:** Keep check names in sync with workflow names in `.github/workflows/` when workflows are renamed.

---

## Release Readiness Checklist

### 1) Version and release metadata

- [ ] Confirm `project.version` in `pyproject.toml` matches the release target.
- [ ] Confirm release tag format is `vX.Y.Z` (or prerelease format like `vX.Y.Z-rc.1`).
- [ ] Confirm `CHANGELOG.md` has a matching dated section for `X.Y.Z`.
- [ ] Confirm release type (patch/minor/major) is explicitly noted in PR title/body or release notes draft.
- [ ] Confirm tag commit is from a merged PR.
- [ ] For direct emergency patch releases, confirm the annotated tag message includes `[break-glass]`.
- [ ] For direct emergency patch releases, complete `docs/RELEASE_HOTFIX_TEMPLATE.md` and attach/link it in the follow-up PR.
- [ ] For direct emergency patch releases, confirm a follow-up PR link is recorded.

### 2) API compatibility and behavior

- [ ] Validate key public imports still resolve (top-level package, `api`, `models`, `validators`).
- [ ] Validate endpoint wrapper signatures/required params changed only when intended.
- [ ] Validate key return-shape assumptions (`success`, `data`, `message/messages`) in touched flows.
- [ ] Verify deprecations called out in `DEPRECATION.md` are still accurate for this release.

### 3) Configuration and auth paths

- [ ] Validate configuration precedence still works (`settings.toml`, user config, project config, `BRITECORE_SDK_SETTINGS_FILE`, `BRITECORE_SDK_*`).
- [ ] Validate explicit inline credential init (`base_url`, auth values) for multi-site scenarios.
- [ ] Validate both auth modes for touched flows: API key mode and OAuth mode.
- [ ] Confirm no secrets are logged in release notes/examples/tests.

### 4) Runtime reliability

- [ ] Validate sync client flow with representative endpoint wrappers.
- [ ] Validate async client flow for the selected transport(s) used by your project.
- [ ] Validate timeout/retry overrides for touched endpoints (`RequestParameters`).
- [ ] Validate cleanup behavior for long-lived clients (`with`/context manager paths).

### 5) Packaging and distribution

- [ ] Build local artifacts (`sdist` and wheel) and verify they complete successfully.
- [ ] Confirm install works from fresh env (editable and wheel install smoke check).
- [ ] Confirm `project.scripts` entry points still import and run.
- [ ] Confirm extras metadata (`async-http`, `typed-config`) installs as expected.

### 6) CI and release automation

- [ ] Confirm core CI checks pass for the release branch/tag.
- [ ] Confirm release workflow validates version/tag parity.
- [ ] Confirm publish workflow completed and PyPI package is visible.
- [ ] If manual publish is required, record who executed it and from which tag.

### 7) Security and compliance

- [ ] Run dependency vulnerability scan for changed or bumped dependencies.
- [ ] Confirm license and attribution docs are still present and current.
- [ ] Run `scripts/release_compliance_check.ps1` before release finalization.

### 8) Rollback and incident readiness

- [ ] Define rollback action for this release (hotfix tag, patch release, or yank guidance).
- [ ] Record an owner-on-call for the first post-release observation window.
- [ ] Record where release validation logs/artifacts are stored.

---

## Minimal Release-Day Commands (PowerShell)

```powershell
python -m pytest tests/unit -m unit -v --no-cov
python -m pytest tests/integration -m integration -v --no-cov
python -m build
pwsh -File .\scripts\release_compliance_check.ps1
```

If you changed docs, also run:

```powershell
python scripts\docs_qa.py
```

Linux/macOS equivalent:

```bash
python -m pytest tests/unit -m unit -v --no-cov
python -m pytest tests/integration -m integration -v --no-cov
python -m build
pwsh -File ./scripts/release_compliance_check.ps1
```

---

## Ownership Sign-off Template

```text
Release operations checklist sign-off for vX.Y.Z
- Release maintainer: @<name>
- QA/runtime reviewer: @<name>
- Security/compliance reviewer: @<name>
- Notes: <exceptions or N/A>
```

---

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [DOCUMENTATION_RELEASE_CHECKLIST](./DOCUMENTATION_RELEASE_CHECKLIST.md)
- [RELEASE_HOTFIX_TEMPLATE](./RELEASE_HOTFIX_TEMPLATE.md)
- [DEPRECATION.md](../DEPRECATION.md)
- [SECURITY.md](../SECURITY.md)
- [STABILITY.md](../STABILITY.md)
