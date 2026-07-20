"""Check for unresolved type: ignore comments.

This script identifies type: ignore comments that should be resolved
or documented as needed.
"""

import sys
from pathlib import Path


def check_file(filepath: str) -> list[str]:
    """Check a file for unresolved type: ignore comments.

    Args:
        filepath: Path to Python file.

    Returns:
        List of issues found.
    """
    issues = []
    path = Path(filepath)

    if not path.exists() or not path.suffix == ".py":
        return issues

    content = path.read_text()
    for line_num, line in enumerate(content.splitlines(), 1):
        if "type: ignore" in line:
            # Flag any type: ignore that looks suspicious
            if "[assignment]" in line or "[arg-type]" in line:
                # These are expected and documented
                continue

            # Check if there's a reason after the comment
            if not any(marker in line for marker in ["[", ":"]):
                issues.append(f"{filepath}:{line_num}: type: ignore without reason")

    return issues


def main():
    """Main entry point."""
    total_issues = []

    for arg in sys.argv[1:]:
        issues = check_file(arg)
        total_issues.extend(issues)

    if total_issues:
        for issue in total_issues:
            print(issue)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
