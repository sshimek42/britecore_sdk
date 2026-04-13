"""BriteCore v2 Nightly Jobs API endpoint wrappers.

This module provides wrappers for invoking BriteCore nightly processing jobs
such as autopays, renewals, cancellations, and non-pay workflows.
"""

from logging import Logger
from typing import Any, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk import logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a nightly_jobs request and normalize the response."""
    LOGGER.debug("Calling nightly_jobs endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def process_auto_pays(
    on_date: str | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Process automatic payments for a date or policy.

    This wrapper sends ``on_date`` and the optional ``policy_number`` filter to
    ``/api/v2/nightly_jobs/process_auto_pays`` and returns the normalized
    ``process_result(...)`` payload for the nightly job run. ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
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
    """Process cancellation-pending or non-renewal policies.

    This wrapper sends ``on_date`` and the optional ``policy_number`` filter to
    ``/api/v2/nightly_jobs/process_cancellation_pending_or_non_renewals`` and
    returns the normalized ``process_result(...)`` payload for the nightly job
    run. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
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
    """Process non-pay and cancellation events.

    This wrapper sends ``on_date`` and the optional ``policy_number`` filter to
    ``/api/v2/nightly_jobs/process_non_pays_and_cancellations`` and returns the
    normalized ``process_result(...)`` payload for the nightly job run.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
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
    """Process policy renewals for a renewal date or policy.

    This wrapper sends ``policy_number`` and ``renew_date`` to
    ``/api/v2/nightly_jobs/process_renewals`` and returns the normalized
    ``process_result(...)`` payload for the nightly job run. ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
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
