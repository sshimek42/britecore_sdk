"""Move API_CLIENT alias after all imports (fix E402)."""

import pathlib
import re

files = [
    "src/britecore_sdk/api/api_calls/v2/attachments.py",
    "src/britecore_sdk/api/api_calls/v2/commissions.py",
    "src/britecore_sdk/api/api_calls/v2/data.py",
    "src/britecore_sdk/api/api_calls/v2/settings.py",
    "src/britecore_sdk/api/api_calls/v2/signatures.py",
    "src/britecore_sdk/api/api_calls/v2/vendors.py",
]

ALIAS_LINE = "API_CLIENT: BritecoreAPIClient = api_client\n"

for path in files:
    f = pathlib.Path(path)
    text = f.read_text(encoding="utf-8")
    if ALIAS_LINE not in text:
        print(f"  SKIP (no alias): {f.name}")
        continue

    # Remove the alias line from wherever it is
    text_no_alias = text.replace(ALIAS_LINE, "")

    # Find the last import line
    lines = text_no_alias.splitlines(keepends=True)
    last_import_idx = -1
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import_idx = i

    if last_import_idx == -1:
        print(f"  SKIP (no imports found): {f.name}")
        continue

    # Insert the alias after the last import line (with a blank line)
    insert_at = last_import_idx + 1
    new_lines = lines[:insert_at] + ["\n", ALIAS_LINE] + lines[insert_at:]

    # Clean up double blank lines around insertion point
    result = "".join(new_lines)
    result = re.sub(r"\n{3,}", "\n\n", result)

    f.write_text(result, encoding="utf-8")
    print(f"  ok: {f.name}")

print("\nDone.")
