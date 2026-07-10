"""Fix W0622 builtin redefinitions across API wrapper modules."""

import pathlib


def patch(path: str, old: str, new: str) -> None:
    """Replace one exact snippet in a file and log whether the patch applied."""
    f = pathlib.Path(path)
    text = f.read_text(encoding="utf-8")
    if old not in text:
        print(f"  WARN: pattern not found in {path}")
        print(f"    {old[:80]!r}")
        return
    f.write_text(text.replace(old, new), encoding="utf-8")
    print(f"  ok: {path}")


# --- v1/contacts.py ---
# zip -> zip_code
patch(
    "src/britecore_sdk/api/api_calls/v1/contacts.py",
    "def retrieveaddressinfofromzip(\n    zip: str | None = None,",
    "def retrieveaddressinfofromzip(\n    zip_code: str | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v1/contacts.py",
    '        "zip": zip,\n        "addressLine1"',
    '        "zip": zip_code,\n        "addressLine1"',
)
# id -> id_, all -> all_
patch(
    "src/britecore_sdk/api/api_calls/v1/contacts.py",
    "    id: str | None = None,\n    all: str | None = None,",
    "    id_: str | None = None,\n    all_: str | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v1/contacts.py",
    '        "id": id,\n        "all": all,',
    '        "id": id_,\n        "all": all_,',
)

# --- v2/async_quotes.py ---
# id -> quote_id
patch(
    "src/britecore_sdk/api/api_calls/v2/async_quotes.py",
    "async def aget_quote(id: str,",
    "async def aget_quote(quote_id: str,",
)
# Find the json={"id": id} usage inside aget_quote body
patch(
    "src/britecore_sdk/api/api_calls/v2/async_quotes.py",
    'json={"id": id}',
    'json={"id": quote_id}',
)

# --- v2/claim_exposures.py ---
# type -> exposure_type in get_broken_limits
patch(
    "src/britecore_sdk/api/api_calls/v2/claim_exposures.py",
    "def get_broken_limits(\n    instance: Any | None = None,\n    type: Any | None = None,",
    "def get_broken_limits(\n    instance: Any | None = None,\n    exposure_type: Any | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/claim_exposures.py",
    (
        '        "type": type,\n'
        "    }\n"
        "    filtered_json = {k: v for k, v in request_json.items() if v is not None}\n"
        "    request_result = API_CLIENT.do_request(\n"
        '        path="/api/v2/claim_exposures/get_broken_limits"'
    ),
    (
        '        "type": exposure_type,\n'
        "    }\n"
        "    filtered_json = {k: v for k, v in request_json.items() if v is not None}\n"
        "    request_result = API_CLIENT.do_request(\n"
        '        path="/api/v2/claim_exposures/get_broken_limits"'
    ),
)

# --- v2/contacts.py ---
# get_aspect_data: all -> all_, id -> id_
patch(
    "src/britecore_sdk/api/api_calls/v2/contacts.py",
    "def get_aspect_data(\n    all: str | None = None,\n    id: str | None = None,",
    "def get_aspect_data(\n    all_: str | None = None,\n    id_: str | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/contacts.py",
    '        "all": all,\n        "id": id,\n        "has_permissions"',
    '        "all": all_,\n        "id": id_,\n        "has_permissions"',
)
# retrieveaddressinfo: zip -> zip_code
patch(
    "src/britecore_sdk/api/api_calls/v2/contacts.py",
    "def retrieveaddressinfo(\n    stateAbbr: str | None = None,\n    zip: str | None = None,",
    "def retrieveaddressinfo(\n    stateAbbr: str | None = None,\n    zip_code: str | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/contacts.py",
    '        "zip": zip,',
    '        "zip": zip_code,',
)
# set_aspect_data: id -> id_
patch(
    "src/britecore_sdk/api/api_calls/v2/contacts.py",
    "    login_information: dict[str, Any] | None = None,\n    id: str | None = None,\n    commission_payment",
    "    login_information: dict[str, Any] | None = None,\n    id_: str | None = None,\n    commission_payment",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/contacts.py",
    '        "id": id,\n        "commission_payment"',
    '        "id": id_,\n        "commission_payment"',
)

# --- v2/custom_data.py ---
# get_custom_data: id -> id_
patch(
    "src/britecore_sdk/api/api_calls/v2/custom_data.py",
    "    reference_id: str | None = None,\n    id: str | None = None,",
    "    reference_id: str | None = None,\n    id_: str | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/custom_data.py",
    '        "id": id,',
    '        "id": id_,',
)

# --- v2/notes.py ---
# retrieve_notes: id -> entity_id
patch(
    "src/britecore_sdk/api/api_calls/v2/notes.py",
    "def retrieve_notes(\n    id: str,",
    "def retrieve_notes(\n    entity_id: str,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/notes.py",
    '        "id": id,',
    '        "id": entity_id,',
)

