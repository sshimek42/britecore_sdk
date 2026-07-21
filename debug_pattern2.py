#!/usr/bin/env python3
"""Debug script - print exact characters."""

import re
from pathlib import Path

file_path = Path("src/britecore_sdk/api/api_calls/v2/authority_limits.py")

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the problematic line
lines = content.split('\n')
for i, line in enumerate(lines, 1):
    if "Get Authority Limit" in line and ")." in line:
        print(f"Line {i}:")
        print(f"Raw repr: {repr(line)}")
        print(f"Actual text: {line}")

        # Find the location of ).
        idx = line.find("). (POST")
        if idx >= 0:
            print(f"\nFound ). (POST at position {idx}")
            print(f"Substring from that position: {repr(line[idx:idx+60])}")

            # Now try a simpler pattern
            pattern = r'\)\. \(POST'
            if re.search(pattern, line):
                print(f"✓ Simple pattern '\\)\\. \\(POST' matches!")
                # Find the rest
                pattern2 = r'\)\. \(POST[^:]+\)\)"""'
                if re.search(pattern2, line):
                    print(f"✓ Extended pattern matches!")
                    match = re.search(pattern2, line)
                    print(f"Match: {repr(match.group())}")
        break

