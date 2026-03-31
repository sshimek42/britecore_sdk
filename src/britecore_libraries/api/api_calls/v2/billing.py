"""BriteCore v2 Billing API endpoint wrappers."""

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
    """Build a JSON payload while preserving explicit ``False`` values."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: Optional[dict[str, Any]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a billing request and normalize the response."""
    LOGGER.debug("Calling billing endpoint %s", path)
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path=path,
        json=payload or {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def get_installments_preview(
    billing_schedule_ids: Optional[list[str]] = None,
    effective_date: Optional[str] = None,
    premium: Optional[float | int] = None,
    payment_method: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a billing installments preview for a new or updated premium."""
    return _post(
        "/api/v2/billing/get_installments_preview",
        _build_payload(
            billing_schedule_ids=billing_schedule_ids,
            effective_date=effective_date,
            premium=premium,
            payment_method=payment_method,
        ),
        **kwargs,
    )


def get_installments_preview_mid_term(
    billing_schedule_ids: Optional[list[str]] = None,
    payment_method: Optional[str] = None,
    revision_effective_date: Optional[str] = None,
    prorated_premium: Optional[float | int] = None,
    policy_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a mid-term billing installments preview."""
    return _post(
        "/api/v2/billing/get_installments_preview_mid_term",
        _build_payload(
            billing_schedule_ids=billing_schedule_ids,
            payment_method=payment_method,
            revision_effective_date=revision_effective_date,
            prorated_premium=prorated_premium,
            policy_id=policy_id,
        ),
        **kwargs,
    )


def get_renewal_installments_preview(
    billing_schedule_ids: Optional[list[str]] = None,
    effective_date: Optional[str] = None,
    premium: Optional[float | int] = None,
    payment_method: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a renewal billing installments preview."""
    return _post(
        "/api/v2/billing/get_renewal_installments_preview",
        _build_payload(
            billing_schedule_ids=billing_schedule_ids,
            effective_date=effective_date,
            premium=premium,
            payment_method=payment_method,
        ),
        **kwargs,
    )


def rating_factors(
    policy_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve billing-related rating factors for a policy."""
    return _post(
        "/api/v2/billing/rating_factors",
        _build_payload(policy_id=policy_id),
        **kwargs,
    )


__all__ = [
    "get_installments_preview",
    "get_installments_preview_mid_term",
    "get_renewal_installments_preview",
    "rating_factors",
]
