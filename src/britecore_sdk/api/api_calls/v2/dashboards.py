"""BriteCore v2 Dashboards API endpoint wrappers.

This module provides wrappers for dashboard metrics, report URLs, transaction
reports, and loss-run validation in the BriteCore v2 dashboards API.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


def get_agency_experience_data(
    contact_id: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve agency experience dashboard data.

    POST /api/v2/dashboards/get_agency_experience_data
    """
    return post(
        "/api/v2/dashboards/get_agency_experience_data",
        build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_csr_data(
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve CSR dashboard data.

    POST /api/v2/dashboards/get_csr_data
    """
    return post(
        "/api/v2/dashboards/get_csr_data",
        build_payload(contact_id=contact_id),
        **kwargs,
    )


def get_loss_ratio_chart(
    contact_id: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve loss ratio chart data.

    POST /api/v2/dashboards/get_loss_ratio_chart
    """
    return post(
        "/api/v2/dashboards/get_loss_ratio_chart",
        build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_policy_count_data(
    contact_id: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy count dashboard data.

    POST /api/v2/dashboards/get_policy_count_data
    """
    return post(
        "/api/v2/dashboards/get_policy_count_data",
        build_payload(contact_id=contact_id, to_date=to_date),
        **kwargs,
    )


def get_premium_data(
    contact_id: str | None = None,
    to_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve premium dashboard data.

    POST /api/v2/dashboards/get_premium_data
    """
    return post(
        "/api/v2/dashboards/get_premium_data",
        build_payload(contact_id=contact_id, to_date=to_date),
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

    POST /api/v2/dashboards/get_report_url
    """
    return post(
        "/api/v2/dashboards/get_report_url",
        build_payload(
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

    POST /api/v2/dashboards/get_transaction_report
    """
    return post(
        "/api/v2/dashboards/get_transaction_report",
        build_payload(
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

    POST /api/v2/dashboards/validate_loss_run
    """
    return post(
        "/api/v2/dashboards/validate_loss_run",
        build_payload(contact_id=contact_id, policy_number=policy_number),
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
