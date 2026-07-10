"""BriteCore v2 Commissions API endpoint wrappers."""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.api.api_calls.v2._common import build_payload, post

API_CLIENT: BritecoreAPIClient = api_client


def delete_batch_payments(
    payment_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete commission payments in batch.

    Supply ``payment_ids`` for the commission payment records that should be
    removed from the queue. Returns the normalized ``process_result(...)``
    payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post(
        "/api/v2/commissions/delete_batch_payments",
        build_payload(payment_ids=payment_ids),
        **kwargs,
    )


def delete_payment(
    payment_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a single commission payment.

    Use ``payment_id`` to identify the commission payment record to remove.
    Returns the normalized ``process_result(...)`` payload, and ``**kwargs`` may
    include ``RequestParameters`` overrides for timeout, retry, or headers.
    """
    return post(
        "/api/v2/commissions/delete_payment",
        build_payload(payment_id=payment_id),
        **kwargs,
    )


def get_commission_payees(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the list of commission payee agency numbers.

    This endpoint returns the payees that can be referenced in commission payment
    workflows. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post("/api/v2/commissions/get_commission_payees", **kwargs)


def get_payment(
    commission_payment_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a commission payment record.

    Use ``commission_payment_id`` to fetch the specific payment record documented
    by the commissions API. Returns the normalized ``process_result(...)``
    payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post(
        "/api/v2/commissions/get_payment",
        build_payload(commission_payment_id=commission_payment_id),
        **kwargs,
    )


def get_unexported_commissions(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve commission records that have not yet been exported.

    This endpoint is intended for export workflows that only process outstanding
    commission data. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` may include ``RequestParameters`` overrides.
    """
    return post("/api/v2/commissions/get_unexported_commissions", **kwargs)


def save_batch_payments(
    payments: list[dict[str, Any]] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Save commission payments in batch.

    Pass serialized commission payment objects in ``payments`` to create or store
    them in one request. Returns the normalized ``process_result(...)`` payload,
    and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post(
        "/api/v2/commissions/save_batch_payments",
        build_payload(payments=payments),
        **kwargs,
    )


def save_batch_payments_csv(
    data: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Save commission payments in batch from CSV data.

    Use ``data`` for the CSV content expected by the commissions import workflow.
    Returns the normalized ``process_result(...)`` payload, and ``**kwargs`` may
    include ``RequestParameters`` overrides.
    """
    return post(
        "/api/v2/commissions/save_batch_payments_csv",
        build_payload(data=data),
        **kwargs,
    )


def save_payment(
    amount: float | int | None = None,
    agency_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Save a single commission payment.

    The request uses ``amount`` and ``agency_number`` for the payment record being
    stored. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post(
        "/api/v2/commissions/save_payment",
        build_payload(amount=amount, agency_number=agency_number),
        **kwargs,
    )


def update_commission_payments_complete(
    commission_payment_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Clear selected payments from the commission queue.

    Provide ``commission_payment_ids`` for the commission payments that should be
    marked complete. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` may supply ``RequestParameters`` overrides.
    """
    return post(
        "/api/v2/commissions/update_commission_payments_complete",
        build_payload(commission_payment_ids=commission_payment_ids),
        **kwargs,
    )


__all__ = [
    "delete_batch_payments",
    "delete_payment",
    "get_commission_payees",
    "get_payment",
    "get_unexported_commissions",
    "save_batch_payments",
    "save_batch_payments_csv",
    "save_payment",
    "update_commission_payments_complete",
]

# --- Autogenerated spec wrappers ---


def batch_export_payments(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/batch_export_payments``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/batch_export_payments",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/commissions/batch_export_payments"
    )


def batch_review_payments(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/batch_review_payments``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/batch_review_payments",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/commissions/batch_review_payments"
    )


def batch_update_payment_methods(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/batch_update_payment_methods``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/batch_update_payment_methods",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/commissions/batch_update_payment_methods"
    )


def create_adjustment(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/create_adjustment``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/create_adjustment",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/commissions/create_adjustment"
    )


def download_commission_report(
    report: str | None = None,
    year: str | None = None,
    month: str | None = None,
    contacts: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/download_commission_report``."""
    request_json: dict[str, Any] = {
        "report": report,
        "year": year,
        "month": month,
        "contacts": contacts,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/download_commission_report",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/commissions/download_commission_report"
    )


def email_commission_report(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/email_commission_report``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/email_commission_report",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/commissions/email_commission_report"
    )


def get_commission_accounting_entries(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/get_commission_accounting_entries``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/get_commission_accounting_entries",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/commissions/get_commission_accounting_entries"
    )


def get_commission_payment_composition(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/get_commission_payment_composition``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/get_commission_payment_composition",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/commissions/get_commission_payment_composition",
    )


def get_commission_payments(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/get_commission_payments``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/get_commission_payments",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/commissions/get_commission_payments"
    )


def get_delayed_commission_accounting_entries(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/get_delayed_commission_accounting_entries``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/get_delayed_commission_accounting_entries",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/commissions/get_delayed_commission_accounting_entries",
    )


def get_delayed_commission_entries_summary(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/get_delayed_commission_entries_summary``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/get_delayed_commission_entries_summary",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/commissions/get_delayed_commission_entries_summary",
    )


def write_off_negative_amount(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/commissions/write_off_negative_amount``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/commissions/write_off_negative_amount",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/commissions/write_off_negative_amount"
    )


__all__.extend(
    [
        "batch_export_payments",
        "batch_review_payments",
        "batch_update_payment_methods",
        "create_adjustment",
        "download_commission_report",
        "email_commission_report",
        "get_commission_accounting_entries",
        "get_commission_payment_composition",
        "get_commission_payments",
        "get_delayed_commission_accounting_entries",
        "get_delayed_commission_entries_summary",
        "write_off_negative_amount",
    ]
)
