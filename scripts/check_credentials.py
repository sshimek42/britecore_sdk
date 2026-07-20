"""Check for hardcoded credentials in source code."""

import re
import sys
from pathlib import Path

# Patterns for common credential types
CREDENTIAL_PATTERNS = [
    (r"api_key\s*=\s*['\"]([a-zA-Z0-9_-]{20,})['\"]", "API Key"),
    (r"password\s*=\s*['\"](.+?)['\"]", "Password"),
    (r"secret\s*=\s*['\"](.+?)['\"]", "Secret"),
    (r"token\s*=\s*['\"]([a-zA-Z0-9_-]{20,})['\"]", "Token"),
    (r"private_key\s*=\s*['\"](.+?)['\"]", "Private Key"),
]


def check_file(filepath: str) -> list[str]:
    """Check for hardcoded credentials.

    Args:
        filepath: Path to file.

    Returns:
        List of issues found.
    """
    issues = []
    path = Path(filepath)

    if not path.exists():
        return issues

    # Skip non-Python files
    if path.suffix not in [".py", ".toml", ".yaml", ".yml"]:
        return issues

    content = path.read_text()

    for pattern, cred_type in CREDENTIAL_PATTERNS:
        for match in re.finditer(pattern, content, re.IGNORECASE):
            line_num = content[: match.start()].count("\n") + 1
            issues.append(
                f"{filepath}:{line_num}: Found potential {cred_type} credential"
            )

    return issues


def main():
    """Main entry point."""
    total_issues = []

    for arg in sys.argv[1:]:
        issues = check_file(arg)
        total_issues.extend(issues)

    if total_issues:
        for issue in total_issues:
            print(issue)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
