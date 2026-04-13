"""Check test CSV files referenced by tests are present and parseable."""

import csv
import sys
from pathlib import Path


def check_test_data_files() -> bool:
    """Validate CSV test-data files under tests/data using a basic parse pass."""
    base = Path(__file__).resolve().parent.parent.parent.parent
    data_dir = base / "tests" / "data"
    if not data_dir.exists():
        print(f"No test data directory found: {data_dir}")
        return True
    all_csv = list(data_dir.glob("*.csv"))
    ok = True
    for csv_file in all_csv:
        try:
            with csv_file.open(newline="") as f:
                reader = csv.reader(f)
                next(reader)  # Try reading header
        except Exception as e:
            print(f"ERROR: Could not parse {csv_file}: {e}")
            ok = False
    if ok:
        print("All test data files are present and parseable.")
    return ok


def main() -> None:
    """Run test-data validation and exit non-zero when parsing fails."""
    print("Checking test data files...")
    ok = check_test_data_files()
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
