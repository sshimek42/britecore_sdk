#!/usr/bin/env python3
"""
Shared CI script for type checking, linting, and testing.
- Type checks: mypy
- Lint: ruff, black (check only)
- Tests: pytest (unit and coverage)

Usage:
  python scripts/ci_typecheck.py
"""

import subprocess
import sys
from collections.abc import Sequence


def run(cmd: Sequence[str], desc: str) -> None:
    """Execute a CI step and exit immediately if it fails."""
    print(f"\n=== {desc} ===")
    result = subprocess.run(cmd, check=False)
    if result.returncode != 0:
        print(f"FAILED: {desc}")
        sys.exit(result.returncode)


def main() -> None:
    """Run lint, type-checking, and unit-test steps for CI."""
    # Lint
    run(["ruff", "check", "src", "tests"], "Lint (ruff)")
    run(["black", "--check", "src", "tests"], "Format check (black)")

    # Type check
    run(
        [
            "mypy",
            "src/britecore_sdk/exceptions.py",
            "src/britecore_sdk/api/britecore_api_client.py",
            "src/britecore_sdk/api/britecore_async_api_client.py",
            "src/britecore_sdk/api/britecore_oauth_token_manager.py",
            "src/britecore_sdk/api/request_cache.py",
            "src/britecore_sdk/api/types.py",
            "src/britecore_sdk/api/api_calls/v1",
            "src/britecore_sdk/api/api_calls/v2",
            "src/britecore_sdk/config/config.py",
            "src/britecore_sdk/maps/__init__.py",
            "src/britecore_sdk/models",
            "src/britecore_sdk/validators",
        ],
        "Type check (mypy)",
    )

    # Unit tests
    run(
        [
            "pytest",
            "tests/unit",
            "-m",
            "unit",
            "--cov=src/britecore_sdk",
            "--cov-report=term-missing",
            "--cov-fail-under=60",
        ],
        "Unit tests",
    )


if __name__ == "__main__":
    main()
