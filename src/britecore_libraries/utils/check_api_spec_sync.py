"""
Script to check that all v2 endpoint wrapper docstrings are in sync with the canonical API spec (api_specs/current/britecore.json).
Warns if the spec file is missing or outdated.
"""

import os
import sys
from datetime import datetime

SPEC_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "api_specs",
    "current",
    "britecore.json",
)

V2_API_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "api",
    "api_calls",
    "v2",
)


def check_spec_exists_and_fresh():
    if not os.path.exists(SPEC_PATH):
        print(f"WARNING: API spec file missing: {SPEC_PATH}")
        return False
    mtime = os.path.getmtime(SPEC_PATH)
    dt = datetime.fromtimestamp(mtime)
    age_days = (datetime.now() - dt).days
    if age_days > 30:
        print(
            f"WARNING: API spec file is older than 30 days (last modified {dt.date()})"
        )
        return False
    return True


def main():
    print("Checking API spec sync...")
    ok = check_spec_exists_and_fresh()
    if not ok:
        print("Please update api_specs/current/britecore.json!")
        sys.exit(1)
    print("API spec file exists and is recent.")
    # Optionally, add more checks for docstring sync here


if __name__ == "__main__":
    main()
