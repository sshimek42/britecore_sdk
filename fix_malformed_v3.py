#!/usr/bin/env python3
"""Fix malformed docstrings - simple regex approach."""

import re
from pathlib import Path

API_V2_DIR = Path("src/britecore_sdk/api/api_calls/v2")


def fix_file(file_path: Path) -> int:
    """Fix malformed docstrings in a file."""
    if not file_path.exists():
        return 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Simple approach: match "). (POST /api/v2/...)" and replace with just ")"
    # The key is to match from ). ( to the next ) that's followed by """
    # We use a non-capturing group and match greedily up to ))."""

    # Pattern: ). (POST [anything not containing )) ])). (POST [anything])"""
    # This is the duplicate endpoint
    # Replace pattern: "). (POST [path]).""" with just ")."""

    # Use a simple regex that matches the duplicate portion
    pattern = r'\)\. \(POST /api/v2/[a-z_/]*\)\)"""'
    content = re.sub(pattern, ')."""', content)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        count = len(re.findall(pattern, original_content))
        return count

    return 0


def main():
    """Fix all malformed docstrings."""
    total_fixed = 0

    for py_file in sorted(API_V2_DIR.glob("*.py")):
        fixed = fix_file(py_file)
        if fixed > 0:
            print(f"✓ {py_file.name}: {fixed} docstring(s) fixed")
            total_fixed += fixed

    print(f"\n{'=' * 60}")
    print(f"Total malformed docstrings fixed: {total_fixed}")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())

