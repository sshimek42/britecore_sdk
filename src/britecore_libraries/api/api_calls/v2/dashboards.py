"""BriteCore dashboards API stubs (generated from britecore_api.json).
This module intentionally contains placeholders for API calls that are not yet
implemented in the SDK. Use these stubs for discovery and planning; concrete
request wrappers will be added in a future implementation phase.
"""
from typing import Any, Final
# NOTE: Keys are planned wrapper function names; values are API endpoint paths.
UNIMPLEMENTED_CALLS: Final[dict[str, str]] = {
    "get_agency_experience_data": "/api/v2/dashboards/get_agency_experience_data",
    "get_csr_data": "/api/v2/dashboards/get_csr_data",
    "get_loss_ratio_chart": "/api/v2/dashboards/get_loss_ratio_chart",
    "get_policy_count_data": "/api/v2/dashboards/get_policy_count_data",
    "get_premium_data": "/api/v2/dashboards/get_premium_data",
    "get_report_url": "/api/v2/dashboards/get_report_url",
    "get_transaction_report": "/api/v2/dashboards/get_transaction_report",
    "validate_loss_run": "/api/v2/dashboards/validate_loss_run",
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