# --- v2/policies.py ---
# store_revision_description: type -> description_type
patch(
    "src/britecore_sdk/api/api_calls/v2/policies.py",
    "def store_revision_description(\n    revision_id: str | None = None,\n    type: str | None = None,",
    "def store_revision_description(\n    revision_id: str | None = None,\n    description_type: str | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/policies.py",
    '        "type": type,\n        "description": description',
    '        "type": description_type,\n        "description": description',
)

# --- v2/quote.py ---
# delete_quote_wizard_flow: id -> id_
patch(
    "src/britecore_sdk/api/api_calls/v2/quote.py",
    "def delete_quote_wizard_flow(\n    id: str | None = None,",
    "def delete_quote_wizard_flow(\n    id_: str | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/quote.py",
    (
        "    request_json: dict[str, Any] = {\n"
        '        "id": id,\n'
        "    }\n"
        "    filtered_json = {k: v for k, v in request_json.items() if v is not None}\n"
        "    request_result = API_CLIENT.do_request(\n"
        '        path="/api/v2/quote/delete_quote_wizard_flow"'
    ),
    (
        "    request_json: dict[str, Any] = {\n"
        '        "id": id_,\n'
        "    }\n"
        "    filtered_json = {k: v for k, v in request_json.items() if v is not None}\n"
        "    request_result = API_CLIENT.do_request(\n"
        '        path="/api/v2/quote/delete_quote_wizard_flow"'
    ),
)
# patch_flow_definition: id -> id_
patch(
    "src/britecore_sdk/api/api_calls/v2/quote.py",
    (
        "def patch_flow_definition(\n"
        "    definition: Any | None = None,\n"
        "    is_endorsement: Any | None = None,\n"
        "    id: Any | None = None,"
    ),
    (
        "def patch_flow_definition(\n"
        "    definition: Any | None = None,\n"
        "    is_endorsement: Any | None = None,\n"
        "    id_: Any | None = None,"
    ),
)
patch(
    "src/britecore_sdk/api/api_calls/v2/quote.py",
    '        "is_endorsement": is_endorsement,\n        "id": id,',
    '        "is_endorsement": is_endorsement,\n        "id": id_,',
)

# --- v2/quotes.py ---
# get_quote: id -> quote_id
patch(
    "src/britecore_sdk/api/api_calls/v2/quotes.py",
    "def get_quote(id: str,",
    "def get_quote(quote_id: str,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/quotes.py",
    'json={"id": id}',
    'json={"id": quote_id}',
)
# Also fix docstring reference if present
patch(
    "src/britecore_sdk/api/api_calls/v2/quotes.py",
    "This wrapper sends ``id`` to ``/api/v2/quotes/get_quote``",
    "This wrapper sends ``quote_id`` to ``/api/v2/quotes/get_quote``",
)

# --- v2/search.py ---
# add_to_index: id -> document_id
patch(
    "src/britecore_sdk/api/api_calls/v2/search.py",
    "    document: dict | None = None,\n    id: str | None = None,",
    "    document: dict | None = None,\n    document_id: str | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/search.py",
    "build_payload(document=document, id=id,",
    "build_payload(document=document, id=document_id,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/search.py",
    "This wrapper sends ``document``, ``id``, and ``index_name``",
    "This wrapper sends ``document``, ``document_id``, and ``index_name``",
)
# remove_from_index: id -> document_id
patch(
    "src/britecore_sdk/api/api_calls/v2/search.py",
    "def remove_from_index(\n    id: str | None = None,",
    "def remove_from_index(\n    document_id: str | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/search.py",
    "build_payload(id=id,",
    "build_payload(id=document_id,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/search.py",
    "This wrapper sends ``id`` and ``index_name``",
    "This wrapper sends ``document_id`` and ``index_name``",
)

# --- v2/settings.py ---
# delete_carbone_custom_deliverable: id -> id_
patch(
    "src/britecore_sdk/api/api_calls/v2/settings.py",
    "def delete_carbone_custom_deliverable(\n    id: Any | None = None,",
    "def delete_carbone_custom_deliverable(\n    id_: Any | None = None,",
)
patch(
    "src/britecore_sdk/api/api_calls/v2/settings.py",
    (
        "    request_json: dict[str, Any] = {\n"
        '        "id": id,\n'
        "    }\n"
        "    filtered_json = {k: v for k, v in request_json.items() if v is not None}\n"
        "    request_result = API_CLIENT.do_request(\n"
        '        path="/api/v2/settings/delete_carbone_custom_deliverable"'
    ),
    (
        "    request_json: dict[str, Any] = {\n"
        '        "id": id_,\n'
        "    }\n"
        "    filtered_json = {k: v for k, v in request_json.items() if v is not None}\n"
        "    request_result = API_CLIENT.do_request(\n"
        '        path="/api/v2/settings/delete_carbone_custom_deliverable"'
    ),
)

print("\nAll W0622 patches applied.")
