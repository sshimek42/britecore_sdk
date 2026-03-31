"""BriteCore payments API stubs (generated from britecore_api.json).
This module intentionally contains placeholders for API calls that are not yet
implemented in the SDK. Use these stubs for discovery and planning; concrete
request wrappers will be added in a future implementation phase.
"""
from typing import Any, Final
# NOTE: Keys are planned wrapper function names; values are API endpoint paths.
UNIMPLEMENTED_CALLS: Final[dict[str, str]] = {
    "makemanualpolicypayment": "/api/v1/payments/makeManualPolicyPayment",
    "add_payment_method": "/api/v2/payments/add_payment_method",
    "apply_selected_payments": "/api/v2/payments/apply_selected_payments",
    "change_payment_method": "/api/v2/payments/change_payment_method",
    "change_payment_method_single": "/api/v2/payments/change_payment_method_single",
    "create_payment_batch": "/api/v2/payments/create_payment_batch",
    "create_payment_entries": "/api/v2/payments/create_payment_entries",
    "delete_payment_batch": "/api/v2/payments/delete_payment_batch",
    "delete_payment_entries": "/api/v2/payments/delete_payment_entries",
    "get_payment_method_info": "/api/v2/payments/get_payment_method_info",
    "get_unpaid_invoices_by_date": "/api/v2/payments/get_unpaid_invoices_by_date",
    "import_payment_entries": "/api/v2/payments/import_payment_entries",
    "make_payment_by_contact_and_payment_method": "/api/v2/payments/make_payment_by_contact_and_payment_method",
    "make_payment_by_invoice_or_policy": "/api/v2/payments/make_payment_by_invoice_or_policy",
    "mark_payment_nsf": "/api/v2/payments/mark_payment_nsf",
    "remove_payment_method": "/api/v2/payments/remove_payment_method",
    "retrieve_account_payoff_amount": "/api/v2/payments/retrieve_account_payoff_amount",
    "retrieve_convenience_fee": "/api/v2/payments/retrieve_convenience_fee",
    "retrieve_payment": "/api/v2/payments/retrieve_payment",
    "retrieve_payment_batch_entries": "/api/v2/payments/retrieve_payment_batch_entries",
    "retrieve_payment_batches": "/api/v2/payments/retrieve_payment_batches",
    "retrieve_payment_entries": "/api/v2/payments/retrieve_payment_entries",
    "retrieve_payment_methods": "/api/v2/payments/retrieve_payment_methods",
    "retrieve_policy_billing_information": "/api/v2/payments/retrieve_policy_billing_information",
    "retrieve_sweep_payment_list": "/api/v2/payments/retrieve_sweep_payment_list",
    "retrieve_updated_invoice_balance": "/api/v2/payments/retrieve_updated_invoice_balance",
    "update_payment_batch": "/api/v2/payments/update_payment_batch",
    "update_payment_entries": "/api/v2/payments/update_payment_entries",
    "update_sweep_payments_complete": "/api/v2/payments/update_sweep_payments_complete",
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
