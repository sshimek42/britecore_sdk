#!/usr/bin/env python3
"""Test the v3 pattern."""

import re

line = '    """Get Authority Limit (POST /api/v2/authority_limits/get_authority_limit). (POST /api/v2/authority_limits/get_authority_limit))."""'

pattern = r'\)\. \(POST /api/v2/[a-z_/]*\)\)"""'

match = re.search(pattern, line)
print(f"Line: {line}\n")
print(f"Pattern: {pattern}")
print(f"Match: {match}")

if match:
    print(f"Matched: {repr(match.group())}")
    new_line = re.sub(pattern, ')."""', line)
    print(f"Result: {new_line}")
else:
    print("No match - trying variations...")

    patterns = [
        r'\)\. \(POST /api/v2/[a-z_/-]*\)\)"""',
        r'\)\. \(POST /api/v2/.*?\)\)"""',
        r'\)\. \(POST /api/v2/.+?\)\)"""',
    ]

    for p in patterns:
        if re.search(p, line):
            print(f"  ✓ Pattern works: {p}")
            break
        else:
            print(f"  ✗ Pattern fails: {p}")

