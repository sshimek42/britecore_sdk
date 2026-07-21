#!/usr/bin/env python3
"""Test the pattern directly."""

import re

test_line = '    """Get Authority Limit (POST /api/v2/authority_limits/get_authority_limit). (POST /api/v2/authority_limits/get_authority_limit))."""'

patterns = [
    (r'\)\. \(POST .+?\)\)"""', 'Current (fails)'),
    (r'\)\. \([^)]+\)\)"""', 'Match [^)] (fails because path has /)'),
    (r'\)\. \(POST[^)]*\)\)"""', 'Match path without )'),
    (r'\)\. \(POST /api/v2/[^)]+\)\)"""', 'Match path with /api/v2'),
    (r'\)\. \(.*?\)\)"""', 'Match any method'),
    (r'\)\. \((?!POST)[^)]*\)\)"""', 'Negative lookahead'),
]

print(f"Test line: {test_line}\n")

for pattern, desc in patterns:
    match = re.search(pattern, test_line)
    if match:
        print(f"✓ {desc}")
        print(f"  Pattern: {pattern}")
        print(f"  Matched: {repr(match.group())}\n")
    else:
        print(f"✗ {desc}: {pattern}\n")

