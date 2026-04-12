"""Run repository health/config/data checks for local dev and CI."""

# pylint: disable=cyclic-import

import subprocess
import sys

SCRIPTS = [
    "check_site_configs.py",
    "check_api_spec_sync.py",
    "check_test_data.py",
]

UTILS_DIR = __file__.replace("run_all_checks.py", "")


def run_script(script: str) -> None:
    """Execute one check script and stop the run on first failure."""
    print(f"\n=== Running {script} ===")
    result = subprocess.run([sys.executable, UTILS_DIR + script], check=False)
    if result.returncode != 0:
        print(f"FAILED: {script}")
        sys.exit(result.returncode)
    print(f"PASSED: {script}")


def main() -> None:
    """Run each configured health check script and print final status."""
    for script in SCRIPTS:
        run_script(script)
    print("\nAll checks passed.")


if __name__ == "__main__":
    main()
