#!/usr/bin/env python3
"""Check character by character."""

import re

line56 = '    """Get Authority Limit (POST /api/v2/authority_limits/get_authority_limit). (POST /api/v2/authority_limits/get_authority_limit))."""'

# Find the position of ). (POST
idx = line56.find("). (POST")
if idx >= 0:
    print(f"Found ). (POST at position {idx}")
    print(f"Characters around that position:")
    for i in range(idx-5, min(idx+20, len(line56))):
        char = line56[i]
        print(f"  Position {i}: {repr(char)} (ASCII {ord(char)})")

    # Extract and analyze
    snippet = line56[idx:idx+50]
    print(f"\nSnippet: {repr(snippet)}")

    # Try various patterns
    test_patterns = [
        r'\)\. \(',
        r')\. (',
        '). (POST',
    ]

    print(f"\nPattern matching:")
    for pattern in test_patterns:
        if re.search(pattern, snippet):
            print(f"  ✓ Pattern matches: {repr(pattern)}")
        else:
            print(f"  ✗ Pattern fails: {repr(pattern)}")

