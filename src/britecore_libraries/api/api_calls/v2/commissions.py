"""BriteCore v2 Commissions API endpoint wrappers."""

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
    """Build a JSON payload while preserving explicit empty collections."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: Optional[dict[str, Any]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a commissions request and normalize the response."""
    LOGGER.debug("Calling commissions endpoint %s", path)
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path=path,
        json=payload or {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def delete_batch_payments(
    payment_ids: Optional[list[str]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a batch of commission payments by ID."""
    return _post(
        "/api/v2/commissions/delete_batch_payments",
        _build_payload(payment_ids=payment_ids),
        **kwargs,
    )


def delete_payment(
    payment_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a single commission payment."""
    return _post(
        "/api/v2/commissions/delete_payment",
        _build_payload(payment_id=payment_id),
        **kwargs,
    )


def get_commission_payees(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the available commission payees."""
    return _post("/api/v2/commissions/get_commission_payees", **kwargs)


def get_payment(
    commission_payment_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a commission payment by ID."""
    return _post(
        "/api/v2/commissions/get_payment",
        _build_payload(commission_payment_id=commission_payment_id),
        **kwargs,
    )


def get_unexported_commissions(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve commissions that have not yet been exported."""
    return _post("/api/v2/commissions/get_unexported_commissions", **kwargs)


def save_batch_payments(
    payments: Optional[list[dict[str, Any]]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Save a batch of commission payments."""
    return _post(
        "/api/v2/commissions/save_batch_payments",
        _build_payload(payments=payments),
        **kwargs,
    )


def save_batch_payments_csv(
    data: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Save batch commission payments from CSV data."""
    return _post(
        "/api/v2/commissions/save_batch_payments_csv",
        _build_payload(data=data),
        **kwargs,
    )


def save_payment(
    amount: Optional[float | int] = None,
    agency_number: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Save a single commission payment."""
    return _post(
        "/api/v2/commissions/save_payment",
        _build_payload(amount=amount, agency_number=agency_number),
        **kwargs,
    )


def update_commission_payments_complete(
    commission_payment_ids: Optional[list[str]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Mark commission payments as complete."""
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
