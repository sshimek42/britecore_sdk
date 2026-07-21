#!/usr/bin/env python3
"""Debug pattern pieces."""

import re

test_line = '    """Get Authority Limit (POST /api/v2/authority_limits/get_authority_limit). (POST /api/v2/authority_limits/get_authority_limit))."""'

print(f"Test line: {test_line}\n")

# Test just the path part
path_part = '/api/v2/authority_limits/get_authority_limit'
print(f"Path part: {path_part}")
print(f"Has ): {')' in path_part}")
print(f"Has /: {'/' in path_part}\n")

# Test individual parts
patterns = [
    (r'\.', 'Dot'),
    (r'\. \(', 'Dot space paren'),
    (r'\. \(POST', 'Dot space paren POST'),
    (r'\. \(POST /', 'Dot space paren POST slash'),
    (r'\. \(POST /api/v2/', 'Dot space paren POST /api/v2/'),
    (r'\. \(POST /api/v2/[^)]*\)', 'Full path without extra paren'),
]

for pattern, desc in patterns:
    match = re.search(pattern, test_line)
    if match:
        print(f"✓ {desc}: {repr(match.group())}")
    else:
        print(f"✗ {desc}: No match")

# Now try building up the full pattern
print("\nBuilding full pattern:")
pattern = r'\). \(POST /api/v2/[^)]*\)\)'
match = re.search(pattern, test_line)
if match:
    print(f"✓ Full pattern works: {repr(match.group())}")
else:
    print(f"✗ Full pattern doesn't match")

# Maybe I need to include the trailing triple quotes?
print("\nWith trailing quotes:")
pattern2 = r'\). \(POST /api/v2/[^)]*\)\)"""'
match2 = re.search(pattern2, test_line)
if match2:
    print(f"✓ Pattern with quotes works: {repr(match2.group())}")
else:
    print(f"✗ Pattern with quotes doesn't match")
    # Check if the """ is actually there
    print(f"Line ends with: {repr(test_line[-20:])}")

