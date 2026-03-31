"""BriteCore settings API stubs (generated from britecore_api.json).
This module intentionally contains placeholders for API calls that are not yet
implemented in the SDK. Use these stubs for discovery and planning; concrete
request wrappers will be added in a future implementation phase.
"""
from typing import Any, Final
# NOTE: Keys are planned wrapper function names; values are API endpoint paths.
UNIMPLEMENTED_CALLS: Final[dict[str, str]] = {
    "add_city_to_zip_override": "/api/v2/settings/add_city_to_zip_override",
    "add_counties_to_state": "/api/v2/settings/add_counties_to_state",
    "add_county_to_zip_override": "/api/v2/settings/add_county_to_zip_override",
    "get_pdf_engine": "/api/v2/settings/get_pdf_engine",
    "get_setting_value": "/api/v2/settings/get_setting_value",
    "get_system_tags_list": "/api/v2/settings/get_system_tags_list",
    "retrieve_credit_permission_prompt": "/api/v2/settings/retrieve_credit_permission_prompt",
    "retrieve_property_valuation_availability": "/api/v2/settings/retrieve_property_valuation_availability",
    "retrieve_system_tags": "/api/v2/settings/retrieve_system_tags",
    "set_pdf_engine": "/api/v2/settings/set_pdf_engine",
    "set_setting_value": "/api/v2/settings/set_setting_value",
}
def list_unimplemented_calls() -> dict[str, str]:
    """Return a copy of the unimplemented call map for this API domain."""
    return dict(UNIMPLEMENTED_CALLS)
def not_implemented_call(
    call_name: str,
    payload: dict[str, Any] | None = None,
) -> Any:
    """Placeholder dispatcher for unimplemented calls in this module.
    Parameters:
        call_name: Planned wrapper function name from ``UNIMPLEMENTED_CALLS``.
        payload: Optional future request body payload.
    Raises:
        ValueError: If ``call_name`` is unknown.
        NotImplementedError: Always, for known stub calls.
    """
    if call_name not in UNIMPLEMENTED_CALLS:
        raise ValueError(
            f"Unknown stub call '{call_name}'. "
            f"Valid values: {', '.join(sorted(UNIMPLEMENTED_CALLS))}"
        )
    _ = payload
    raise NotImplementedError(
        f"Call '{call_name}' ({UNIMPLEMENTED_CALLS[call_name]}) is not yet implemented."
    )
__all__ = [
    "UNIMPLEMENTED_CALLS",
    "list_unimplemented_calls",
    "not_implemented_call",
]
