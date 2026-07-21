#!/usr/bin/env python3
"""Fix malformed docstrings with duplicate endpoint information."""

import re
from pathlib import Path

API_V2_DIR = Path("src/britecore_sdk/api/api_calls/v2")


def fix_file(file_path: Path) -> int:
    """Fix malformed docstrings in a file. Returns the number of fixes made."""
    if not file_path.exists():
        return 0
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Pattern: ). (POST /api/v2/...)) followed by """
    # Match endpoint paths like /api/v2/authority_limits/get_authority_limit
    # Paths don't contain ), so [^)]+ matches the path
    pattern = r'\). \(POST /api/v2/[^)]*\)\)"""'
    content = re.sub(pattern, ')."""', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        # Count fixes
        fixes = len(re.findall(pattern, original_content))
        return fixes
    
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

