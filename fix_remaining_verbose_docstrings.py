#!/usr/bin/env python3
# Fix remaining verbose docstrings that use "Returns the normalized process_result"

import glob
import os
import re

BASE_DIR = r"C:\PythonProjects\BriteCore\britecore_sdk\src\britecore_sdk\api\api_calls"


def fix_verbose_returns_docstrings(content: str) -> str:
    """Convert verbose 'Returns the normalized process_result' docstrings to concise format."""

    def replace(m: re.Match) -> str:
        full_match = m.group(0)
        indent = m.group(1)
        summary_line = m.group(2).strip()
        docstring_body = m.group(3)  # Everything between summary and closing """

        # Only process if it contains "Returns the normalized"
        if "Returns the normalized" not in docstring_body:
            return full_match

        # Extract path from the post() call that should follow
        # Look ahead in content after this match
        search_start = m.end()
        search_end = min(search_start + 500, len(content))
        remaining = content[search_start:search_end]

        path_match = re.search(r'post\(\s*"(/api/v[12]/[^"]+)"', remaining)
        if not path_match:
            return full_match

        path = path_match.group(1)
        method = "POST"

        return f'{indent}"""{summary_line}.\n\n{indent}{method} {path}\n{indent}"""'

    # Use non-crossing pattern: (?:(?!""")[\s\S]) prevents """ from appearing in body
    _NTQ = r"(?:(?!\"\"\")[\s\S])"
    pattern = rf'([ \t]+)"""([^\n]+)\n({_NTQ}*?)"""'

    return re.sub(pattern, replace, content)


def process_file(filepath: str) -> bool:
    """Process a single file; return True if changed."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content
    content = fix_verbose_returns_docstrings(content)

    if content != original:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    return False


def main() -> None:
    pattern = os.path.join(BASE_DIR, "**", "*.py")
    files = sorted(glob.glob(pattern, recursive=True))

    fixed = 0
    for filepath in files:
        if process_file(filepath):
            rel = os.path.relpath(
                filepath,
                r"C:\PythonProjects\BriteCore\britecore_sdk",
            )
            print(f"  Fixed: {rel}")
            fixed += 1

    print(f"\nTotal files modified: {fixed}")


if __name__ == "__main__":
    main()
