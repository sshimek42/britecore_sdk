"""BriteCore v2 Payments API endpoint wrappers.

Provides helpers for payment method management, batch entry workflows,
policy and invoice payments, sweep processing, and billing lookups.
"""

from logging import Logger
from typing import Any, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_libraries.api.api_calls.v1.payments import (
    makemanualpolicypayment as _v1_makemanualpolicypayment,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def _build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload while preserving explicit ``False`` and empty lists."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a payment request and normalize the response."""
    LOGGER.debug("Calling payments endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload or {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def add_payment_method(
    card_expires_mm: str | None = None,
    ach_bank: str | None = None,
    customer_profile_id: str | None = None,
    card_cvv2: str | None = None,
    card_name_on: str | None = None,
    account_description: str | None = None,
    contact_id: str | None = None,
    ach_account: str | None = None,
    card_type: str | None = None,
    card_expires_yy: str | None = None,
    ach_type: str | None = None,
    ach_routing: str | None = None,
    ach_name_on: str | None = None,
    metadata: dict[str, Any] | None = None,
    payment_method_type: str | None = None,
    card_number: str | None = None,
    address: dict[str, Any] | None = None,
    vendor_payment_method_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add a payment method for a contact.

    The payload may include card or ACH details, contact linkage, vendor metadata,
    and billing address fields for the stored method. Returns the normalized
    ``process_result(...)`` payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    # Backward compatibility: allow legacy callers to pass type=... in kwargs.
    if "type" in kwargs and not payment_method_type:
        payment_method_type = kwargs.pop("type")

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
            type=payment_method_type,
            card_number=card_number,
            address=address,
            vendor_payment_method_id=vendor_payment_method_id,
        ),
        **kwargs,
    )


def apply_selected_payments(
    payment_ids: list[str] | None = None,
    print_deposit_receipt: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Apply selected payments and optionally generate a deposit receipt.

    Use ``payment_ids`` to identify queued payments and ``print_deposit_receipt``
    to request receipt generation after successful application. Returns the
    normalized ``process_result(...)`` payload, and ``**kwargs`` accepts
    ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/apply_selected_payments",
        _build_payload(
            print_deposit_receipt=print_deposit_receipt,
            payment_ids=payment_ids,
        ),
        **kwargs,
    )


