# Release Hotfix Template

*Last updated: September 4, 2026*
*Document type: Governance policy*

Use this template only when an emergency patch release is cut without a merged PR (break-glass path).

---

## Usage Rules

- Use this template for urgent production incidents only.
- The release tag must be an annotated tag and include `[break-glass]` in the tag message.
- Open a follow-up PR immediately after the release and link this completed template.

---

## Hotfix Record

```text
Hotfix release record

1) Incident context
- Incident ID / ticket:
- Start time (UTC):
- Customer impact summary:
- Why immediate release was required:

2) Release metadata
- Tag (vX.Y.Z):
- Tag type: annotated
- Tag message includes [break-glass]: yes/no
- Release owner:

3) Commit and diff traceability
- Commit SHA tagged:
- Compare link (previous tag -> hotfix tag):
- Files changed summary:

4) Validation performed
- Unit smoke status:
- Integration smoke status:
- Build status:
- Release compliance script status:
- Docs QA status (if docs changed):

5) Follow-up PR
- Follow-up PR link:
- Follow-up PR owner:
- Target merge deadline (UTC):

6) Rollback readiness
- Rollback plan:
- On-call owner for post-release watch:
- Observation window:

7) Approvals
- Release maintainer:
- QA/runtime reviewer:
- Security/compliance reviewer:
- Notes/exceptions:
```

---

## See Also

- [CONTRIBUTING.md](../CONTRIBUTING.md)
- [RELEASE_OPERATIONS_CHECKLIST](./RELEASE_OPERATIONS_CHECKLIST.md)
- [DOCUMENTATION_RELEASE_CHECKLIST](./DOCUMENTATION_RELEASE_CHECKLIST.md)
