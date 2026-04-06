"""BriteCore v2 Nightly Jobs API endpoint wrappers.

Provides:
    process_auto_pays                               -- Process automatic payments for a date.
    process_cancellation_pending_or_non_renewals    -- Process cancellation-pending or non-renewal policies.
    process_non_pays_and_cancellations              -- Process non-pay and cancellation events.
    process_renewals                                -- Process policy renewals for a date.
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

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def _build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
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
    """Process automatic payments for a given date.

    Parameters
    ----------
    on_date : str, optional
        Date on which to process auto-pays in ``YYYY-MM-DD`` format.
    policy_number : str, optional
        Limit processing to a specific policy number.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response indicating the outcome.
    """
    return _post(
        "/api/v2/nightly_jobs/process_auto_pays",
        _build_payload(on_date=on_date, policy_number=policy_number),
        **kwargs,
    )


def process_cancellation_pending_or_non_renewals(
    on_date: str | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Process cancellation-pending or non-renewal policies for a date.

    Parameters
    ----------
    on_date : str, optional
        Date on which to run the job in ``YYYY-MM-DD`` format.
    policy_number : str, optional
        Limit processing to a specific policy number.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response indicating the outcome.
    """
    return _post(
        "/api/v2/nightly_jobs/process_cancellation_pending_or_non_renewals",
        _build_payload(on_date=on_date, policy_number=policy_number),
        **kwargs,
    )


def process_non_pays_and_cancellations(
    on_date: str | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Process non-pay events and policy cancellations for a date.

    Parameters
    ----------
    on_date : str, optional
        Date on which to run the job in ``YYYY-MM-DD`` format.
    policy_number : str, optional
        Limit processing to a specific policy number.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response indicating the outcome.
    """
    return _post(
        "/api/v2/nightly_jobs/process_non_pays_and_cancellations",
        _build_payload(on_date=on_date, policy_number=policy_number),
        **kwargs,
    )


def process_renewals(
    policy_number: str | None = None,
    renew_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Process policy renewals for a given renewal date.

    Parameters
    ----------
    policy_number : str, optional
        Limit processing to a specific policy number.
    renew_date : str, optional
        Renewal date to process in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response indicating the outcome.
    """
    return _post(
        "/api/v2/nightly_jobs/process_renewals",
        _build_payload(policy_number=policy_number, renew_date=renew_date),
        **kwargs,
    )


__all__ = [
    "process_auto_pays",
    "process_cancellation_pending_or_non_renewals",
    "process_non_pays_and_cancellations",
    "process_renewals",
]
