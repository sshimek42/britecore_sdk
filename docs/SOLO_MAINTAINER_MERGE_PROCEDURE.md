# Solo Maintainer Merge Procedure

*Last updated: September 4, 2026*
*Document type: Operational runbook*

Use this guide when you are the only maintainer on the repository and a pull request is otherwise ready to merge, but branch protection still requires an approval from another reviewer.

---

## When to use this procedure

Use this only when all of the following are true:

- You are the only active maintainer/reviewer available.
- All required status checks are green.
- All review comments are resolved.
- The PR is ready to merge, but you cannot approve your own PR.

If another reviewer is available, prefer the normal review-and-merge flow.

### Optional preflight: count human reviewers

Before relaxing any approval rules, you can list only human reviews on the PR and ignore bots/apps by filtering on `.user.type == "User"`.

```powershell
gh api "repos/OWNER/REPO/pulls/PR_NUMBER/reviews" --jq '.[] | select(.user.type == "User") | {reviewer: .user.login, state: .state}'
```

If you want a quick human-only count, use:

```powershell
gh api "repos/OWNER/REPO/pulls/PR_NUMBER/reviews" --jq '[.[] | select(.user.type == "User") | .user.login] | unique | length'
```

If you prefer a reusable wrapper, run:

```powershell
python scripts/check_pr_human_reviewers.py OWNER REPO PR_NUMBER --count
```

If you are the only human maintainer and you want the helper to submit the approval for you, run:

```powershell
python scripts/check_pr_human_reviewers.py OWNER REPO PR_NUMBER --approve-if-solo-human
```

Use this as a preflight check: if the PR has only one human reviewer available and you are operating as the sole maintainer, proceed with the temporary approval relaxation steps below for the merge window only.

> **Note:** GitHub blocks self-approval on your own pull request. For self-authored branches, use the temporary approval-relaxation path below or merge with admin privileges after the checks are green.

---

## Recommended approach

The safest solo-maintainer path is:

1. Keep the default branch protection in place for normal work.
2. Temporarily reduce the required approval count to `0`.
3. Keep required status checks enabled.
4. Resolve every review thread before merging.
5. Merge with admin privileges if needed.
6. Restore the original protection settings immediately after merging.

---

## Step-by-step

### 1) Verify the PR is ready

Before changing repository settings, confirm:

- All required checks have passed.
- The PR branch is up to date.
- Every review thread is resolved.
- No follow-up fix commits are still pending.

### 2) Temporarily relax the approval requirement

Set branch protection so that:

- `required_approving_review_count = 0`
- `require_code_owner_reviews = false`
- all required status checks remain enabled
- `enforce_admins` stays enabled
- force pushes and deletions remain disabled

This should be a short-lived change only for the merge window.

### 3) Resolve review threads

GitHub will not allow the merge while unresolved review threads remain open.

If you addressed the comments, resolve the thread after confirming the fix is in place.

### 4) Merge the PR

Use the admin merge path if GitHub still treats the branch as protected.

Example:

```powershell
gh pr merge 239 --squash --admin --delete-branch
```

Adjust the PR number as needed.

### 5) Restore branch protection

Immediately after the merge, restore the original settings:

- `required_approving_review_count = 1`
- `require_code_owner_reviews = true`
- keep the same required status checks
- keep `enforce_admins` enabled
- keep force pushes and deletions disabled

---

## Suggested verification commands

```powershell
gh pr view <pr-number> --json mergeStateStatus,statusCheckRollup,reviewDecision
```

```powershell
gh api repos/<owner>/<repo>/branches/master/protection
```

These commands help confirm that the PR is mergeable and that protection has been restored afterward.

---

## Notes

- Do not leave the approval count at `0` longer than necessary.
- If you expect to need this often, document the workflow in your team checklist and keep the temporary change as short as possible.
- If you later add another maintainer, return to the normal review-driven merge path.
