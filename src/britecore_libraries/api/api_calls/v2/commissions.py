"""BriteCore v2 Commissions API endpoint wrappers."""

from logging import Logger
from typing import Any, Unpack, cast

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
    """Build a JSON payload while preserving explicit empty collections."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a commissions request and normalize the response."""
    LOGGER.debug("Calling commissions endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload or {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def delete_batch_payments(
    payment_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete commission payments in batch.

    Supply ``payment_ids`` for the commission payment records that should be
    removed from the queue. Returns the normalized ``process_result(...)``
    payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/commissions/delete_batch_payments",
        _build_payload(payment_ids=payment_ids),
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
    return _post(
        "/api/v2/commissions/delete_payment",
        _build_payload(payment_id=payment_id),
        **kwargs,
    )


def get_commission_payees(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the list of commission payee agency numbers.

    This endpoint returns the payees that can be referenced in commission payment
    workflows. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post("/api/v2/commissions/get_commission_payees", **kwargs)


def get_payment(
    commission_payment_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a commission payment record.

    Use ``commission_payment_id`` to fetch the specific payment record documented
    by the commissions API. Returns the normalized ``process_result(...)``
    payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/commissions/get_payment",
        _build_payload(commission_payment_id=commission_payment_id),
        **kwargs,
    )


def get_unexported_commissions(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve commission records that have not yet been exported.

    This endpoint is intended for export workflows that only process outstanding
    commission data. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` may include ``RequestParameters`` overrides.
    """
    return _post("/api/v2/commissions/get_unexported_commissions", **kwargs)


def save_batch_payments(
    payments: list[dict[str, Any]] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Save commission payments in batch.

    Pass serialized commission payment objects in ``payments`` to create or store
    them in one request. Returns the normalized ``process_result(...)`` payload,
    and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/commissions/save_batch_payments",
        _build_payload(payments=payments),
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
    return _post(
        "/api/v2/commissions/save_batch_payments_csv",
        _build_payload(data=data),
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
    return _post(
        "/api/v2/commissions/save_payment",
        _build_payload(amount=amount, agency_number=agency_number),
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
    return _post(
        "/api/v2/commissions/update_commission_payments_complete",
        _build_payload(commission_payment_ids=commission_payment_ids),
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
