#!/usr/bin/env python3
"""Test matching on the exact string from the file."""

import re

line56 = '    """Get Authority Limit (POST /api/v2/authority_limits/get_authority_limit). (POST /api/v2/authority_limits/get_authority_limit))."""'

# Original pattern
pattern1 = r'\). \(POST /api/v2/[^)]*\)\)"""'

# Alternative patterns
patterns = [
    (r'\). \(POST /api/v2/[^)]*\)\)"""', 'Original'),
    (r'\)\. \(POST /api/v2/[^)]*?\)\)"""', 'Non-greedy [^)]*?'),
    (r'''\)\. \(POST /api/v2/[a-z_]+\)\)"""''', 'Match a-z_ only'),
    (r'\)\. \(POST /api/v2/.*?\)\)"""', 'Greedy .*?'),
]

print(f"Test line: {repr(line56)}\n")
print(f"Line contains duplicate: {'. (POST' in line56}\n")

for pattern, desc in patterns:
    match = re.search(pattern, line56)
    print(f"{desc}:")
    print(f"  Pattern: {repr(pattern)}")
    if match:
        print(f"  ✓ Match: {repr(match.group())}\n")
    else:
        print(f"  ✗ No match\n")

