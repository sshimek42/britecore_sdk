#!/usr/bin/env python3
"""Fix all 55 malformed docstrings with direct string replacement."""

from pathlib import Path

# All replacements extracted from the earlier grep output
replacements_by_file = {
    "authority_limits.py": [
        ("). (POST /api/v2/authority_limits/get_authority_limit)).", ")."),
        ("). (POST /api/v2/authority_limits/update_all_authority_limits)).", ")."),
    ],
    "lines.py": [
        ("). (POST /api/v2/lines/create_effective_date)).", ")."),
        ("). (POST /api/v2/lines/create_policy_type)).", ")."),
        ("). (POST /api/v2/lines/create_rating_grid_definition)).", ")."),
        ("). (POST /api/v2/lines/delete_effective_date)).", ")."),
        ("). (POST /api/v2/lines/delete_policy_type)).", ")."),
        ("). (POST /api/v2/lines/delete_rating_table)).", ")."),
        ("). (POST /api/v2/lines/delete_rating_table_file)).", ")."),
        ("). (POST /api/v2/lines/get_effective_date)).", ")."),
        ("). (POST /api/v2/lines/get_policy_type)).", ")."),
        ("). (POST /api/v2/lines/get_rating_table_template)).", ")."),
        ("). (POST /api/v2/lines/get_underwriting_question_autofill_answers)).", ")."),
        ("). (POST /api/v2/lines/import_rating_table)).", ")."),
        ("). (POST /api/v2/lines/list_effective_dates)).", ")."),
        ("). (POST /api/v2/lines/list_rating_grid_definitions)).", ")."),
        ("). (POST /api/v2/lines/list_rating_tables)).", ")."),
        ("). (POST /api/v2/lines/modify_effective_date)).", ")."),
        ("). (POST /api/v2/lines/modify_policy_type)).", ")."),
        ("). (POST /api/v2/lines/retrieve_policy_type_claims_tabs_visibility)).", ")."),
        ("). (POST /api/v2/lines/retrieve_rating_table)).", ")."),
        ("). (POST /api/v2/lines/retrieve_underwriting_questions)).", ")."),
        ("). (POST /api/v2/lines/update_policy_type_claims_tab_visibility)).", ")."),
        ("). (POST /api/v2/lines/update_rating_table)).", ")."),
    ],
    "named_insureds.py": [
        ("). (POST /api/v2/named_insureds/get_named_insured)).", ")."),
        ("). (POST /api/v2/named_insureds/get_named_insured_by_id)).", ")."),
        ("). (POST /api/v2/named_insureds/get_named_insureds)).", ")."),
        ("). (POST /api/v2/named_insureds/run_score)).", ")."),
        ("). (POST /api/v2/named_insureds/set_primary_insured)).", ")."),
    ],
    "quotes.py": [
        ("). (POST /api/v2/quotes/associate_agentcy_to_quote)).", ")."),
        ("). (POST /api/v2/quotes/bind_full_quote)).", ")."),
        ("). (POST /api/v2/quotes/calculate_premium)).", ")."),
        ("). (POST /api/v2/quotes/copy_from_existing_policy)).", ")."),
        ("). (POST /api/v2/quotes/copy_quote)).", ")."),
        ("). (POST /api/v2/quotes/decline_quote)).", ")."),
        ("). (POST /api/v2/quotes/delete_quote)).", ")."),
        ("). (POST /api/v2/quotes/expire_quote)).", ")."),
        ("). (POST /api/v2/quotes/list_quote_ids)).", ")."),
        ("). (POST /api/v2/quotes/quote_details)).", ")."),
        ("). (POST /api/v2/quotes/quote_save)).", ")."),
        ("). (POST /api/v2/quotes/remove_quote_hold)).", ")."),
        ("). (POST /api/v2/quotes/retrieve_active_quote_options)).", ")."),
        ("). (POST /api/v2/quotes/retrieve_quote)).", ")."),
        ("). (POST /api/v2/quotes/retrieve_quote_details)).", ")."),
        ("). (POST /api/v2/quotes/submit_bound_quote)).", ")."),
        ("). (POST /api/v2/quotes/submit_quote_for_review)).", ")."),
    ]
}

api_v2_dir = Path("src/britecore_sdk/api/api_calls/v2")
total_fixed = 0

for filename, replacements in replacements_by_file.items():
    file_path = api_v2_dir / filename
    if not file_path.exists():
        print(f"  File not found: {filename}")
        continue

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
        print(f"✓ {filename}: {fixes} docstring(s) fixed")
        total_fixed += fixes
    else:
        if fixes > 0:
            print(f"  {filename}: Found {fixes} but didn't write (content unchanged?)")

print(f"\n{'=' * 60}")
print(f"Total malformed docstrings fixed: {total_fixed}")

