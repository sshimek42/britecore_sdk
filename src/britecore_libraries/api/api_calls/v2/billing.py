"""BriteCore v2 Billing API endpoint wrappers."""

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
    """Build a JSON payload while preserving explicit ``False`` values."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a billing request and normalize the response."""
    LOGGER.debug("Calling billing endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload or {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def get_installments_preview(
    billing_schedule_ids: list[str] | None = None,
    effective_date: str | None = None,
    premium: float | int | None = None,
    payment_method: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Return upcoming installments for the supplied billing schedules.

    Use ``billing_schedule_ids`` together with the effective date, premium, and
    payment method to preview the installments a billing schedule would generate.
    Returns the normalized ``process_result(...)`` payload, and ``**kwargs`` may
    include ``RequestParameters`` overrides such as timeout, retry, or headers.
    """
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
    billing_schedule_ids: list[str] | None = None,
    payment_method: str | None = None,
    revision_effective_date: str | None = None,
    prorated_premium: float | int | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Return upcoming installments for a mid-term billing change.

    The request uses ``billing_schedule_ids``, ``revision_effective_date``,
    ``prorated_premium``, ``payment_method``, and optionally ``policy_id`` to
    preview how a mid-term revision affects installments. Returns the normalized
    ``process_result(...)`` payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
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
    billing_schedule_ids: list[str] | None = None,
    effective_date: str | None = None,
    premium: float | int | None = None,
    payment_method: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Return upcoming installments for a renewal billing schedule.

    Use ``billing_schedule_ids`` with the renewal effective date, premium, and
    payment method to preview installments for the renewal scenario documented by
    the API. Returns the normalized ``process_result(...)`` payload, and
    ``**kwargs`` may supply ``RequestParameters`` overrides.
    """
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
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Return the billing rating factors related to a policy.

    The API uses ``policy_id`` to identify which policy's billing factors should
    be calculated or retrieved. Returns the normalized ``process_result(...)``
    payload, and ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
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
