"""BriteCore commissions API stubs (generated from britecore_api.json).
This module intentionally contains placeholders for API calls that are not yet
implemented in the SDK. Use these stubs for discovery and planning; concrete
request wrappers will be added in a future implementation phase.
"""
from typing import Any, Final
# NOTE: Keys are planned wrapper function names; values are API endpoint paths.
UNIMPLEMENTED_CALLS: Final[dict[str, str]] = {
    "delete_batch_payments": "/api/v2/commissions/delete_batch_payments",
    "delete_payment": "/api/v2/commissions/delete_payment",
    "get_commission_payees": "/api/v2/commissions/get_commission_payees",
    "get_payment": "/api/v2/commissions/get_payment",
    "get_unexported_commissions": "/api/v2/commissions/get_unexported_commissions",
    "save_batch_payments": "/api/v2/commissions/save_batch_payments",
    "save_batch_payments_csv": "/api/v2/commissions/save_batch_payments_csv",
    "save_payment": "/api/v2/commissions/save_payment",
    "update_commission_payments_complete": "/api/v2/commissions/update_commission_payments_complete",
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
