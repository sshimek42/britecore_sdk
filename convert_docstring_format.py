#!/usr/bin/env python3
# Convert all API wrapper docstrings to consistent multi-line format.
#
# Pattern 1 (single-line with endpoint in parens):
#   Description (POST /api/v2/endpoint).
# -> Description.
#
#    POST /api/v2/endpoint
#
# Pattern 2 (multi-line "This wrapper" body):
#   Summary line.
#   This wrapper sends ... to /api/v2/endpoint ...
# -> Summary line.
#
#    POST /api/v2/endpoint

import glob
import os
import re

BASE_DIR = r"C:\PythonProjects\BriteCore\britecore_sdk\src\britecore_sdk\api\api_calls"


def fix_single_line_with_endpoint(content: str) -> str:
    """Convert single-line docstrings with endpoint in parens to multi-line."""

    def replace(m: re.Match) -> str:
        indent = m.group(1)
        description = m.group(2).rstrip(".")
        method = m.group(3)
        path = m.group(4)
        return f'{indent}"""{description}.\n\n{indent}{method} {path}\n{indent}"""'

    return re.sub(
        r'([ \t]+)"""([^"\n]+?) \((POST|GET|PUT|DELETE|PATCH) (/api/v[12]/[^\)]+)\)\."""',
        replace,
        content,
    )


def fix_this_wrapper_docstrings(content: str) -> str:
    """Convert multi-line 'This wrapper' docstrings to concise multi-line format."""

    def replace_wrapper(m: re.Match) -> str:
        indent = m.group(1)
        docstring_body = m.group(2)

        # Extract the summary (first line, strip trailing dot)
        summary = docstring_body.split("\n")[0].strip().rstrip(".")

        # Find the API path embedded as ``/api/v.../endpoint`` in the docstring
        path_match = re.search(r"``(/api/v[12]/[^`\s]+)``", docstring_body)
        if not path_match:
            return m.group(0)  # Leave unchanged if no embedded path found

        path = path_match.group(1)
        method = "POST"  # All wrapped endpoints in these files use POST

        return f'{indent}"""{summary}.\n\n{indent}{method} {path}\n{indent}"""'

    # Use (?:(?!""")[\s\S]) so the content cannot contain """ and the match
    # cannot cross triple-quote boundaries into adjacent docstrings.
    _NTQ = r"(?:(?!\"\"\")[\s\S])"  # one character that is not the start of """
    pattern = rf'([ \t]+)"""({_NTQ}*?This wrapper{_NTQ}*?)"""'
    return re.sub(pattern, replace_wrapper, content)


def process_file(filepath: str) -> bool:
    """Process a single file; return True if the file was changed."""
    with open(filepath, encoding="utf-8") as f:
        content = f.read()

    original = content
    content = fix_single_line_with_endpoint(content)
    content = fix_this_wrapper_docstrings(content)

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
