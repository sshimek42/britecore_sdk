# Branch Hygiene Guide

*Last updated: September 24, 2026*
*Document type: Living guide*

This guide defines a lightweight branch-cleanup routine for solo maintenance.

## Purpose

Keep local and remote branches easy to reason about, reduce stale context, and avoid accidentally reviving outdated release prep work.

## Branch Categories

- **Active work branches**: open PRs or current in-progress tasks.
- **Archive branches**: release/history branches intentionally retained (for example `release/2.5.x`).
- **Disposable branches**: merged or superseded branches that can be deleted.

## Monthly 30-Second Cleanup

From the repository root:

```powershell
git fetch --prune
git branch --no-merged master
git branch --merged master
```

Then apply this policy:

1. Delete local branches fully merged into `master`:
   - `git branch -d <branch>`
2. If branch commits are patch-equivalent but not graph-merged, confirm first, then force-delete:
   - `git cherry -v master <branch>`
   - `git branch -D <branch>`
3. Keep only one release archive branch per active release train.

## Safety Checks Before Force Deleting

Run all three checks:

```powershell
git log --oneline master..<branch>
git cherry -v master <branch>
git diff --stat master...<branch>
```

Force-delete only when the branch is either:
- patch-equivalent to `master`, or
- stale/superseded and intentionally discarded.

## Recommended Keep List

- `master`
- current release branch(es) still relevant for hotfixes
- one archive release branch for recent release context

## Recommended Delete List

- merged feature branches
- superseded release-prep branches
- abandoned local experiment branches with no current roadmap value

## Notes for Solo Maintainers

- Favor short-lived branches and small PRs.
- Resolve or archive old branches immediately after merge windows.
- Record exceptional keep/delete decisions in `docs/DECISIONS.md` (if present).
