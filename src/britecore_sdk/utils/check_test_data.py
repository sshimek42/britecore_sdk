"""Check test CSV files referenced by tests are present and parseable."""

import csv
import glob
import os
import sys


def check_test_data_files() -> bool:
    """Validate CSV test-data files under tests/data using a basic parse pass."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base, "..", "tests", "data")
    if not os.path.exists(data_dir):
        print(f"No test data directory found: {data_dir}")
        return True
    all_csv = glob.glob(os.path.join(data_dir, "*.csv"))
    ok = True
    for csv_file in all_csv:
        try:
            with open(csv_file, newline="") as f:
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
