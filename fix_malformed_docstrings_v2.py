#!/usr/bin/env python3
"""Fix malformed docstrings with simple string replacement."""

from pathlib import Path

API_V2_DIR = Path("src/britecore_sdk/api/api_calls/v2")


def fix_file(file_path: Path) -> int:
    """Fix malformed docstrings in a file by removing duplicate endpoint sections."""
    if not file_path.exists():
        return 0

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixes = 0

    # Process line by line to find and fix malformed docstrings
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Check if line has the malformed pattern: ). (POST ... )
        if '). (POST' in line and ')."""' in line:
            # Find the duplicate pattern and remove it
            # Pattern: ). (POST /api/v2/...). (POST /api/v2/...)."""
            # Should become: ). (POST /api/v2/...)."""

            # Find the first ). (POST
            first_idx = line.find('). (POST')
            if first_idx >= 0:
                # Find the position of the closing )) right before """
                docstring_end = line.rfind(')."""')
                if docstring_end > first_idx:
                    # Extract the part we want to keep
                    # It's from first_idx up to the second )) before """
                    # Count ) characters to find which ) closes the duplicate
                    before_section = line[:first_idx+1]  # Keep up to first )

                    # Find all (POST...) pairs after that
                    after_section = line[first_idx+1:]  # From '. (POST onwards

                    # Look for "). (POST" pattern - that's where the duplicate starts
                    duplicate_start = after_section.find('). (POST')
                    if duplicate_start >= 0:
                        # Keep the first endpoint, remove the duplicate
                        # Find the first closing ) of the first endpoint
                        first_close = after_section.find(')', 1)  # Start from position 1 to skip the first )
                        if first_close > 0:
                            # Keep everything up to that first )
                            kept_section = after_section[:first_close+1]  # Include the )
                            # Append the closing """
                            new_line = before_section + kept_section + '."""'
                            lines[i] = new_line
                            fixes += 1

    new_content = '\n'.join(lines)

    if new_content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
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

