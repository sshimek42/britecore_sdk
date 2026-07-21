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
    """Return upcoming installments for the supplied billing schedules..

    POST /api/v2/billing/get_installments_preview
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
    """Return upcoming installments for a mid-term billing change..

    POST /api/v2/billing/get_installments_preview_mid_term
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
    """Return upcoming installments for a renewal billing schedule..

    POST /api/v2/billing/get_renewal_installments_preview
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
    """Return the billing rating factors related to a policy..

    POST /api/v2/billing/rating_factors
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
