# Branch Protection Baseline

*Last updated: September 24, 2026*
*Document type: Operations baseline*

This document snapshots the current branch-protection baseline for `britecore_sdk` and provides replayable commands for solo maintenance.

## Scope

Protected branches covered here:
- `master`
- `release/2.5.x`
- `release/2.4.x`

## Baseline Policy (Current)

All three branches currently share the same policy:

- **Require a pull request before merge**
- **Required status checks (strict/up-to-date):**
  - `Analyze (actions)`
  - `Analyze (python)`
  - `CodeQL`
  - `DeepSource: Secrets`
- **Additional CI jobs may run on pull requests, but only the checks above are currently configured as branch-protection requirements.**
- **Required approving reviews:** `0` (solo-pragmatic)
- **Dismiss stale reviews:** `true`
- **Require conversation resolution:** `true`
- **Enforce admins:** `true`
- **Require linear history:** `true`
- **Allow force pushes:** `false`
- **Allow deletions:** `false`
- **Block branch creation:** `false`
- **Allow fork syncing:** `false`

## Replay Commands

Use these commands to reapply the baseline after accidental drift.

```powershell
$fullProtectionBody = @'
{
  "required_status_checks": {
    "strict": true,
    "contexts": [
      "Analyze (actions)",
      "Analyze (python)",
      "CodeQL",
      "DeepSource: Secrets"
    ]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "require_last_push_approval": false,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": false
}
'@

# apply the full payload to each protected branch
$fullProtectionBody | gh api --method PUT repos/sshimek42/britecore_sdk/branches/master/protection --input -
$fullProtectionBody | gh api --method PUT repos/sshimek42/britecore_sdk/branches/release/2.5.x/protection --input -
$fullProtectionBody | gh api --method PUT repos/sshimek42/britecore_sdk/branches/release/2.4.x/protection --input -
```

## Verification Commands

```powershell
gh api repos/sshimek42/britecore_sdk/branches/master/protection
gh api repos/sshimek42/britecore_sdk/branches/release/2.5.x/protection
gh api repos/sshimek42/britecore_sdk/branches/release/2.4.x/protection
```

## Notes

- This baseline intentionally keeps CI gates high while avoiding approval bottlenecks for solo ownership.
- If required check names change (workflow renames), update this document in the same PR as the workflow change.
- This document records the exact live GitHub settings; broader governance docs should link back here instead of duplicating different approval or check lists.
