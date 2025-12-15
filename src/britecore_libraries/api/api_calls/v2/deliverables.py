from logging import Logger
from typing import Any, Optional, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (BritecoreAPIClient,
                                               api_client, RequestParameters)
from britecore_libraries.exceptions import BritecoreError

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def list_attachments(
    policy_id: Optional[str] = None,
    revision_id: Optional[str] = None,
    contact_id: Optional[str] = None,
    print_date_from: Optional[str] = None,
    print_date_to: Optional[str] = None,
    print_state_ne: Optional[str] = None,
    print_state: Optional[str] = None,
    order_by: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieve policy attachments
    :param policy_id: Policy Id
    :type policy_id: str
    :param revision_id: Revision ID
    :type contact_id: str
    :param print_date_from: Start Date (yyyy-mm-dd)
    :type print_date_from: str
    :param print_date_to: End Date (yyyy-mm-dd)
    :type print_date_to: str
    :param print_state_ne: Do not get attachments from this state
    :type print_state_ne: str
    :param print_state: Get attachments from this state only
    :type print_state: str
    :param order_by: Order list by
    :type order_by: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Attachment IDs
    :rtype: Any
    """
    local_env: dict[str, Optional[str]] = {**locals}
    if not policy_id and not contact_id and not revision_id:
        BritecoreError.MissingParameter("policy_id, contact_id or revision_id required")

    parameter_list: list[dict[str, str | None]] = [{"policy_id": policy_id},{"contact_id":contact_id},{"revision_id": revision_id}]
    parameter_priority: list[str] = ["revision_id", "contact_id", "policy_id"]

    attachments_search = api_client.multiple_parameter_verification(parameter_list, parameter_priority)

    for _, (k, v) in enumerate(local_env.items()):  #Add any non-default parameters to request
        if v and k not in parameter_priority:
            attachments_search.update({k: v})

    logger.debug("Getting attachments")

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/deliverables/list_attachments",
        json=attachments_search,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def get_attachment(file_id: str, **kwargs:Unpack[RequestParameters]) -> Any:
    """
    Retrieve policy attachment
    :param file_id: Attachment ID
    :type file_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Requested file
    :rtype: Any
    """
    LOGGER.debug(f"Getting attachment %f.yellow%{file_id}%f%")
    file_search: dict[str, str] = {"file_id": file_id}
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/deliverables/get_attachment", json=file_search, **kwargs
    )

    return API_CLIENT.process_result(request_result)


def get_edeliverables(
    date_from: str, date_to: str, unprocessed_only: Optional[bool] = True,
    **kwargs:Unpack[RequestParameters]
) -> Any:
    """Get E-Deliverables
    :param date_from: Start date (yyyy-mm-dd)
    :type date_from: str
    :param date_to: End date (yyyy-mm-dd)
    :type date_from: str
    :param unprocessed_only: Unprocessed or processed policies (Default: True)
    :type unprocessed_only: Optional[bool]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: E-Deliverables
    :rtype: Any
    """
    required_json: dict[str, str] = {
        "date_from": date_from,
        "date_to": date_to,
        "unprocessed_only": unprocessed_only,
    }

    LOGGER.debug(f"Getting E-Deliverables\n%f.yellow%{required_json}%f%")

    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v2/deliverables/get_edeliverables",
        json=required_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)
