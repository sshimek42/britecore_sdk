"""Fix 8 failing tests after W0622 parameter renames."""

import pathlib

# 1. notes tests: id= -> entity_id=
f = pathlib.Path("tests/unit/test_v2_coverage_gaps.py")
t = f.read_text(encoding="utf-8")
t = t.replace("notes.retrieve_notes(id=", "notes.retrieve_notes(entity_id=")
f.write_text(t, encoding="utf-8")
print("fixed coverage_gaps notes")

# 2. search tests: id= -> document_id= in call_kwargs and expected_json
f = pathlib.Path("tests/unit/test_v2_new_endpoints.py")
t = f.read_text(encoding="utf-8")
# add_to_index call_kwargs and expected_json both have {"document":..., "id": "DOC-1", ...}
t = t.replace(
    '"id": "DOC-1", "index_name": "policies"',
    '"document_id": "DOC-1", "index_name": "policies"',
)
f.write_text(t, encoding="utf-8")
print("fixed search tests")

# 3. smoke tests: patch API_CLIENT at module level instead of api_client proxy
f = pathlib.Path("tests/unit/test_v2_new_domains_smoke.py")
t = f.read_text(encoding="utf-8")
t = t.replace(
    'patch("britecore_sdk.api.api_calls.api_client", mock_client):\n'
    "        result = background_jobs.search()",
    'patch("britecore_sdk.api.api_calls.v2.background_jobs.API_CLIENT", mock_client):\n'
    "        result = background_jobs.search()",
)
t = t.replace(
    'patch("britecore_sdk.api.api_calls.api_client", mock_client):\n'
    "        result = ingestion_job.list_ingestion_jobs()",
    'patch("britecore_sdk.api.api_calls.v2.ingestion_job.API_CLIENT", mock_client):\n'
    "        result = ingestion_job.list_ingestion_jobs()",
)
f.write_text(t, encoding="utf-8")
print("fixed smoke tests")

