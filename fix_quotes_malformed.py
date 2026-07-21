#!/usr/bin/env python3
"""Fix remaining 22 malformed docstrings in quotes.py."""

from pathlib import Path

file_path = Path("src/britecore_sdk/api/api_calls/v2/quotes.py")

# All 22 remaining malformed docstrings in quotes.py
replacements = [
    ("). (POST /api/v2/quotes/create_and_rate_full_quote)).", ")."),
    ("). (POST /api/v2/quotes/create_endorsement_quote)).", ")."),
    ("). (POST /api/v2/quotes/create_renewal_quote)).", ")."),
    ("). (POST /api/v2/quotes/delete_full_quote)).", ")."),
    ("). (POST /api/v2/quotes/get_estimated_quote)).", ")."),
    ("). (POST /api/v2/quotes/get_quote_properties_summary)).", ")."),
    ("). (POST /api/v2/quotes/get_quote_wizard_plugin)).", ")."),
    ("). (POST /api/v2/quotes/get_risks)).", ")."),
    ("). (POST /api/v2/quotes/issue_full_quote)).", ")."),
    ("). (POST /api/v2/quotes/list_available_offers)).", ")."),
    ("). (POST /api/v2/quotes/modify_full_quote)).", ")."),
    ("). (POST /api/v2/quotes/prefill_loss_history)).", ")."),
    ("). (POST /api/v2/quotes/prefill_quote)).", ")."),
    ("). (POST /api/v2/quotes/prefill_violations)).", ")."),
    ("). (POST /api/v2/quotes/rate_full_quote)).", ")."),
    ("). (POST /api/v2/quotes/rate_quote)).", ")."),
    ("). (POST /api/v2/quotes/retrieve_full_quote)).", ")."),
    ("). (POST /api/v2/quotes/submit_application)).", ")."),
    ("). (POST /api/v2/quotes/submit_change)).", ")."),
    ("). (POST /api/v2/quotes/summary)).", ")."),
    ("). (POST /api/v2/quotes/turn_quote_into_application)).", ")."),
    ("). (POST /api/v2/quotes/update_e_delivery_enabled)).", ")."),
]

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

original_content = content
fixes = 0

for old_text, new_text in replacements:
    if old_text in content:
        content = content.replace(old_text, new_text)
        fixes += 1

if content != original_content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ quotes.py: {fixes} docstring(s) fixed")
else:
    print(f"✗ No changes made to quotes.py")

print(f"\nTotal fixed: {fixes}")

