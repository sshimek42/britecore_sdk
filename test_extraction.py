import os, re

version = "1.1.2"
changelog = open("CHANGELOG.md").read()

# Match the section for this version up to (but not including) the next ## heading
pattern = rf"## \[{re.escape(version)}\][^\n]*\n(.*?)(?=\n## \[|\Z)"
match = re.search(pattern, changelog, re.DOTALL)

notes = match.group(1).strip() if match else f"Release {version}"

print("=== Extracted Notes ===")
print(notes[:500] if len(notes) > 500 else notes)
print(f"\n=== Length: {len(notes)} chars ===")
print(f"\nMatch found: {match is not None}")

