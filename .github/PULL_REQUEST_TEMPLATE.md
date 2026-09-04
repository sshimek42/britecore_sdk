## Summary

<!-- Describe what this PR does and why. Link related issues if applicable (e.g., Closes #123). -->

## Change type

<!-- Check all that apply. -->

- [ ] Bug fix
- [ ] New feature / endpoint wrapper
- [ ] Refactor / internal improvement
- [ ] Documentation update
- [ ] Dependency update
- [ ] Other: <!-- describe -->

## Checklist

- [ ] Tests pass locally for changed behavior (`python -m pytest tests/unit -m unit -v`)
- [ ] Docs updated when public behavior or usage changes
- [ ] New exports added to relevant `__all__` lists
- [ ] New endpoint wrappers follow the existing `v2` request/response pattern
- [ ] Config/env assumptions are documented if needed
- [ ] No secrets or credentials are committed

## Release PR checklist (required when cutting a release)

- [ ] Not a release PR, or I selected the release type below:
  - [ ] Patch (for example, `v1.2.4`)
  - [ ] Minor (for example, `v1.3.0`)
  - [ ] Major (for example, `v2.0.0`)
  - [ ] Prerelease (for example, `v1.2.4-rc.1`, `v1.2.4-beta.1`, etc.)
- [ ] Not a release PR, or I completed `docs/DOCUMENTATION_RELEASE_CHECKLIST.md`
- [ ] Not a release PR, or I completed `docs/RELEASE_OPERATIONS_CHECKLIST.md`
- [ ] Not a release PR, or tag/version/changelog are aligned (`vX.Y.Z`, `pyproject.toml`, `CHANGELOG.md`)
- [ ] Not a release PR, or (minor/major) this release will be cut from this merged PR
- [ ] Not a release PR, or (patch exception) I linked the break-glass incident and completed `docs/RELEASE_HOTFIX_TEMPLATE.md`

## Break-glass patch follow-up (required only for emergency no-PR patch releases)

- [ ] Not applicable, or this PR is the required follow-up PR after a break-glass patch release
- [ ] Not applicable, or incident/ticket is linked in the PR description
- [ ] Not applicable, or completed hotfix record is linked: `docs/RELEASE_HOTFIX_TEMPLATE.md`
- [ ] Not applicable, or tag message included `[break-glass]` and the tag is referenced here

## Testing notes

<!-- Describe how you tested this change. Include any edge cases or manual steps. -->
