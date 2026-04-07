"""BriteCore v2 Dashboards API endpoint wrappers.

This module provides wrappers for dashboard metrics, report URLs, transaction
reports, and loss-run validation in the BriteCore v2 dashboards API.
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
    """Send a dashboards request and normalize the response."""
    LOGGER.debug("Calling dashboards endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def get_agency_experience_data(
    contact_id: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve agency experience dashboard data.

    This wrapper sends ``contact_id`` and ``to_date`` to
    ``/api/v2/dashboards/get_agency_experience_data`` and returns the
    normalized ``process_result(...)`` payload for the requested dashboard
    metrics. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/dashboards/get_agency_experience_data",
        _build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_csr_data(
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve CSR dashboard data.

    This wrapper sends the optional ``contact_id`` filter to
    ``/api/v2/dashboards/get_csr_data`` and returns the normalized
    ``process_result(...)`` payload for the CSR dashboard metrics.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/dashboards/get_csr_data",
        _build_payload(contact_id=contact_id),
        **kwargs,
    )


def get_loss_ratio_chart(
    contact_id: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve loss ratio chart data.

    This wrapper sends ``contact_id`` and ``to_date`` to
    ``/api/v2/dashboards/get_loss_ratio_chart`` and returns the normalized
    ``process_result(...)`` payload for the loss ratio visualization.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/dashboards/get_loss_ratio_chart",
        _build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_policy_count_data(
    contact_id: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy count dashboard data.

    This wrapper sends ``contact_id`` and ``to_date`` to
    ``/api/v2/dashboards/get_policy_count_data`` and returns the normalized
    ``process_result(...)`` payload for the requested policy-count metrics.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/dashboards/get_policy_count_data",
        _build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_premium_data(
    contact_id: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve premium dashboard data.

    This wrapper sends ``contact_id`` and ``to_date`` to
    ``/api/v2/dashboards/get_premium_data`` and returns the normalized
    ``process_result(...)`` payload for the requested premium metrics.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/dashboards/get_premium_data",
        _build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_report_url(
    contact_id: str | None = None,
    from_date: str | None = None,
    payment_types: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a dashboard report URL.

    This wrapper sends the dashboard report filters to
    ``/api/v2/dashboards/get_report_url`` and returns the normalized
    ``process_result(...)`` payload containing the generated report URL or
    related metadata. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/dashboards/get_report_url",
        _build_payload(
            contact_id=contact_id,
            from_date=from_date,
            payment_types=payment_types,
            to_date=to_date,
        ),
        **kwargs,
    )


def get_transaction_report(
    contact_id: str | None = None,
    from_date: str | None = None,
    page: int | None = None,
    payment_types: str | None = None,
    records_per_page: str | None = None,
    sort_obj: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a paginated dashboard transaction report.

    This wrapper sends the report filters, pagination fields, and sort options
    to ``/api/v2/dashboards/get_transaction_report`` and returns the normalized
    ``process_result(...)`` payload for the transaction report. ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/dashboards/get_transaction_report",
        _build_payload(
            contact_id=contact_id,
            from_date=from_date,
            page=page,
            payment_types=payment_types,
            records_per_page=records_per_page,
            sort_obj=sort_obj,
            to_date=to_date,
        ),
        **kwargs,
    )


def validate_loss_run(
    contact_id: str | None = None,
    policy_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Validate whether a loss run is available for a policy or contact.

    This wrapper sends ``contact_id`` and ``policy_number`` to
    ``/api/v2/dashboards/validate_loss_run`` and returns the normalized
    ``process_result(...)`` payload for the validation request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/dashboards/validate_loss_run",
        _build_payload(contact_id=contact_id, policy_number=policy_number),
        **kwargs,
    )


__all__ = [
    "get_agency_experience_data",
    "get_csr_data",
    "get_loss_ratio_chart",
    "get_policy_count_data",
    "get_premium_data",
    "get_report_url",
    "get_transaction_report",
    "validate_loss_run",
]
