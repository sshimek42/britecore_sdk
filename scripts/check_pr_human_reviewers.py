#!/usr/bin/env python3
"""List or count human pull request reviewers via GitHub CLI.

This helper wraps `gh api` with a jq filter that keeps only human review
accounts (`.user.type == "User"`) and ignores bots/apps. It can:

- print the human review rows for a PR
- print a unique human-reviewer count
- auto-approve a PR when only the current human maintainer is eligible
- fail if the count exceeds a chosen maximum

Examples:
    python scripts/check_pr_human_reviewers.py sshimek42 britecore_sdk 239
    python scripts/check_pr_human_reviewers.py sshimek42 britecore_sdk 239 --count
    python scripts/check_pr_human_reviewers.py sshimek42 britecore_sdk 239 --max-human-reviewers 1
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class ReviewRow:
    """A single human review row."""

    reviewer: str
    state: str


@dataclass(frozen=True)
class ReviewSummary:
    """Human-review summary for a pull request."""

    rows: list[ReviewRow]
    count: int
    approvals: int


def _run_gh_api(owner: str, repo: str, pr_number: int, jq_expr: str) -> str:
    """Run gh api against PR reviews and return stdout."""
    cmd = [
        "gh",
        "api",
        f"repos/{owner}/{repo}/pulls/{pr_number}/reviews",
        "--paginate",
        "--jq",
        jq_expr,
    ]
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def _run_gh_command(cmd: list[str]) -> str:
    """Run a gh command and return stdout."""
    completed = subprocess.run(cmd, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def _parse_review_rows(output: str) -> list[ReviewRow]:
    """Parse newline-delimited JSON review rows from gh api output."""
    rows: list[ReviewRow] = []
    if not output:
        return rows

    for line in output.splitlines():
        payload = json.loads(line)
        rows.append(ReviewRow(reviewer=payload["reviewer"], state=payload["state"]))

    return rows


def summarize_reviews(owner: str, repo: str, pr_number: int) -> ReviewSummary:
    """Return human-review rows and the unique human-reviewer count."""
    list_expr = (
        '.[] | select(.user.type == "User") | {reviewer: .user.login, state: .state}'
    )
    count_expr = '[.[] | select(.user.type == "User") | .user.login] | unique | length'

    output = _run_gh_api(owner, repo, pr_number, list_expr)
    rows = _parse_review_rows(output)
    count_text = _run_gh_api(owner, repo, pr_number, count_expr)
    count = int(count_text or "0")
    approvals = sum(1 for row in rows if row.state == "APPROVED")
    return ReviewSummary(rows=rows, count=count, approvals=approvals)


def _current_user_login() -> str:
    """Return the authenticated gh user login."""
    return _run_gh_command(["gh", "api", "user", "--jq", ".login"])


def _pr_author_login(owner: str, repo: str, pr_number: int) -> str:
    """Return the PR author's login."""
    return _run_gh_command(
        [
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--repo",
            f"{owner}/{repo}",
            "--json",
            "author",
            "--jq",
            ".author.login",
        ]
    )


def approve_if_solo_human(owner: str, repo: str, pr_number: int) -> bool:
    """Approve the PR if there are no other human reviewers to defer to."""
    summary = summarize_reviews(owner, repo, pr_number)
    current_login = _current_user_login()
    author_login = _pr_author_login(owner, repo, pr_number)
    human_reviewers = {row.reviewer for row in summary.rows}

    if current_login == author_login:
        raise ValueError("GitHub blocks self-approval on your own pull request")

    if current_login in {
        row.reviewer for row in summary.rows if row.state == "APPROVED"
    }:
        return True

    if human_reviewers and human_reviewers != {current_login}:
        return False

    _run_gh_command(
        ["gh", "pr", "review", str(pr_number), "--approve", "--repo", f"{owner}/{repo}"]
    )
    return True


def parse_args(argv: list[str]) -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(
        description="List or count human reviewers on a pull request using gh api and jq.",
    )
    parser.add_argument("owner", help="Repository owner/org login.")
    parser.add_argument("repo", help="Repository name.")
    parser.add_argument("pr_number", type=int, help="Pull request number.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--count",
        action="store_true",
        help="Print the unique human-reviewer count instead of the review rows.",
    )
    mode.add_argument(
        "--approve-if-solo-human",
        action="store_true",
        help="Auto-approve the PR when there are no other human reviewers to defer to.",
    )
    parser.add_argument(
        "--max-human-reviewers",
        type=int,
        default=None,
        help="Fail with exit code 1 if the unique human-reviewer count exceeds this limit.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """Run the reviewer summary command and return a shell exit code."""
    args = parse_args(sys.argv[1:] if argv is None else argv)

    try:
        summary = summarize_reviews(args.owner, args.repo, args.pr_number)
    except FileNotFoundError:
        print("error: gh is not installed or not on PATH", file=sys.stderr)
        return 127
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else ""
        if stderr:
            print(stderr, file=sys.stderr)
        return exc.returncode or 1

    if (
        args.max_human_reviewers is not None
        and summary.count > args.max_human_reviewers
    ):
        print(
            f"human reviewer count {summary.count} exceeds limit {args.max_human_reviewers}",
            file=sys.stderr,
        )
        return 1

    if args.approve_if_solo_human:
        try:
            approved = approve_if_solo_human(args.owner, args.repo, args.pr_number)
        except FileNotFoundError:
            print("error: gh is not installed or not on PATH", file=sys.stderr)
            return 127
        except ValueError as exc:
            print(f"skipping auto-approval: {exc}", file=sys.stderr)
            return 2
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() if exc.stderr else ""
            if stderr:
                print(stderr, file=sys.stderr)
            return exc.returncode or 1

        if approved:
            print("approved")
            return 0

        print(
            "skipping auto-approval: more than one human reviewer is present on this PR",
            file=sys.stderr,
        )
        return 2

    if args.count:
        print(summary.count)
    else:
        for row in summary.rows:
            print(json.dumps({"reviewer": row.reviewer, "state": row.state}))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
