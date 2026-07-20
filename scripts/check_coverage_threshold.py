"""Script to enforce coverage thresholds in CI/CD.

This script checks test coverage and fails if it drops below the threshold.
"""

import re
import subprocess
import sys


def get_coverage_percentage() -> float:
    """Get overall coverage percentage from pytest-cov.

    Returns:
        Coverage percentage as float (0-100).
    """
    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "--cov=britecore_sdk",
                "--cov-report=term-missing",
                "--no-header",
                "-q",
            ],
            capture_output=True,
            text=True,
        )

        output = result.stdout + result.stderr

        # Look for coverage line like "TOTAL 1234 567 54%"
        match = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", output)
        if match:
            return float(match.group(1))

        return 0.0
    except Exception as e:
        print(f"Error running coverage: {e}")
        return 0.0


def main(threshold: float = 75.0):
    """Check coverage against threshold.

    Args:
        threshold: Minimum coverage percentage (default 75%).

    Returns:
        Exit code (0 if coverage >= threshold, 1 otherwise).
    """
    print(f"Checking coverage threshold: {threshold}%")

    coverage = get_coverage_percentage()
    print(f"Current coverage: {coverage}%")

    if coverage < threshold:
        print(f"❌ Coverage {coverage}% is below threshold {threshold}%")
        return 1
    else:
        print(f"✅ Coverage {coverage}% meets threshold {threshold}%")
        return 0


if __name__ == "__main__":
    threshold = float(sys.argv[1]) if len(sys.argv) > 1 else 75.0
    sys.exit(main(threshold))
