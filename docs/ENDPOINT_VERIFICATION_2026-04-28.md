# Endpoint Verification Snapshot (2026-04-28)

*Generated on: April 28, 2026*
*Spec source: `api_specs/current/britecore.json`*

This snapshot records endpoint path verification for existing wrapper modules,
including older wrappers.

---

## Scope

- Wrapper root scanned: `src/britecore_sdk/api/api_calls/`
- Files included: all `*.py` wrapper modules except `__init__.py`
- Comparison target: `api_specs/current/britecore.json`
- Gap baseline source: `tests/unit/test_api_spec_alignment.py` (`KNOWN_SPEC_GAPS`)

---

## Summary

- Wrapper files scanned: **36**
- Unique wrapper endpoint paths discovered: **217**
- Paths found in current spec: **207**
- Paths in tracked known gaps: **10**
- Unknown missing paths: **0**

### Older v1 wrapper status

- V1 wrapper files scanned: **4**
- Unknown missing V1 paths: **0**
- Conclusion: older V1 wrappers currently align to the spec at endpoint-path level.

---

## Verification Commands Used

```powershell
python -m pytest tests/unit/test_api_spec_alignment.py::test_wrapper_paths_exist_in_api_spec -q
python -m pytest tests/unit/test_v1_endpoint_routing.py tests/unit/test_v2_endpoints.py tests/unit/test_v2_new_endpoints.py -q
```

Strict coverage mode was also checked for context:

```powershell
$env:BRITECORE_STRICT_SPEC_COVERAGE='1'
python -m pytest tests/unit/test_api_spec_alignment.py::test_spec_paths_have_wrappers_report_only -q
Remove-Item Env:BRITECORE_STRICT_SPEC_COVERAGE
```

Note: strict mode reports endpoints in the spec without wrapper implementations,
which is a coverage/backlog signal and not evidence that existing wrappers are
incorrect.

---

## Known Gap Paths (Tracked)

The following paths are already tracked in `KNOWN_SPEC_GAPS` and therefore are
excluded from failure in wrapper-to-spec path verification.

```text
/api/v2/lines/list_policy_types
/api/v2/policies/new_mortgagee
/api/v2/policies/new_revision_contact
/api/v2/policies/retrieve_policy_snapshot
/api/v2/policies/store_mortgagee
/api/v2/policies/update_revision_contact
/api/v2/quotes/create_full_quote
/api/v2/quotes/get_quote
/api/v2/reports/retrieve_report
/api/v2/utils/get_available_function_names
```

---

## Caveat

This snapshot verifies endpoint **path alignment** and routing test coverage. It
does not by itself guarantee full request/response schema parity for every
wrapper.
