#!/usr/bin/env python3
"""Run local documentation QA checks (strict HTML build + link validation)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _run(cmd: list[str], cwd: Path) -> None:
    """Run a command and fail fast on non-zero exit."""
    print("[docs-qa] $", " ".join(cmd))
    subprocess.run(cmd, cwd=str(cwd), check=True)


def main() -> int:
    """Parse CLI args and run strict docs checks, returning process exit code."""
    parser = argparse.ArgumentParser(
        description="Run documentation QA checks used before PRs.",
    )
    parser.add_argument(
        "--skip-linkcheck",
        action="store_true",
        help="Only run strict HTML build and skip external link validation.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    docs_dir = repo_root / "docs"

    if not docs_dir.exists():
        print("[docs-qa] docs directory not found:", docs_dir, file=sys.stderr)
        return 2

    try:
        _run(
            [
                sys.executable,
                "-m",
                "sphinx",
                "-W",
                "--keep-going",
                "-b",
                "html",
                "docs",
                "docs/_build/html-strict",
            ],
            cwd=repo_root,
        )

        if not args.skip_linkcheck:
            _run(
                [
                    sys.executable,
                    "-m",
                    "sphinx",
                    "-b",
                    "linkcheck",
                    "docs",
                    "docs/_build/linkcheck",
                ],
                cwd=repo_root,
            )

    except subprocess.CalledProcessError as exc:
        print(f"[docs-qa] failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode

    print("[docs-qa] all checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
