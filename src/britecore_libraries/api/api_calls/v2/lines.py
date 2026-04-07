"""BriteCore v2 Lines API endpoint wrappers.

Provides programmatic helpers for working with BriteCore
line/policy export data.

Key functions:
    get_export_line_file -- Fetch export data for a specific line or policy type.

For interactive menu functionality, see britecore_libraries.utils.interactive_menu.
"""

from json import loads
from logging import Logger
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import BritecoreError, logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def get_export_line_file(
    line: tuple,
    line_type: str,
    line_name: str,
    include_custom_sequences: bool | None = False,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieve export line file data based on line type and parameters.

    This function fetches line or policy data from an API endpoint based on the specified line type.
    It supports both 'Line' and 'Policy' types, with optional inclusion of custom sequences for line data.

    Args:
        line: A tuple containing line information (current effective date ID, current state ID, current line ID).
        line_type: String indicating the type of line data to retrieve ('Line' or 'Policy').
        line_name: String identifier for the line being processed, used in logging.
        include_custom_sequences: Boolean flag to include custom sequences in the request for line data.
        **kwargs: Additional keyword arguments passed to the API client request method.

    Returns:
        The processed API response data, either as parsed JSON or the raw response object.

    Raises:
        Any exceptions raised by the underlying API client or JSON parsing operations.
    """
    request_result: BaseHTTPResponse | HTTPResponse | None = None
    LOGGER.info(f"Retrieving '{line_name}' lines")

    if line_type == "Line":
        web_request_json: dict[str, str | bool] = {
            "curr_eff_date_id": line[0],
            "curr_line_id": line[2],
            "curr_state_id": line[1],
            "include_custom_sequences": include_custom_sequences,
        }

        request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
            path="/api/v2/lines/get_export_line_file",
            json=web_request_json,
            **kwargs,
        )
    elif line_type == "Policy":
        request_result = API_CLIENT.do_request(path="/api/v2/policies/get_policies")

    LOGGER.info(f"Finished retrieving '{line_name}' lines")

    API_CLIENT.process_results = API_CLIENT.process_result(request_result)
    if API_CLIENT.process_results is not None:
        return loads(API_CLIENT.process_results)

    return request_result


# Backward compatibility: re-export from new interactive_menu utility module.
# This import is lazy to avoid requiring pyinputplus for API-only users.
def line_menu(**kwargs: Unpack[RequestParameters]):
    """
    Deprecated: Use britecore_libraries.utils.interactive_menu.line_menu instead.

    This function is retained for backward compatibility.
    """
    from britecore_libraries.utils.interactive_menu import line_menu as _line_menu

    return _line_menu(**kwargs)


def get_all_effective_dates(**kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve all effective dates for lines from the API.

    This function makes a request to the API endpoint to fetch all effective dates
    associated with lines. It uses the API client to perform the HTTP request and
    process the response.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Variable length argument list containing request parameters.
        These parameters are passed directly to the API client's request method.

    Returns
    -------
    Any
        The processed result from the API response. The exact type depends on
        the structure of the API response and how it's processed by the client.

    Raises
    ------
    HTTPException
        If the HTTP request fails or returns an error status code.
        The specific exception type may vary based on the API client implementation.

    Notes
    -----
    The function uses the API client's do_request method to execute the HTTP request
    and process_result method to handle the response. The path parameter is
    hardcoded to "/api/v2/lines/get_all_effective_dates".
    """
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_effective_dates", **kwargs
    )

    return API_CLIENT.process_result(request_result)


def get_all_states(
    effective_date_id: str | None = None, **kwargs: Unpack[RequestParameters]
) -> Any:
    """
    Retrieve all states from the API endpoint.

    This function fetches all states from the API using the specified effective date ID
    and any additional request parameters. It constructs a request to the
    /api/v2/lines/get_all_states endpoint and processes the response.

    Parameters:
        effective_date_id (str, optional): The effective date ID to filter states.
                                           If None, all states are retrieved.
        **kwargs: Additional request parameters to be passed to the API client.

    Returns:
        Any: The processed result from the API request, typically containing
             the states data.

    Raises:
        Any exceptions raised by the underlying API client or request processing
        mechanisms are propagated as-is.
    """

    effective_date_json: dict[str, str] | None = {}

    if effective_date_id:
        effective_date_json = {"effective_date_id": effective_date_id}

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_states", json=effective_date_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)


def get_all_lines(
    effective_date_id: str,
    location_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieve all lines based on effective date ID with optional location filter.

    This function fetches line information from the API using the provided effective date ID.
    An optional location ID can be specified to filter results by a specific location.

    Parameters:
        effective_date_id (str): The ID of the effective date to filter lines by.
        location_id (str, optional): The ID of the location to filter lines by. If not provided,
            lines from all locations will be returned.
        **kwargs: Additional keyword arguments passed to the API client request.

    Returns:
        Any: The processed result from the API request, typically containing line information
            matching the specified criteria.

    Raises:
        HTTPException: If the API request fails or returns an error status code.
        RequestException: If there is an issue with the request construction or execution.
    """
    current_lines_json: dict[str, str] = {
        "effective_date_id": effective_date_id,
    }

    if location_id:
        current_lines_json.update({"location_id": location_id})

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_lines", json=current_lines_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)


def list_policy_types(
    location_id: str,
    effective_date_id: str | None = None,
    effective_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieve policy types for a given location with optional effective date parameters.

    This function fetches policy types based on the provided location ID and effective date
    information. It requires either effective_date or effective_date_id to be specified.

    Args:
        location_id: The ID of the location for which to retrieve policy types
        effective_date_id: The ID of the effective date to filter policy types
        effective_date: The effective date to filter policy types
        **kwargs: Additional keyword arguments to pass to the API client

    Returns:
        The processed API response containing policy types information

    Raises:
        BritecoreError.MissingParameter: If neither effective_date nor effective_date_id is provided
    """

    if not effective_date and effective_date_id:
        BritecoreError.MissingParameter(
            "Either effective_date or effective_date is required"
        )

    parameter_list: list[dict[str, str | None]] = [
        {"effective_date": effective_date},
        {"effective_date_id": effective_date_id},
    ]
    parameter_priority: list[str] = ["effective_date_id", "effective_date"]

    policy_types_json: dict[str, str] = api_client.multiple_parameter_verification(
        parameter_list, parameter_priority
    )

    policy_types_json.update({"location_id": location_id})

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/lines/list_policy_types", json=policy_types_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)
