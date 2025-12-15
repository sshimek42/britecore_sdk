from logging import Logger
from typing import Any, Optional, Unpack

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
    policy_number: Optional[str] = None,
    property_id: Optional[str] = None,
    next_inspection_date: Optional[str] = None,
    inspection_date_request: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Update inspection dates
    :param policy_number: Policy Number
    :type policy_number: str
    :param property_id: Property ID
    :type property_id: str
    :param next_inspection_date: Next Inspection Date (yyyy-mm-dd)
    :type next_inspection_date: str
    :param inspection_date_request: Request Inspection Date (yyyy-mm-dd)
    :type inspection_date_request: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Returns result
    :rtype: Any
    """
    local_env: dict[str, Optional[str]] = {**locals}

    if not policy_number and not property_id:
        BritecoreError.MissingParameter(
            "policy_number or property_id is required")

    parameter_list: list[dict[str, str | None]] = [
        {"policy_number": policy_number},
        {"property_id": property_id},
    ]
    parameter_priority: list[str] = ["property_id", "policy_number"]

    inspection_json: dict[str, str] = api_client.multiple_parameter_verification(
        parameter_list, parameter_priority
    )

    LOGGER.debug("Updating inspection dates")

    for _, (k, v) in enumerate(local_env.items()):
        if v and k not in parameter_priority:
            inspection_json.update({k: v})

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/inspections/update_inspection_dates",
        json=inspection_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)
