#!/usr/bin/env python3
"""Enforce release-tag policy for GitHub release smoke checks."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

EXACT_SEMVER_RE = re.compile(r"^v(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)$")
BREAK_GLASS_RE = re.compile(r"\[break-glass\]", flags=re.IGNORECASE)
GITHUB_API_TIMEOUT_SECONDS = 15


@dataclass(frozen=True)
class ReleasePolicyResult:
    """Outcome of evaluating a release tag against the policy."""

    exit_code: int
    message: str


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve_git_executable() -> str:
    git_executable = shutil.which("git")
    if not git_executable:
        raise RuntimeError("git executable not found in PATH")
    return git_executable


def _run_git(repo_root: Path, *args: str) -> str:
    return subprocess.check_output(
        [_resolve_git_executable(), *args],
        cwd=str(repo_root),
        text=True,
    )


def _read_tag_contents(tag_name: str, repo_root: Path) -> str:
    try:
        return _run_git(
            repo_root,
            "for-each-ref",
            f"refs/tags/{tag_name}",
            "--format=%(contents)",
        ).strip()
    except subprocess.CalledProcessError:
        return ""


def _list_version_tags(repo_root: Path) -> list[str]:
    tags = _run_git(repo_root, "tag", "--list", "v*.*.*").splitlines()
    return [tag.strip() for tag in tags if tag.strip()]


def determine_release_type(tag_name: str, version_tags: list[str]) -> tuple[str, str]:
    """Return the release type and the previous tag for an exact SemVer tag."""
    match = EXACT_SEMVER_RE.fullmatch(tag_name)
    if not match:
        return "prerelease", "none"

    current = tuple(int(part) for part in match.groups())
    versions: list[tuple[tuple[int, int, int], str]] = []
    for item in version_tags:
        other = EXACT_SEMVER_RE.fullmatch(item)
        if other and item != tag_name:
            major, minor, patch = (int(part) for part in other.groups())
            versions.append(((major, minor, patch), item))

    previous = [candidate for candidate in versions if candidate[0] < current]
    if not previous:
        return "major", "none"

    previous_version, previous_tag = max(previous, key=lambda item: item[0])
    if current[0] > previous_version[0]:
        return "major", previous_tag
    if current[1] > previous_version[1]:
        return "minor", previous_tag
    if current[2] > previous_version[2]:
        return "patch", previous_tag
    return "unknown", previous_tag


def has_break_glass_marker(tag_contents: str) -> bool:
    """Return True when the tag annotation includes the literal [break-glass] marker."""
    return bool(BREAK_GLASS_RE.search(tag_contents))


def _fetch_associated_pull_requests(
    repo: str, commit_sha: str, token: str | None
) -> list[dict[str, Any]]:
    url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}/pulls"
    parsed_url = urlsplit(url)
    if parsed_url.scheme != "https" or parsed_url.netloc != "api.github.com":
        raise RuntimeError("GitHub API URL must use https://api.github.com")

    headers = {
        "Accept": "application/vnd.github.groot-preview+json, application/vnd.github+json",
        "User-Agent": "britecore-sdk-release-smoke-policy",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers, method="GET")
    try:
        with urlopen(request, timeout=GITHUB_API_TIMEOUT_SECONDS) as response:
            payload = response.read().decode("utf-8")
    except HTTPError as exc:
        raise RuntimeError(
            f"GitHub API request failed with HTTP {exc.code}: {exc.reason}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc

    data = json.loads(payload)
    if not isinstance(data, list):
        raise RuntimeError(
            "GitHub API returned an unexpected payload for commit PR associations"
        )

    return [item for item in data if isinstance(item, dict)]


def _format_pr_refs(
    pulls: list[dict[str, Any]], *, merged_only: bool | None = None
) -> str:
    refs: list[str] = []
    for pull in pulls:
        is_merged = bool(pull.get("merged_at"))
        if merged_only is True and not is_merged:
            continue
        if merged_only is False and is_merged:
            continue
        number = pull.get("number")
        if isinstance(number, int):
            refs.append(f"#{number}")
    return ", ".join(refs)


def evaluate_release_policy(
    release_type: str,
    pulls: list[dict[str, Any]],
    break_glass: bool,
) -> ReleasePolicyResult:
    """Return the policy result for a release tag and associated PRs."""
    merged_refs = _format_pr_refs(pulls, merged_only=True)
    all_refs = _format_pr_refs(pulls, merged_only=None)

    if release_type in {"major", "minor", "prerelease"}:
        if merged_refs:
            return ReleasePolicyResult(
                0,
                f"Tag commit is associated with merged PR(s): {merged_refs}",
            )
        if all_refs:
            return ReleasePolicyResult(
                1,
                (
                    f"Release policy violation: {release_type} tags must point to a commit associated with "
                    f"at least one merged PR. Found open/unmerged PR(s): {all_refs}. Merge the PR(s) first."
                ),
            )
        return ReleasePolicyResult(
            1,
            (
                f"Release policy violation: {release_type} tags must point to a commit associated with "
                "at least one merged PR. No PR associations were found."
            ),
        )

    if release_type == "patch":
        if merged_refs:
            return ReleasePolicyResult(
                0,
                f"Tag commit is associated with merged PR(s): {merged_refs}",
            )
        if break_glass:
            return ReleasePolicyResult(
                0,
                (
                    "Emergency break-glass patch tag detected without a merged PR association. "
                    "Open a follow-up PR immediately for auditability."
                ),
            )
        if all_refs:
            return ReleasePolicyResult(
                1,
                (
                    "Release policy violation: patch tags with only open/unmerged PR associations still require "
                    f"a merged PR or an annotated tag message containing [break-glass]. Found PR(s): {all_refs}."
                ),
            )
        return ReleasePolicyResult(
            1,
            (
                "Release policy violation: patch tags without a merged PR association require an annotated tag "
                "message containing [break-glass]."
            ),
        )

    return ReleasePolicyResult(
        1,
        f"Release policy violation: unsupported release type '{release_type}'.",
    )


def main(argv: list[str] | None = None) -> int:
    """Validate release policy for the current release tag."""
    parser = argparse.ArgumentParser(
        description="Validate release-tag policy for the release smoke workflow.",
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="GitHub repository in owner/repo form (defaults to GITHUB_REPOSITORY).",
    )
    parser.add_argument(
        "--tag",
        default=os.environ.get("GITHUB_REF_NAME", ""),
        help="Release tag name to evaluate (defaults to GITHUB_REF_NAME).",
    )
    parser.add_argument(
        "--sha",
        default=os.environ.get("GITHUB_SHA", ""),
        help="Commit SHA the tag points to (defaults to GITHUB_SHA).",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN", ""),
        help="GitHub token for commit-to-PR lookup (defaults to GITHUB_TOKEN).",
    )
    args = parser.parse_args(argv)

    repo_root = _repo_root()
    if not args.repo:
        print(
            "[release-policy] missing repository context (set --repo or GITHUB_REPOSITORY)",
            file=sys.stderr,
        )
        return 2
    if not args.tag:
        print(
            "[release-policy] missing tag context (set --tag or GITHUB_REF_NAME)",
            file=sys.stderr,
        )
        return 2
    if not args.sha:
        print(
            "[release-policy] missing commit context (set --sha or GITHUB_SHA)",
            file=sys.stderr,
        )
        return 2

    release_type, previous_tag = determine_release_type(
        args.tag, _list_version_tags(repo_root)
    )
    tag_contents = _read_tag_contents(args.tag, repo_root)
    break_glass = has_break_glass_marker(tag_contents)

    try:
        pulls = _fetch_associated_pull_requests(args.repo, args.sha, args.token or None)
    except RuntimeError as exc:
        print(f"[release-policy] {exc}", file=sys.stderr)
        return 2

    merged_refs = _format_pr_refs(pulls, merged_only=True)
    all_refs = _format_pr_refs(pulls, merged_only=None)
    print(
        f"[release-policy] Release type: {release_type}; previous tag: {previous_tag}; "
        f"break-glass marker: {str(break_glass).lower()}; associated PR count: {len(pulls)}; "
        f"merged PR count: {len([pull for pull in pulls if pull.get('merged_at')])}"
    )

    result = evaluate_release_policy(release_type, pulls, break_glass)
    if result.exit_code != 0:
        print(result.message, file=sys.stderr)
        if all_refs:
            print(f"[release-policy] Associated PRs: {all_refs}", file=sys.stderr)
        return result.exit_code

    print(result.message)
    if release_type == "patch" and break_glass and not merged_refs:
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
