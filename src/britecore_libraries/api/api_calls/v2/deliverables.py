"""BriteCore v2 Deliverables API endpoint wrappers.

Provides:
    list_attachments   -- List file attachments filtered by policy, contact, or revision.
    get_attachment     -- Retrieve a single attachment by file ID.
    get_edeliverables  -- Retrieve e-deliverables within a date range.
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


def list_attachments(
    policy_id: str | None = None,
    revision_id: str | None = None,
    contact_id: str | None = None,
    print_date_from: str | None = None,
    print_date_to: str | None = None,
    print_state_ne: str | None = None,
    print_state: str | None = None,
    order_by: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieve a list of attachments based on specified criteria.

    This function fetches attachments associated with policies, contacts, or revisions,
    using various optional filters. It constructs a request with the provided parameters
    and sends it to the API endpoint for retrieving attachments.

    Parameters:
        policy_id (str, optional): The ID of the policy to filter attachments by.
        revision_id (str, optional): The ID of the revision to filter attachments by.
        contact_id (str, optional): The ID of the contact to filter attachments by.
        print_date_from (str, optional): The start date for filtering attachments by print date. (YYYY-MM-DD)
        print_date_to (str, optional): The end date for filtering attachments by print date. (YYYY-MM-DD)
        print_state_ne (str, optional): Exclude attachments with this print state.
        print_state (str, optional): Filter attachments by this print state.
        order_by (str, optional): Specify the order of results.
        **kwargs (Unpack[RequestParameters]): Additional request parameters to be passed to the API.

    Returns:
        Any: The result of the API request, typically containing the list of attachments.

    Raises:
        BritecoreError.MissingParameter: If none of policy_id, contact_id, or revision_id are provided.
    """
    local_env: dict[str, str | None] = {**locals()}
    if not policy_id and not contact_id and not revision_id:
        BritecoreError.MissingParameter("policy_id, contact_id or revision_id required")

    parameter_list: list[dict[str, str | None]] = [
        {"policy_id": policy_id},
        {"contact_id": contact_id},
        {"revision_id": revision_id},
    ]
    parameter_priority: list[str] = ["revision_id", "contact_id", "policy_id"]

    attachments_search = api_client.multiple_parameter_verification(
        parameter_list, parameter_priority
    )

    for _, (k, v) in enumerate(
        local_env.items()
    ):  # Add any non-default parameters to request
        if v and k not in parameter_priority:
            attachments_search.update({k: v})

    logger.debug("Getting attachments")

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/deliverables/list_attachments",
        json=attachments_search,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def get_attachment(file_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve attachment data by file ID.

    This function fetches attachment information from the API using the provided file ID.
    It constructs a request to the deliverables endpoint and processes the response.

    Parameters:
        file_id (str): The unique identifier of the file to retrieve
        **kwargs (Unpack[RequestParameters]): Additional request parameters

    Returns:
        Any: The processed result from the API response, typically attachment data

    Raises:
        Any exceptions raised by the underlying API client or HTTP request handling

    Note:
        The function logs the attachment retrieval operation at debug level
        The function uses the global API_CLIENT instance for making requests
    """
    LOGGER.debug(f"Getting attachment '{file_id}'")
    file_search: dict[str, str] = {"file_id": file_id}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/deliverables/get_attachment", json=file_search, **kwargs
    )

    return API_CLIENT.process_result(request_result)


def get_edeliverables(
    date_from: str,
    date_to: str,
    unprocessed_only: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieve E-Deliverables data within a specified date range.

    This function fetches E-Deliverables information from the API for a given date
    range. It allows filtering for unprocessed items only and supports additional
    request parameters.

    Parameters:
        date_from: Start date for the query in string format (YYYY-MM-DD)
        date_to: End date for the query in string format (YYYY-MM-DD)
        unprocessed_only: If True, returns only unprocessed deliverables
        **kwargs: Additional request parameters to be passed to the API client

    Returns:
        The processed result from the API request, type depends on the API response

    Raises:
        Any exceptions raised by the underlying API client or HTTP request handling

    Note:
        The function uses a debug logger to trace the request being made
    """
    required_json: dict[str, str] = {
        "date_from": date_from,
        "date_to": date_to,
        "unprocessed_only": unprocessed_only,
    }

    LOGGER.debug(f"Getting E-Deliverables\n{required_json}")

    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v2/deliverables/get_edeliverables",
        json=required_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)
