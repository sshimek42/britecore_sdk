"""BriteCore v2 Dashboards API endpoint wrappers.

Provides:
    get_agency_experience_data  -- Retrieve agency experience dashboard data.
    get_csr_data                -- Retrieve CSR dashboard data.
    get_loss_ratio_chart        -- Retrieve loss ratio chart data.
    get_policy_count_data       -- Retrieve policy count dashboard data.
    get_premium_data            -- Retrieve premium dashboard data.
    get_report_url              -- Retrieve a dashboard report URL.
    get_transaction_report      -- Retrieve a paginated transaction report.
    validate_loss_run           -- Validate a loss run for a policy/contact.
"""
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
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: Optional[dict[str, Any]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a dashboards request and normalize the response."""
    LOGGER.debug("Calling dashboards endpoint %s", path)
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def get_agency_experience_data(
    contact_id: Optional[str] = None,
    to_date: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve agency experience data for the dashboard.

    Parameters
    ----------
    contact_id : str, optional
        UUID of the agency contact to filter by.
    to_date : str, optional
        Upper date boundary in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing agency experience metrics.
    """
    return _post(
        "/api/v2/dashboards/get_agency_experience_data",
        _build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_csr_data(
    contact_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve CSR (Customer Service Representative) dashboard data.

    Parameters
    ----------
    contact_id : str, optional
        UUID of the CSR contact to filter by.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing CSR metrics.
    """
    return _post(
        "/api/v2/dashboards/get_csr_data",
        _build_payload(contact_id=contact_id),
        **kwargs,
    )


def get_loss_ratio_chart(
    contact_id: Optional[str] = None,
    to_date: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve loss ratio chart data for the dashboard.

    Parameters
    ----------
    contact_id : str, optional
        UUID of the contact to filter by.
    to_date : str, optional
        Upper date boundary in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing loss ratio chart data.
    """
    return _post(
        "/api/v2/dashboards/get_loss_ratio_chart",
        _build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_policy_count_data(
    contact_id: Optional[str] = None,
    to_date: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy count data for the dashboard.

    Parameters
    ----------
    contact_id : str, optional
        UUID of the contact to filter by.
    to_date : str, optional
        Upper date boundary in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing policy count metrics.
    """
    return _post(
        "/api/v2/dashboards/get_policy_count_data",
        _build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_premium_data(
    contact_id: Optional[str] = None,
    to_date: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve premium data for the dashboard.

    Parameters
    ----------
    contact_id : str, optional
        UUID of the contact to filter by.
    to_date : str, optional
        Upper date boundary in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing premium metrics.
    """
    return _post(
        "/api/v2/dashboards/get_premium_data",
        _build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_report_url(
    contact_id: Optional[str] = None,
    from_date: Optional[str] = None,
    payment_types: Optional[str] = None,
    to_date: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a dashboard report URL.

    Parameters
    ----------
    contact_id : str, optional
        UUID of the contact to filter by.
    from_date : str, optional
        Lower date boundary in ``YYYY-MM-DD`` format.
    payment_types : str, optional
        Comma-separated payment types to include.
    to_date : str, optional
        Upper date boundary in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the report URL.
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
    contact_id: Optional[str] = None,
    from_date: Optional[str] = None,
    page: Optional[int] = None,
    payment_types: Optional[str] = None,
    records_per_page: Optional[str] = None,
    sort_obj: Optional[str] = None,
    to_date: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a paginated transaction report.

    Parameters
    ----------
    contact_id : str, optional
        UUID of the contact to filter by.
    from_date : str, optional
        Lower date boundary in ``YYYY-MM-DD`` format.
    page : int, optional
        Page number (1-based).
    payment_types : str, optional
        Comma-separated payment types to include.
    records_per_page : str, optional
        Number of records per page.
    sort_obj : str, optional
        Sort descriptor string.
    to_date : str, optional
        Upper date boundary in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the transaction report.
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
    contact_id: Optional[str] = None,
    policy_number: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Validate a loss run for a policy or contact.

    Parameters
    ----------
    contact_id : str, optional
        UUID of the contact associated with the loss run.
    policy_number : str, optional
        Policy number to validate.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response indicating validation result.
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
