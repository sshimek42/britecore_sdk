#!/usr/bin/env python3
"""Debug script to find the exact pattern."""

import re
from pathlib import Path

file_path = Path("src/britecore_sdk/api/api_calls/v2/authority_limits.py")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find lines with the malformed pattern
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if "Get Authority Limit" in line and ")." in line and "POST" in line:
        print(f"Line {i}: {repr(line)}")

        # Simpler pattern: match ). (POST followed by anything, then ))."""
        # The key is that we want to remove the ". (POST ... )" part
        patterns = [
            r'''\)\. \(POST [^)]*\)\)"""''',  # Post path can't have ), but might have /
            r'''\)\. \(POST /api/v2/[^)]*\)\)"""''',  # Better: match the api path
            r'''\)\. \(POST /api/v2/.+?\)\)"""''',  # Non-greedy match to first )
            r'''\)\. \((POST|GET|PUT|DELETE|PATCH) /api/v2/[^)]*\)\)"""''',  # Explicit method + api path
        ]
        for pattern in patterns:
            if re.search(pattern, line):
                print(f"  ✓ Pattern matches: {pattern}")
                match = re.search(pattern, line)
                if match:
                    print(f"    Found: {repr(match.group())}")
            else:
                print(f"  ✗ Pattern doesn't match: {pattern}")

