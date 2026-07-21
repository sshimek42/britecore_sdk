#!/usr/bin/env python3
"""Test the fix directly on authority_limits.py."""

import re
from pathlib import Path

file_path = Path("src/britecore_sdk/api/api_calls/v2/authority_limits.py")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

print(f"File: {file_path.name}")
print(f"Content length: {len(content)} bytes\n")

# Pattern for malformed docstrings
pattern = r'\). \(POST /api/v2/[^)]*\)\)"""'

matches = re.findall(pattern, content)
print(f"Matches found: {len(matches)}")

if matches:
    for i, match in enumerate(matches[:3], 1):
        print(f"\nMatch {i}: {repr(match[:80])}")

# Try the substitution
new_content = re.sub(pattern, ')."""', content)
if new_content != content:
    print(f"\n✓ Substitution would make changes")
    print(f"  Before: {len(content)} bytes")
    print(f"  After:  {len(new_content)} bytes")
    print(f"  Reduced by: {len(content) - len(new_content)} bytes")
else:
    print("\n✗ Substitution would NOT change the content")