def change_payment_method(
    auto_payment_method_id: str | None = None,
    auto_pay_days_before: int | None = None,
    contact_id: str | None = None,
    policy_list: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set a payment method across multiple policies.

    The request uses ``auto_payment_method_id``, ``auto_pay_days_before``,
    ``contact_id``, and ``policy_list`` to update recurring payment settings.
    Returns the normalized ``process_result(...)`` payload, and ``**kwargs`` may
    include ``RequestParameters`` overrides.
    """
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
    auto_pay_days_before: int | None = None,
    contact_id: str | None = None,
    policy_term_id: str | None = None,
    auto_payment_method_id: str | None = None,
    override_propagation: bool | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set a payment method for one policy or one policy term.

    Use ``policy_id`` or ``policy_term_id`` with the payment method and timing
    fields to update a single recurring payment setup. Returns the normalized
    ``process_result(...)`` payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
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
    data: dict[str, Any] | list[dict[str, Any]] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a payment batch record in the database.

    Pass the serialized batch payload in ``data`` to create the batch container
    used by later entry workflows. Returns the normalized ``process_result(...)``
    payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/create_payment_batch",
        _build_payload(data=data),
        **kwargs,
    )


def create_payment_entries(
    entries: list[dict[str, Any]] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create payment entries from a serialized dataset.

    Use ``entries`` for the staged payment rows that should be inserted before
    import or application. Returns the normalized ``process_result(...)``
    payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/create_payment_entries",
        _build_payload(entries=entries),
        **kwargs,
    )


def delete_payment_batch(
    batch_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove a payment batch from the database.

    Provide ``batch_id`` for the batch that should be deleted. Returns the
    normalized ``process_result(...)`` payload, and ``**kwargs`` may include
    ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/delete_payment_batch",
        _build_payload(batch_id=batch_id),
        **kwargs,
    )


def delete_payment_entries(
    entry_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete payment entries by entry identifier.

    Use ``entry_ids`` for the entry records that should be removed from the
    database. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/delete_payment_entries",
        _build_payload(entry_ids=entry_ids),
        **kwargs,
    )


def get_payment_method_info(
    payment_method_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve information about a stored payment method.

    The endpoint uses ``payment_method_id`` to return policy and term details
    tied to that method. Returns the normalized ``process_result(...)`` payload,
    and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/get_payment_method_info",
        _build_payload(payment_method_id=payment_method_id),
        **kwargs,
    )


def get_unpaid_invoices_by_date(
    due_date: str | None = None,
    bill_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve unpaid invoices for a bill date and/or due date.

    Use ``bill_date`` and ``due_date`` to filter unpaid invoices and related
    billing information. Returns the normalized ``process_result(...)`` payload,
    and ``**kwargs`` may include ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/get_unpaid_invoices_by_date",
        _build_payload(due_date=due_date, bill_date=bill_date),
        **kwargs,
    )


def import_payment_entries(
    entry_ids: list[str] | None = None,
    bypass_duplicates_check: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Import staged payment entries into the accounting workflow.

    Provide ``entry_ids`` for the rows to import and use
    ``bypass_duplicates_check`` when the API should skip duplicate detection.
    Returns the normalized ``process_result(...)`` payload, and ``**kwargs`` accepts
    ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/import_payment_entries",
        _build_payload(
            entry_ids=entry_ids,
            bypass_duplicates_check=bypass_duplicates_check,
        ),
        **kwargs,
    )


def make_payment_by_contact_and_payment_method(
    policy_id: str | None = None,
    payment_amount: float | int | None = None,
    contact_id: str | None = None,
    payment_method_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Make a payment for a policy using a stored contact payment method.

    The request uses ``policy_id``, ``contact_id``, ``payment_method_id``, and
    ``payment_amount`` to charge the stored method. Returns the normalized
    ``process_result(...)`` payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
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
    payment_date: str | None = None,
    policy_number: str | None = None,
    amount: float | int | None = None,
    meta: dict[str, Any] | None = None,
    payment_transaction_id: str | None = None,
    source_id: str | None = None,
    invoice_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Make a payment identified by invoice number or policy number.

    Use the invoice or policy identifiers together with payment details such as
    ``amount``, ``payment_date``, transaction metadata, and optional source IDs.
    Returns the normalized ``process_result(...)`` payload, and ``**kwargs`` accepts
    ``RequestParameters`` overrides.
    """
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
    payment_date: str | None = None,
    confirmation_number: str | None = None,
    policy_number: str | None = None,
    amount: float | int | None = None,
    disable_auto_pay: bool | None = None,
    invoice_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Mark a payment as NSF.

    The API locates the payment using the supplied date, confirmation number,
    policy or invoice identifiers, and amount, with optional auto-pay disablement.
    Returns the normalized ``process_result(...)`` payload, and ``**kwargs`` accepts
    ``RequestParameters`` overrides.
    """
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
    payment_method_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Soft-delete a stored payment method.

    Use ``payment_method_id`` for the method to remove when it is no longer
    referenced by policy billing. Returns the normalized ``process_result(...)``
    payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/remove_payment_method",
        _build_payload(payment_method_id=payment_method_id),
        **kwargs,
    )


def retrieve_account_payoff_amount(
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the payoff amount for an account or policy.

    The endpoint uses ``policy_number`` to determine the amount needed to pay off
    the account balance. Returns the normalized ``process_result(...)`` payload,
    and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/retrieve_account_payoff_amount",
        _build_payload(policy_number=policy_number),
        **kwargs,
    )


def retrieve_convenience_fee(
    payment_amount: float | int | None = None,
    account_type: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the processor convenience fee for a payment.

    Use ``payment_amount`` and ``account_type`` to calculate the fee that the
    enabled payment processor would charge. Returns the normalized
    ``process_result(...)`` payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/retrieve_convenience_fee",
        _build_payload(payment_amount=payment_amount, account_type=account_type),
        **kwargs,
    )


def retrieve_payment(
    payment_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a specific payment record.

    Provide ``payment_id`` for the payment that should be fetched. Returns the
    normalized ``process_result(...)`` payload, and ``**kwargs`` may include
    ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/retrieve_payment",
        _build_payload(payment_id=payment_id),
        **kwargs,
    )


def retrieve_payment_batch_entries(
    batch_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the entries related to a payment batch.

    Use ``batch_id`` to load the batch entries documented by the payments API.
    Returns the normalized ``process_result(...)`` payload, and ``**kwargs`` accepts
    ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/retrieve_payment_batch_entries",
        _build_payload(batch_id=batch_id),
        **kwargs,
    )


def retrieve_payment_batches(
    load_entries: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve payment batch records.

    Set ``load_entries`` when the response should include the batch's related
    entry data. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/retrieve_payment_batches",
        _build_payload(load_entries=load_entries),
        **kwargs,
    )


def retrieve_payment_entries(
    entry_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve payment entries by entry identifier.

    Provide ``entry_ids`` for the entry records that should be returned. Returns
    the normalized ``process_result(...)`` payload, and ``**kwargs`` accepts
    ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/retrieve_payment_entries",
        _build_payload(entry_ids=entry_ids),
        **kwargs,
    )


def retrieve_payment_methods(
    contact_ids: list[str] | None = None,
    exp_less_than: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve payment methods for one or more contacts.

    Use ``contact_ids`` and optional ``exp_less_than`` filtering to return stored
    payment methods that match the request. Returns the normalized
    ``process_result(...)`` payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/retrieve_payment_methods",
        _build_payload(contact_ids=contact_ids, exp_less_than=exp_less_than),
        **kwargs,
    )


def retrieve_policy_billing_information(
    policy_term_id: str | None = None,
    billing_only: bool | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve billing information for a policy.

    The request accepts ``policy_id`` or ``policy_term_id`` and can restrict the
    response to billing-only fields with ``billing_only``. Returns the normalized
    ``process_result(...)`` payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
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
    procdate: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve pending sweep payments.

    Use ``procdate`` to filter the sweep payments scheduled for a given processing
    date. Returns the normalized ``process_result(...)`` payload, and ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/retrieve_sweep_payment_list",
        _build_payload(procdate=procdate),
        **kwargs,
    )


def retrieve_updated_invoice_balance(
    invoice_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the current balance for an invoice.

    The API uses ``invoice_id`` to look up the latest stored invoice balance.
    Returns the normalized ``process_result(...)`` payload, and ``**kwargs`` may
    include ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/retrieve_updated_invoice_balance",
        _build_payload(invoice_id=invoice_id),
        **kwargs,
    )


def update_payment_batch(
    batch_id: str | None = None,
    data: dict[str, Any] | list[dict[str, Any]] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update a payment batch record.

    Provide ``batch_id`` and the serialized ``data`` changes for the batch that
    should be updated. Returns the normalized ``process_result(...)`` payload,
    and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/update_payment_batch",
        _build_payload(batch_id=batch_id, data=data),
        **kwargs,
    )


def update_payment_entries(
    entries: list[dict[str, Any]] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update payment entries from a serialized dataset.

    Use ``entries`` for the payment entry objects that should be updated in the
    database. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/update_payment_entries",
        _build_payload(entries=entries),
        **kwargs,
    )


def update_sweep_payments_complete(
    procdate: str | None = None,
    payment_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Mark sweep payments as completed.

    Use ``procdate`` and ``payment_ids`` to clear the pending sweep payment set
    for a processing date. Returns the normalized ``process_result(...)``
    payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/payments/update_sweep_payments_complete",
        _build_payload(procdate=procdate, payment_ids=payment_ids),
        **kwargs,
    )


def make_manual_policy_payment(
    json_dict: dict[str, Any],
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Post a payment already collected outside vendor processing.

    This v2 export delegates to ``/api/v1/payments/makeManualPolicyPayment`` and
    uses ``json_dict`` for the collected payment payload tied to a policy.
    Returns the normalized ``process_result(...)`` response from that endpoint,
    and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return makemanualpolicypayment(json_dict=json_dict, **kwargs)


def makemanualpolicypayment(
    json_dict: dict[str, Any],
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delegate to ``/api/v1/payments/makeManualPolicyPayment``.

    This v2 compatibility wrapper delegates to the canonical v1 implementation
    and returns its normalized ``process_result(...)`` payload.
    """
    return _v1_makemanualpolicypayment(json_dict=json_dict, **kwargs)


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
