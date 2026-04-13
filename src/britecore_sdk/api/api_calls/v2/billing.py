"""BriteCore v2 Billing API endpoint wrappers."""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


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
    return post(
        "/api/v2/billing/get_installments_preview",
        build_payload(
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
    return post(
        "/api/v2/billing/get_installments_preview_mid_term",
        build_payload(
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
    return post(
        "/api/v2/billing/get_renewal_installments_preview",
        build_payload(
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
    return post(
        "/api/v2/billing/rating_factors",
        build_payload(policy_id=policy_id),
        **kwargs,
    )


__all__ = [
    "get_installments_preview",
    "get_installments_preview_mid_term",
    "get_renewal_installments_preview",
    "rating_factors",
]
