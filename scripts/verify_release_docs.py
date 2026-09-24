#!/usr/bin/env python3
"""Validate release-facing docs against a tagged release version."""

from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ReleaseDocCheck:
    """A single release-doc expectation."""

    path: str
    description: str
    pattern_template: str


RELEASE_DOC_CHECKS: tuple[ReleaseDocCheck, ...] = (
    ReleaseDocCheck(
        path="README.md",
        description="release/status banner",
        pattern_template=r"^\*\*Status:\*\* Stable \(v{version}\+\)",
    ),
    ReleaseDocCheck(
        path="IMPROVEMENT_ROADMAP.md",
        description="roadmap version baseline",
        pattern_template=r"^\*Status: Active roadmap aligned to `v{version}`",
    ),
    ReleaseDocCheck(
        path="CHANGELOG.md",
        description="matching release changelog section",
        pattern_template=r"^## \[{version}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
    ),
)

EXACT_SEMVER_RE = re.compile(
    r"^(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?$"
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _read_project_version(repo_root: Path) -> str:
    with (repo_root / "pyproject.toml").open("rb") as fh:
        pyproject = tomllib.load(fh)
    return pyproject["project"]["version"]


def _release_type(version: str) -> str:
    """Return the release type for a semantic version string."""
    match = EXACT_SEMVER_RE.fullmatch(version)
    if not match:
        return "unknown"

    major = int(match.group("major"))
    minor = int(match.group("minor"))
    patch = int(match.group("patch"))

    if patch > 0:
        return "patch"
    if minor > 0:
        return "minor"
    if major > 0:
        return "major"
    return "unknown"


def _verify_security_support_table(version: str, repo_root: Path) -> list[str]:
    """Return SECURITY.md validation errors for non-patch releases."""
    match = EXACT_SEMVER_RE.fullmatch(version)
    if not match or _release_type(version) not in {"major", "minor"}:
        return []

    major = int(match.group("major"))
    next_major = major + 1
    security_path = repo_root / "SECURITY.md"
    if not security_path.exists():
        return ["SECURITY.md: missing file"]

    text = security_path.read_text(encoding="utf-8")
    support_pattern = (
        rf"^\|\s*{major}\.x\s*\|\s*Active\s*\|\s*"
        rf"Until next major release \(`v{next_major}\.0\.0`\)\s*\|$"
    )
    if not re.search(support_pattern, text, flags=re.MULTILINE):
        return [
            f"SECURITY.md: expected supported-version table row for {major}.x active support through v{next_major}.0.0"
        ]

    return []


def verify_release_docs(version: str, repo_root: Path) -> list[str]:
    """Return a list of release-doc validation errors for the supplied version."""
    errors: list[str] = []

    for check in RELEASE_DOC_CHECKS:
        doc_path = repo_root / check.path
        if not doc_path.exists():
            errors.append(f"{check.path}: missing file")
            continue

        text = doc_path.read_text(encoding="utf-8")
        pattern = check.pattern_template.format(version=re.escape(version))
        if not re.search(pattern, text, flags=re.MULTILINE):
            errors.append(f"{check.path}: expected {check.description} for v{version}")

    errors.extend(_verify_security_support_table(version, repo_root))

    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate release-facing docs after a version bump or tag.",
    )
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=_repo_root(),
        help="Repository root to inspect (defaults to the repo containing this script).",
    )
    parser.add_argument(
        "--version",
        help="Release version to verify (defaults to pyproject.toml project.version).",
    )
    args = parser.parse_args(argv)

    repo_root = args.repo_root.resolve()
    if not repo_root.exists():
        print(f"[release-docs] repo root not found: {repo_root}", file=sys.stderr)
        return 2

    version = args.version or _read_project_version(repo_root)
    errors = verify_release_docs(version, repo_root)
    if errors:
        print(
            f"[release-docs] documentation checks failed for v{version}",
            file=sys.stderr,
        )
        for error in errors:
            print(f"[release-docs] - {error}", file=sys.stderr)
        return 1

    print(f"[release-docs] release-facing docs match v{version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
