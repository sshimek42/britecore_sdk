"""BriteCore vendors API stubs (generated from britecore_api.json).
This module intentionally contains placeholders for API calls that are not yet
implemented in the SDK. Use these stubs for discovery and planning; concrete
request wrappers will be added in a future implementation phase.
"""
from typing import Any, Final
# NOTE: Keys are planned wrapper function names; values are API endpoint paths.
UNIMPLEMENTED_CALLS: Final[dict[str, str]] = {
    "build_ivans_manual_claim": "/api/v2/vendors/build_ivans_manual_claim",
    "build_nxtech_initial_load": "/api/v2/vendors/build_nxtech_initial_load",
    "build_nxtech_manual_transactions": "/api/v2/vendors/build_nxtech_manual_transactions",
    "commercial_munichre_indepth_eligibility": "/api/v2/vendors/commercial_munichre_indepth_eligibility",
    "fetch_motor_vehicle_report_for_drivers": "/api/v2/vendors/fetch_motor_vehicle_report_for_drivers",
    "get_aon_cat_score": "/api/v2/vendors/get_aon_cat_score",
    "get_prefill_services_data": "/api/v2/vendors/get_prefill_services_data",
    "get_value360_token": "/api/v2/vendors/get_value360_token",
    "get_wtw_score": "/api/v2/vendors/get_wtw_score",
    "invoice_cloud_autopay_enroll": "/api/v2/vendors/invoice_cloud_autopay_enroll",
    "invoice_cloud_autopay_is_enrolled": "/api/v2/vendors/invoice_cloud_autopay_is_enrolled",
    "invoice_cloud_suppress_insured_deliverable_printings": "/api/v2/vendors/invoice_cloud_suppress_insured_deliverable_printings",
    "ivans_edocs_build": "/api/v2/vendors/ivans_edocs_build",
    "ivans_file_upload": "/api/v2/vendors/ivans_file_upload",
    "munichre_indepth_eligibility": "/api/v2/vendors/munichre_indepth_eligibility",
    "update_value360_replacement_cost_value": "/api/v2/vendors/update_value360_replacement_cost_value",
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
