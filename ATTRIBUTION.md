# Attribution & Third-Party Notices

*Last updated: July 21, 2026*
*Document type: Maintenance template*

Use this file to record third-party notices that should travel with releases.
Keep entries concise, factual, and easy to diff.

## When to update this file

Update this file when you:

- Add a runtime or distributed dependency with special notice requirements.
- Vendor/copy non-trivial third-party code snippets, templates, or assets.
- Bundle data files from third-party sources (for example CSVs, maps, examples).
- Change attribution text or upstream license references.

## Notice Entry Template

Copy this block for each item:

```markdown
### <Component or dependency name>

- Source: <URL to upstream project or source location>
- Version/commit used: <version, tag, or commit hash>
- License: <SPDX identifier or license name>
- Copyright: <copyright holder text>
- Used in: <repo path(s)>
- Modifications: <none | brief summary>
- Required notice text:

  > <exact attribution/notice text, if required>
```

## Current Notices

_No additional third-party notices are currently recorded._

Last attribution review: **July 21, 2026**.

## Release Checklist (Attribution)

Before tagging a release:

1. Confirm `LICENSE` is present and unchanged unless legal terms changed.
2. Verify new dependencies are license-compatible with Apache-2.0 distribution.
3. Confirm any vendored/bundled third-party content is listed above.
4. Ensure required notice text is included exactly where required.

## Helpful Commands

Example dependency license inventory (run from repo root):

**Windows (PowerShell):**

```powershell
python -m pip install pip-licenses
python -m piplicenses --format=markdown --with-urls --with-license-file
```

**Linux/macOS (bash):**

```bash
python -m pip install pip-licenses
python -m piplicenses --format=markdown --with-urls --with-license-file
```

Use the command output as input for review, then keep curated final notices in this file.

You can also run the repository compliance helper:

**Windows (PowerShell):**

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release_compliance_check.ps1
```

**Linux/macOS (bash):**

```bash
pwsh -ExecutionPolicy Bypass -File ./scripts/release_compliance_check.ps1
```
