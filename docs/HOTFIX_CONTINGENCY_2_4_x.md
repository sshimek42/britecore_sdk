# 2.4.x Hotfix Contingency Runbook

*Last updated: September 8, 2026*
*Document type: Operations runbook*

Use this runbook to ship urgent `2.4.x` patch releases (for example `2.4.9`) from `release/2.4.x` with minimal delay and clear auditability.

---

## Preconditions

- A production issue requires a patch on the `2.4.x` maintenance line.
- The fix commit exists on another branch, or can be authored directly on a hotfix branch.
- A release owner is assigned for merge, tag, publish, and post-release verification.

---

## Fast Path Checklist (`2.4.9` Example)

### 1) Create hotfix branch from `release/2.4.x`

```powershell
git fetch --all --tags
git checkout release/2.4.x
git pull --ff-only
git checkout -b hotfix/2.4.9-<short-topic>
```

### 2) Cherry-pick only required fix commits

```powershell
git cherry-pick <commit-sha-1>
git cherry-pick <commit-sha-2>
```

- Resolve conflicts with `2.4.x` compatibility in mind.
- Do not include unrelated `2.5.x` refactors.

### 3) Update release metadata

- Bump `project.version` in `pyproject.toml` to `2.4.9`.
- Add `2.4.9` section in `CHANGELOG.md` with date and concise patch notes.

### 4) Validate before PR

Run at least targeted tests for touched functionality and a package build smoke check.

```powershell
python -m pytest tests/unit -m unit -v --no-cov
python -m build
```

If docs changed:

```powershell
python scripts\docs_qa.py
```

### 5) Open PR into `release/2.4.x`

- Suggested title: `release(2.4.9): <fix summary>`
- Include risk assessment, validation evidence, and rollback notes.

### 6) Merge and tag release commit

```powershell
git checkout release/2.4.x
git pull --ff-only
git tag -a v2.4.9 -m "v2.4.9"
git push origin v2.4.9
```

- Ensure tag points to the merged PR commit.
- For a no-PR incident path, use annotated tag message with `[break-glass]` and complete `docs/RELEASE_HOTFIX_TEMPLATE.md`.

### 7) Publish and verify

- Trigger the release/publish workflow for `v2.4.9`.
- Verify package visibility on indexes used by downstream consumers.
- Confirm both package name variants if your automation publishes both (`britecore-sdk`, `britecore_sdk`).

### 8) Post-release hygiene

- Confirm the same fix exists on `release/2.5.x` or `master`.
- Link PR, tag, release URL, and any incident record in your internal tracker.

---

## Quick Rollback Options

- Cut follow-up patch (`2.4.10`) that reverts/fixes the regression.
- If package registry policy allows, yank the bad release and publish corrected patch.
- Coordinate downstream consumers on pin/upgrade guidance.

---

## See Also

- [RELEASE_OPERATIONS_CHECKLIST](./RELEASE_OPERATIONS_CHECKLIST.md)
- [RELEASE_HOTFIX_TEMPLATE](./RELEASE_HOTFIX_TEMPLATE.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
