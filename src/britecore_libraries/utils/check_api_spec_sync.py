"""Check that the canonical API spec file exists and is reasonably recent."""

import sys
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SPEC_PATH = REPO_ROOT / "api_specs" / "current" / "britecore.json"


def check_spec_exists_and_fresh() -> bool:
    """Return True when the canonical API spec exists and is <= 30 days old."""
    if not SPEC_PATH.exists():
        print(f"WARNING: API spec file missing: {SPEC_PATH}")
        return False
    mtime = SPEC_PATH.stat().st_mtime
    dt = datetime.fromtimestamp(mtime)
    age_days = (datetime.now() - dt).days
    if age_days > 30:
        print(
            f"WARNING: API spec file is older than 30 days (last modified {dt.date()})"
        )
        return False
    return True


def main() -> None:
    """Run the API spec freshness check and exit non-zero on failure."""
    print("Checking API spec sync...")
    ok = check_spec_exists_and_fresh()
    if not ok:
        print("Please update api_specs/current/britecore.json!")
        sys.exit(1)
    print("API spec file exists and is recent.")
    # Optionally, add more checks for docstring sync here


if __name__ == "__main__":
    main()
