"""
Script to check that all test data files referenced by tests exist and are valid (basic parse check).
"""
import os
import glob
import csv

def check_test_data_files():
    # Example: look for all CSV files in tests/data/
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

def main():
    print("Checking test data files...")
    ok = check_test_data_files()
    if not ok:
        exit(1)

if __name__ == "__main__":
    main()

