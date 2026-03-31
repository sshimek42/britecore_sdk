"""BriteCore v2 Payments API endpoint wrappers.

Provides helpers for payment method management, batch entry workflows,
policy and invoice payments, sweep processing, and billing lookups.
"""

from logging import Logger
from typing import Any, Optional, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def _build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload while preserving explicit ``False`` and empty lists."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: Optional[dict[str, Any]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a payment request and normalize the response."""
    LOGGER.debug("Calling payments endpoint %s", path)
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path=path,
        json=payload or {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def makemanualpolicypayment(
    json_dict: dict[str, Any],
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Call the legacy manual policy payment endpoint."""
    return _post(
        "/api/v1/payments/makeManualPolicyPayment",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def make_manual_policy_payment(
    json_dict: dict[str, Any],
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Alias for :func:`makemanualpolicypayment` with snake_case naming."""
    return makemanualpolicypayment(json_dict=json_dict, **kwargs)


def add_payment_method(
    card_expires_mm: Optional[str] = None,
    ach_bank: Optional[str] = None,
    customer_profile_id: Optional[str] = None,
    card_cvv2: Optional[str] = None,
    card_name_on: Optional[str] = None,
    account_description: Optional[str] = None,
    contact_id: Optional[str] = None,
    ach_account: Optional[str] = None,
    card_type: Optional[str] = None,
    card_expires_yy: Optional[str] = None,
    ach_type: Optional[str] = None,
    ach_routing: Optional[str] = None,
    ach_name_on: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
    type: Optional[str] = None,
    card_number: Optional[str] = None,
    address: Optional[dict[str, Any]] = None,
    vendor_payment_method_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add a stored payment method for a contact."""
    return _post(
        "/api/v2/payments/add_payment_method",
        _build_payload(
            card_expires_mm=card_expires_mm,
            ach_bank=ach_bank,
            customer_profile_id=customer_profile_id,
            card_cvv2=card_cvv2,
            card_name_on=card_name_on,
            account_description=account_description,
            contact_id=contact_id,
            ach_account=ach_account,
            card_type=card_type,
            card_expires_yy=card_expires_yy,
            ach_type=ach_type,
            ach_routing=ach_routing,
            ach_name_on=ach_name_on,
            metadata=metadata,
            type=type,
            card_number=card_number,
            address=address,
            vendor_payment_method_id=vendor_payment_method_id,
        ),
        **kwargs,
    )


def apply_selected_payments(
    payment_ids: Optional[list[str]] = None,
    print_deposit_receipt: Optional[bool] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Apply one or more queued payment records."""
    return _post(
        "/api/v2/payments/apply_selected_payments",
        _build_payload(
            print_deposit_receipt=print_deposit_receipt,
            payment_ids=payment_ids,
        ),
        **kwargs,
    )


def change_payment_method(
    auto_payment_method_id: Optional[str] = None,
    auto_pay_days_before: Optional[int] = None,
    contact_id: Optional[str] = None,
    policy_list: Optional[list[str]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Change the autopay method across multiple policies."""
    return _post(
        "/api/v2/payments/change_payment_method",
        _build_payload(
            auto_payment_method_id=auto_payment_method_id,
            auto_pay_days_before=auto_pay_days_before,
            contact_id=contact_id,
            policy_list=policy_list,
        ),
        **kwargs,
    )


def change_payment_method_single(
    auto_pay_days_before: Optional[int] = None,
    contact_id: Optional[str] = None,
    policy_term_id: Optional[str] = None,
    auto_payment_method_id: Optional[str] = None,
    override_propagation: Optional[bool] = None,
    policy_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Change the autopay method for a single policy or policy term."""
    return _post(
        "/api/v2/payments/change_payment_method_single",
        _build_payload(
            auto_pay_days_before=auto_pay_days_before,
            contact_id=contact_id,
            policy_term_id=policy_term_id,
            auto_payment_method_id=auto_payment_method_id,
            override_propagation=override_propagation,
            policy_id=policy_id,
        ),
        **kwargs,
    )


def create_payment_batch(
    data: Optional[dict[str, Any] | list[dict[str, Any]]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a payment batch container."""
    return _post(
        "/api/v2/payments/create_payment_batch",
        _build_payload(data=data),
        **kwargs,
    )


def create_payment_entries(
    entries: Optional[list[dict[str, Any]]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create payment entries for later import or application."""
    return _post(
        "/api/v2/payments/create_payment_entries",
        _build_payload(entries=entries),
        **kwargs,
    )


def delete_payment_batch(
    batch_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a payment batch by ID."""
    return _post(
        "/api/v2/payments/delete_payment_batch",
        _build_payload(batch_id=batch_id),
        **kwargs,
    )


def delete_payment_entries(
    entry_ids: Optional[list[str]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete one or more payment entries."""
    return _post(
        "/api/v2/payments/delete_payment_entries",
        _build_payload(entry_ids=entry_ids),
        **kwargs,
    )


def get_payment_method_info(
    payment_method_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a stored payment method record."""
    return _post(
        "/api/v2/payments/get_payment_method_info",
        _build_payload(payment_method_id=payment_method_id),
        **kwargs,
    )


def get_unpaid_invoices_by_date(
    due_date: Optional[str] = None,
    bill_date: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve unpaid invoices filtered by due and bill date."""
    return _post(
        "/api/v2/payments/get_unpaid_invoices_by_date",
        _build_payload(due_date=due_date, bill_date=bill_date),
        **kwargs,
    )


def import_payment_entries(
    entry_ids: Optional[list[str]] = None,
    bypass_duplicates_check: Optional[bool] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Import staged payment entries into payment processing."""
    return _post(
        "/api/v2/payments/import_payment_entries",
        _build_payload(
            entry_ids=entry_ids,
            bypass_duplicates_check=bypass_duplicates_check,
        ),
        **kwargs,
    )


def make_payment_by_contact_and_payment_method(
    policy_id: Optional[str] = None,
    payment_amount: Optional[float | int] = None,
    contact_id: Optional[str] = None,
    payment_method_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Submit a payment using a stored contact payment method."""
    return _post(
        "/api/v2/payments/make_payment_by_contact_and_payment_method",
        _build_payload(
            policy_id=policy_id,
            payment_amount=payment_amount,
            contact_id=contact_id,
            payment_method_id=payment_method_id,
        ),
        **kwargs,
    )


def make_payment_by_invoice_or_policy(
    payment_date: Optional[str] = None,
    policy_number: Optional[str] = None,
    amount: Optional[float | int] = None,
    meta: Optional[dict[str, Any]] = None,
    payment_transaction_id: Optional[str] = None,
    source_id: Optional[str] = None,
    invoice_number: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Submit a payment by invoice number or policy number."""
    return _post(
        "/api/v2/payments/make_payment_by_invoice_or_policy",
        _build_payload(
            payment_date=payment_date,
            policy_number=policy_number,
            amount=amount,
            meta=meta,
            payment_transaction_id=payment_transaction_id,
            source_id=source_id,
            invoice_number=invoice_number,
        ),
        **kwargs,
    )


def mark_payment_nsf(
    payment_date: Optional[str] = None,
    confirmation_number: Optional[str] = None,
    policy_number: Optional[str] = None,
    amount: Optional[float | int] = None,
    disable_auto_pay: Optional[bool] = None,
    invoice_number: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Mark a payment as non-sufficient funds."""
    return _post(
        "/api/v2/payments/mark_payment_nsf",
        _build_payload(
            payment_date=payment_date,
            confirmation_number=confirmation_number,
            policy_number=policy_number,
            amount=amount,
            disable_auto_pay=disable_auto_pay,
            invoice_number=invoice_number,
        ),
        **kwargs,
    )


def remove_payment_method(
    payment_method_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove a stored payment method."""
    return _post(
        "/api/v2/payments/remove_payment_method",
        _build_payload(payment_method_id=payment_method_id),
        **kwargs,
    )


def retrieve_account_payoff_amount(
    policy_number: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the payoff amount for a policy account."""
    return _post(
        "/api/v2/payments/retrieve_account_payoff_amount",
        _build_payload(policy_number=policy_number),
        **kwargs,
    )


def retrieve_convenience_fee(
    payment_amount: Optional[float | int] = None,
    account_type: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the calculated convenience fee for a payment."""
    return _post(
        "/api/v2/payments/retrieve_convenience_fee",
        _build_payload(payment_amount=payment_amount, account_type=account_type),
        **kwargs,
    )


def retrieve_payment(
    payment_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a payment record by ID."""
    return _post(
        "/api/v2/payments/retrieve_payment",
        _build_payload(payment_id=payment_id),
        **kwargs,
    )


def retrieve_payment_batch_entries(
    batch_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve all entries associated with a payment batch."""
    return _post(
        "/api/v2/payments/retrieve_payment_batch_entries",
        _build_payload(batch_id=batch_id),
        **kwargs,
    )


def retrieve_payment_batches(
    load_entries: Optional[bool] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List payment batches, optionally including entry details."""
    return _post(
        "/api/v2/payments/retrieve_payment_batches",
        _build_payload(load_entries=load_entries),
        **kwargs,
    )


def retrieve_payment_entries(
    entry_ids: Optional[list[str]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve one or more payment entries by ID."""
    return _post(
        "/api/v2/payments/retrieve_payment_entries",
        _build_payload(entry_ids=entry_ids),
        **kwargs,
    )


def retrieve_payment_methods(
    contact_ids: Optional[list[str]] = None,
    exp_less_than: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve stored payment methods for one or more contacts."""
    return _post(
        "/api/v2/payments/retrieve_payment_methods",
        _build_payload(contact_ids=contact_ids, exp_less_than=exp_less_than),
        **kwargs,
    )


def retrieve_policy_billing_information(
    policy_term_id: Optional[str] = None,
    billing_only: Optional[bool] = None,
    policy_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve billing information for a policy or policy term."""
    return _post(
        "/api/v2/payments/retrieve_policy_billing_information",
        _build_payload(
            policy_term_id=policy_term_id,
            billing_only=billing_only,
            policy_id=policy_id,
        ),
        **kwargs,
    )


def retrieve_sweep_payment_list(
    procdate: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve sweep payments scheduled for a processing date."""
    return _post(
        "/api/v2/payments/retrieve_sweep_payment_list",
        _build_payload(procdate=procdate),
        **kwargs,
    )


def retrieve_updated_invoice_balance(
    invoice_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the latest invoice balance for an invoice ID."""
    return _post(
        "/api/v2/payments/retrieve_updated_invoice_balance",
        _build_payload(invoice_id=invoice_id),
        **kwargs,
    )


def update_payment_batch(
    batch_id: Optional[str] = None,
    data: Optional[dict[str, Any] | list[dict[str, Any]]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update an existing payment batch."""
    return _post(
        "/api/v2/payments/update_payment_batch",
        _build_payload(batch_id=batch_id, data=data),
        **kwargs,
    )


def update_payment_entries(
    entries: Optional[list[dict[str, Any]]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update one or more payment entries."""
    return _post(
        "/api/v2/payments/update_payment_entries",
        _build_payload(entries=entries),
        **kwargs,
    )


def update_sweep_payments_complete(
    procdate: Optional[str] = None,
    payment_ids: Optional[list[str]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Mark sweep payments as fully processed for a given date."""
    return _post(
        "/api/v2/payments/update_sweep_payments_complete",
        _build_payload(procdate=procdate, payment_ids=payment_ids),
        **kwargs,
    )


__all__ = [
    "add_payment_method",
    "apply_selected_payments",
    "change_payment_method",
    "change_payment_method_single",
    "create_payment_batch",
    "create_payment_entries",
    "delete_payment_batch",
    "delete_payment_entries",
    "get_payment_method_info",
    "get_unpaid_invoices_by_date",
    "import_payment_entries",
    "make_manual_policy_payment",
    "make_payment_by_contact_and_payment_method",
    "make_payment_by_invoice_or_policy",
    "makemanualpolicypayment",
    "mark_payment_nsf",
    "remove_payment_method",
    "retrieve_account_payoff_amount",
    "retrieve_convenience_fee",
    "retrieve_payment",
    "retrieve_payment_batch_entries",
    "retrieve_payment_batches",
    "retrieve_payment_entries",
    "retrieve_payment_methods",
    "retrieve_policy_billing_information",
    "retrieve_sweep_payment_list",
    "retrieve_updated_invoice_balance",
    "update_payment_batch",
    "update_payment_entries",
    "update_sweep_payments_complete",
]
