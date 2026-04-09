"""BriteCore v2 Inspections API endpoint wrappers.

This module provides the SDK wrapper for updating inspection dates for a
policy or property.
"""

from logging import Logger
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_libraries.exceptions import BritecoreError

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def update_inspection_dates(
    policy_number: str | None = None,
    property_id: str | None = None,
    next_inspection_date: str | None = None,
    inspection_date_request: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update inspection dates for a policy or property.

    This wrapper uses either ``property_id`` or ``policy_number`` together with
    the requested inspection dates to call
    ``/api/v2/inspections/update_inspection_dates``. It returns the normalized
    ``process_result(...)`` payload for the update request and accepts
    ``RequestParameters`` overrides via ``**kwargs``.
    """
    local_env: dict[str, str | None] = {**locals()}

    if not policy_number and not property_id:
        BritecoreError.MissingParameter("policy_number or property_id is required")

    parameter_list: list[dict[str, str | None]] = [
        {"policy_number": policy_number},
        {"property_id": property_id},
    ]
    parameter_priority: list[str] = ["property_id", "policy_number"]

    inspection_json: dict[str, str | None] = api_client.multiple_parameter_verification(
        parameter_list, parameter_priority
    )

    LOGGER.debug("Updating inspection dates")

    for _, (k, v) in enumerate(local_env.items()):
        if v and k not in parameter_priority:
            inspection_json.update({k: v})

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/inspections/update_inspection_dates",
        json=inspection_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/inspections/update_inspection_dates"
    )
