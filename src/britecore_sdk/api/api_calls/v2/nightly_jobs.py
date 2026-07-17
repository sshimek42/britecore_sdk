"""BriteCore v2 Nightly Jobs API endpoint wrappers.

This module provides wrappers for invoking BriteCore nightly processing jobs
such as autopays, renewals, cancellations, and non-pay workflows.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


def process_auto_pays(
    on_date: str | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Process automatic payments for a date or policy."""
    return post(
        "/api/v2/nightly_jobs/process_auto_pays",
        build_payload(on_date=on_date, policy_number=policy_number),
        **kwargs,
    )


def process_cancellation_pending_or_non_renewals(
    on_date: str | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Process cancellation-pending or non-renewal policies."""
    return post(
        "/api/v2/nightly_jobs/process_cancellation_pending_or_non_renewals",
        build_payload(on_date=on_date, policy_number=policy_number),
        **kwargs,
    )


def process_non_pays_and_cancellations(
    on_date: str | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Process non-pay and cancellation events."""
    return post(
        "/api/v2/nightly_jobs/process_non_pays_and_cancellations",
        build_payload(on_date=on_date, policy_number=policy_number),
        **kwargs,
    )


def process_renewals(
    policy_number: str | None = None,
    renew_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Process policy renewals for a renewal date or policy."""
    return post(
        "/api/v2/nightly_jobs/process_renewals",
        build_payload(policy_number=policy_number, renew_date=renew_date),
        **kwargs,
    )


__all__ = [
    "process_auto_pays",
    "process_cancellation_pending_or_non_renewals",
    "process_non_pays_and_cancellations",
    "process_renewals",
]
