# Quality of Life Audit — v2.1 Opportunity Analysis

**Date:** July 23, 2026
**Scope:** `quotes.py`, `policies.py`, `contacts.py`
**Focus:** Parameter validation, docstrings, helper patterns

---

## Summary

The auto-wrapper script completed 792 v2 endpoints across 74 modules. However, **documentation and validation are inconsistent**, creating friction for SDK users.

**3 primary opportunities:**
1. **Enhanced docstrings** — Auto-generated functions lack parameter descriptions
2. **Mutual-exclusivity validation** — Some functions accept `ID | external_ref` but don't validate one is provided
3. **Inconsistent error handling** — Some validation calls don't raise errors

---

## Detailed Findings

### 1. Minimal Auto-Generated Docstrings (High Impact)

**Status:** ❌ Needs improvement

#### Example: `quotes.py:200-224`
```python
def create_endorsement_quote(
    quote_external_system_reference: str | None = None,
    quote_id: str | None = None,
    endorsement_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create Endorsement Quote.

    POST /api/v2/quotes/create_endorsement_quote
    """
```

**Issues:**
- Only endpoint path provided
- No parameter descriptions
- No information about which parameters are required/optional
- No error conditions documented

**Current good example: `policies.py:106-129`**
```python
def retrieve_policy_ids(
    policy_number: str, **kwargs: Unpack[RequestParameters]
) -> tuple[str, str]:
    """Retrieve active revision and primary property identifiers for a policy.

    This helper delegates to ``retrieve_policy``
    (``/api/v2/policies/retrieve_policy``) and extracts
    ``active_revision.id`` and ``active_revision.primary_property_id`` from the
    normalized ``process_result(...)`` payload.

    Raises:
        BritecoreError.MissingParameter: If policy_number is missing.
    """
```

**Improvement Pattern:**
- Add parameter descriptions from `api_specs/current/britecore.json`
- Document required vs. optional parameters
- Document mutually-exclusive parameter patterns
- Add "Raises" section for validation errors

---

### 2. Missing Mutual-Exclusivity Validation (High Impact)

**Status:** ⚠️ Inconsistent

#### Example 1: `quotes.py:254-276` — `delete_full_quote`
```python
def delete_full_quote(
    external_system_reference: str | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete Full Quote.

    POST /api/v2/quotes/delete_full_quote
    """
    request_json: dict[str, Any] = {
        "external_system_reference": external_system_reference,
        "id": id,
    }
```

**Problem:** No validation that at least one of `id` or `external_system_reference` is provided.

#### Example 2: `policies.py:242-272` — `retrieve_policy_terms` ✅
```python
def retrieve_policy_terms(
    policy_id: str | None = "",
    policy_number: str | None = "",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """..."""
    if not policy_number and not policy_id:
        BritecoreError.MissingParameter("Either policy_id or policy_number is required")
```

**Good:** Validates that at least one parameter is provided.

**Pattern to apply:** Use `API_CLIENT.multiple_parameter_verification(...)` (already exists in `retrieve_policy`).

---

### 3. Inconsistent Error Handling (Medium Impact)

**Status:** ⚠️ Bugs present

#### Example: `policies.py:225-226` — `create_policy`
```python
if term_type == "Custom" and not expiration_date:
    BritecoreError.MissingParameter("expiation_date needed with 'Custom' term_type")
```

**Problem:** Creates the error but **doesn't raise it**. The error object is discarded.

**Fix:**
```python
if term_type == "Custom" and not expiration_date:
    raise BritecoreError.MissingParameter("expiation_date needed with 'Custom' term_type")
```

---

## Good Patterns Worth Extending

### Pattern 1: Parameter Normalization (`contacts.py:56-93`)
**Status:** ✅ Excellent, but isolated

The `new_contact` function normalizes address/phone/email types using `_ADDRESS_TYPE_NORMALIZER`, `_PHONE_TYPE_NORMALIZER`, `_EMAIL_TYPE_NORMALIZER` before sending requests. This reduces errors and improves user experience.

**Opportunity:** Apply similar normalization to other modules (e.g., quote/policy status fields).

