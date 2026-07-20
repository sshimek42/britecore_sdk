#!/usr/bin/env python3
"""Check authored Markdown files for renderer-unsafe structure issues.

This lightweight check focuses on the specific regressions that previously caused
sections to render as one smashed text block in Markdown viewers:

- unclosed fenced code blocks
- standalone checklist-style emoji lines that are not real Markdown list items

It intentionally ignores generated/output directories and skips content inside
fenced code blocks when checking checklist-style lines.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXCLUDED_PARTS = {
    "build",
    "dist",
    "env",
    ".venv",
    "htmlcov",
    "docs/_build",
}
CHECKLIST_EMOJI_RE = re.compile(r"^\s*[✅❌⏳📋]\s+")
FENCE_RE = re.compile(r"^\s*([`~]{3,})(.*)$")


@dataclass(frozen=True)
class MarkdownIssue:
    """A Markdown structure issue found in a file."""

    path: Path
    line_number: int
    message: str


def _is_excluded(path: Path) -> bool:
    """Return True when a path is inside a generated/output directory."""
    path_text = path.as_posix()
    if ".egg-info" in path_text:
        return True
    return (
        any(part in path.parts for part in EXCLUDED_PARTS) or "docs/_build" in path_text
    )


def iter_markdown_files(root: Path, paths: Iterable[str] | None = None) -> list[Path]:
    """Return authored Markdown files to check.

    Args:
        root: Repository root.
        paths: Optional file or directory paths supplied by a caller such as
            pre-commit. When omitted, all authored Markdown files under the
            repository root are scanned.

    Returns:
        A sorted list of authored Markdown file paths.
    """
    candidates: set[Path] = set()

    if paths:
        for raw_path in paths:
            candidate = Path(raw_path)
            if not candidate.is_absolute():
                candidate = (root / candidate).resolve()
            if not candidate.exists():
                continue
            if candidate.is_dir():
                for subpath in candidate.rglob("*.md"):
                    if not _is_excluded(subpath.relative_to(root)):
                        candidates.add(subpath)
            elif candidate.suffix.lower() == ".md":
                try:
                    relative = candidate.relative_to(root)
                except ValueError:
                    continue
                if not _is_excluded(relative):
                    candidates.add(candidate)
    else:
        for subpath in root.rglob("*.md"):
            relative = subpath.relative_to(root)
            if not _is_excluded(relative):
                candidates.add(subpath)

    return sorted(candidates)


def analyze_markdown_text(text: str, path: Path) -> list[MarkdownIssue]:
    """Analyze Markdown content and return structure issues."""
    issues: list[MarkdownIssue] = []
    in_fence = False
    fence_char = ""
    fence_length = 0

    for line_number, line in enumerate(text.splitlines(), start=1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            marker_char = marker[0]
            marker_length = len(marker)
            if not in_fence:
                in_fence = True
                fence_char = marker_char
                fence_length = marker_length
            elif marker_char == fence_char and marker_length >= fence_length:
                in_fence = False
                fence_char = ""
                fence_length = 0
            continue

        if in_fence:
            continue

        if CHECKLIST_EMOJI_RE.match(line):
            issues.append(
                MarkdownIssue(
                    path=path,
                    line_number=line_number,
                    message=(
                        "Standalone checklist-style emoji line should use a real "
                        "Markdown list marker like '- ✅'."
                    ),
                )
            )

    if in_fence:
        issues.append(
            MarkdownIssue(
                path=path,
                line_number=max(1, len(text.splitlines())),
                message="Unclosed fenced code block.",
            )
        )

    return issues


def analyze_markdown_file(path: Path) -> list[MarkdownIssue]:
    """Read and analyze one Markdown file."""
    return analyze_markdown_text(path.read_text(encoding="utf-8"), path)


def format_issue(issue: MarkdownIssue, root: Path) -> str:
    """Format an issue for human-readable CLI output."""
    return f"{issue.path.relative_to(root)}:{issue.line_number}: {issue.message}"


def main(argv: list[str] | None = None) -> int:
    """Run the Markdown structure check.

    Args:
        argv: Optional CLI-style arguments containing file or directory paths.

    Returns:
        Process exit code: 0 when no issues are found, otherwise 1.
    """
    scan_paths = list(argv) if argv is not None else sys.argv[1:]
    markdown_files = iter_markdown_files(REPO_ROOT, scan_paths)

    issues: list[MarkdownIssue] = []
    for markdown_file in markdown_files:
        issues.extend(analyze_markdown_file(markdown_file))

    if issues:
        for issue in issues:
            # Use sys.stdout.buffer to safely write UTF-8 on any platform (avoids
            # UnicodeEncodeError on Windows cp1252 terminals when emoji are present).
            sys.stdout.buffer.write(
                (format_issue(issue, REPO_ROOT) + "\n").encode("utf-8")
            )
        sys.stdout.buffer.write(
            f"Found {len(issues)} Markdown structure issue(s).\n".encode()
        )
        return 1

    sys.stdout.buffer.write(
        f"Markdown structure check passed for {len(markdown_files)} file(s).\n".encode()
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