### Pattern 2: Convenience Helpers (`policies.py:106-129`, `132-170`)
**Status:** ✅ Good, but sparse

Functions like `retrieve_policy_ids` and `retrieve_policy_list_from_user` wrap lower-level calls and extract common patterns. Only 2-3 such helpers exist across all modules.

**Opportunity:** Add similar helpers to `quotes.py` (e.g., `get_quote_and_rate`, `bind_and_submit_quote`).

### Pattern 3: Mutually-Exclusive Parameter Verification (`policies.py:35-73`)
**Status:** ✅ Good pattern, inconsistently applied

The `multiple_parameter_verification` method exists but is underutilized.

**Current usage:** ~5 functions
**Functions needing it:** ~15-20 auto-generated functions with ID | external_ref patterns

---

## Recommended v2.1 Improvements (In Priority Order)

### Priority 1: Fix Error Handling Bug
- [ ] `policies.py:225-226` — Add missing `raise` statement
- [ ] Audit for similar bugs (other missing raises)
- **Effort:** 15 min
- **Risk:** Very Low
- **Impact:** High (prevents silent failures)

### Priority 2: Enhance Docstrings for Top 10 Functions
- `quotes.py` functions: `create_endorsement_quote`, `create_renewal_quote`, `delete_full_quote`, `bind_full_quote`
- `policies.py` functions: Key auto-generated ones
- Add parameter descriptions, required/optional indicators, error conditions
- **Effort:** 2-3 hours
- **Risk:** Very Low (docs-only)
- **Impact:** High (reduces user confusion)

### Priority 3: Add Mutual-Exclusivity Validation
- Audit auto-generated functions for ID | external_ref patterns
- Apply `multiple_parameter_verification` helper
- **Effort:** 2-3 hours
- **Risk:** Low (existing pattern)
- **Impact:** High (prevents invalid requests)

### Priority 4: Create Convenience Helpers
- `quotes.py`: `bind_and_activate_quote` (chains bind + submit + activate)
- `policies.py`: `create_policy_and_activate` (chains create + activate)
- `contacts.py`: `bulk_create_contacts` (batch with retry)
- **Effort:** 4-5 hours
- **Risk:** Low (new functions, no breaking changes)
- **Impact:** Medium (nice-to-have, workflow simplification)

---

## Sample: Before & After

### Before
```python
def delete_full_quote(
    external_system_reference: str | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete Full Quote.

    POST /api/v2/quotes/delete_full_quote
    """
```

### After
```python
def delete_full_quote(
    external_system_reference: str | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a full quote by ID or external reference.

    Either ``id`` or ``external_system_reference`` must be provided (mutually exclusive).

    Args:
        external_system_reference: The external system reference for the quote.
        id: The internal quote ID. Takes priority if both are provided.
        **kwargs: Additional request parameters (timeout, retry, headers, etc.).

    Returns:
        API response (typically empty on success).

    Raises:
        BritecoreError.MissingParameter: If neither id nor external_system_reference is provided.

    Example:
        >>> delete_full_quote(id="quote-123")
        >>> delete_full_quote(external_system_reference="EXT-456")

    POST /api/v2/quotes/delete_full_quote
    """
    verification_list = [
        {"id": id},
        {"external_system_reference": external_system_reference},
    ]
    priority_list = ["id", "external_system_reference"]
    request_json = API_CLIENT.multiple_parameter_verification(verification_list, priority_list)

    request_result = API_CLIENT.do_request(
        path="/api/v2/quotes/delete_full_quote",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/quotes/delete_full_quote"
    )
```

---

## Recommended Approach

1. **Start with Priority 1** (error handling bug) — 15 min fix, high confidence
2. **Apply to `quotes.py` top 5 functions** — Docstrings + validation
3. **Verify pattern works**, then expand to other modules
4. **Test with real API calls** to confirm validation doesn't break anything

---

## Files to Modify

- `src/britecore_sdk/api/api_calls/v2/quotes.py` — High-value target (30 functions, clear patterns)
- `src/britecore_sdk/api/api_calls/v2/policies.py` — Fix error handling bug
- Consider `src/britecore_sdk/api/api_calls/v2/contacts.py` — Already good, minimal changes needed
