"""BriteCore v2 Lines API endpoint wrappers.

Provides interactive and programmatic helpers for working with BriteCore
line/policy export data and line-menu selection flows.

Key functions:
    get_export_line_file -- Fetch export data for a specific line or policy type.
    line_menu            -- Interactive CLI menu for selecting effective date,
                            state, and line combinations.
"""

from json import loads
from logging import Logger
from typing import Any, Optional, Unpack

import pyinputplus as py_menu
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
    request_result: Optional[BaseHTTPResponse, HTTPResponse] = None
    LOGGER.info(f"Retrieving %f.yellow%{line_name}%f% lines")

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

    LOGGER.info(f"Finished retrieving %f.yellow%{line_name}%f% lines")

    API_CLIENT.process_results = API_CLIENT.process_result(request_result)
    if API_CLIENT.process_results is not None:
        return loads(API_CLIENT.process_results)

    return request_result


def line_menu(
    **kwargs: Unpack[RequestParameters],
) -> tuple[list, list, list, str, str, str]:
    """
    Creates menus for each different line option

    This function generates interactive menus to select effective date, state, and line
    options from API data. It handles user input for choosing from multiple options
    and returns the selected values along with their identifiers.

    :param print_menu_title: Title for the menu being displayed
    :type print_menu_title: str
    :param print_menu_options: Dictionary mapping option names to their identifiers
    :type print_menu_options: dict
    :param print_menu_default: Default selection option
    :type print_menu_default: str
    :return: Tuple containing the selected identifiers and names
    :rtype: tuple[list[Any], list[Any]] or tuple[list[Any], str]
    """
    request_result: Optional[BaseHTTPResponse, HTTPResponse]

    def print_menu(
        print_menu_title: str,
        print_menu_options: dict,
        print_menu_default: str,
    ) -> tuple[list, str]:
        """
        Display a menu with given title and options, and return the selected option's ID and name.

        This function prints a formatted menu based on the provided title and options,
        allows the user to make a selection, and returns the corresponding ID and name
        of the selected option. It supports both single and multiple options, handling
        special cases like "All" selection and default values.

        Parameters:
            print_menu_title: The title to display above the menu options.
            print_menu_options: A dictionary mapping option names to their corresponding IDs.
            print_menu_default: The default option to select if only one option is available.

        Returns:
            A tuple containing:
                - line_id: The ID of the selected option, which can be a string or a list of strings.
                - name: The name of the selected option, which can be a string or a list of strings.
        """
        line_id: str | list[str]
        name: str | list[str]

        LOGGER.info(
            f"\nChoose {print_menu_title.lower()}\n{'=' * (len(print_menu_title) + 7)}"
        )
        if len(print_menu_options) > 1:
            menu_options_list: list = list(print_menu_options.keys())
            tmp_line = py_menu.inputMenu(
                menu_options_list,
                lettered=False,
                numbered=True,
                prompt="",
                default=len(print_menu_options) + 1,
                blank=True,
            )
            if tmp_line in ("All", ""):
                line_id = list(print_menu_options.values())
                name = list(print_menu_options.keys())
            else:
                line_id = print_menu_options[tmp_line]
                name = tmp_line
        else:
            LOGGER.info("1. " + print_menu_default)
            tmp_line = print_menu_default
            line_id = print_menu_options[menu_default]
            name = menu_default
        LOGGER.info(f"{tmp_line} selected")
        return line_id, name

    LOGGER.debug("Getting dates")
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_effective_dates", **kwargs
    )
    get_dates: Any = API_CLIENT.process_result(request_result)

    LOGGER.debug("Getting states")
    menu_options: dict[str, str] = {}
    menu_default: str = ""
    for make_menu in get_dates:
        menu_options.update({make_menu["description"]: make_menu["id"]})
        menu_default = make_menu["description"]
    eff_date: tuple[list[str], str] = print_menu("Date", menu_options, menu_default)
    eff_date_json: dict[str, list[str]] | None = {"effective_date_id": eff_date[0]}

    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_states", json=eff_date_json, **kwargs
    )
    get_states: Any = API_CLIENT.process_result(request_result)

    menu_options = {}
    for make_menu in get_states:
        menu_options.update({make_menu["name"]: make_menu["id"]})
        menu_default = make_menu["name"]
    eff_state = print_menu("State", menu_options, menu_default)
    eff_state_json: dict[str, list[str]] = {
        "effective_date_id": eff_date[0],
        "location_id": eff_state[0],
    }

    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_lines", json=eff_state_json, **kwargs
    )
    all_lines: Any = API_CLIENT.process_result(request_result)
    menu_options: dict[str, str] = {}
    menu_name: list[str] = []
    for make_menu in all_lines:
        menu_options.update({make_menu["name"]: make_menu["id"]})
        menu_name.append(make_menu["name"])
    eff_line = print_menu("Line", menu_options, menu_name[0])

    return (
        eff_date[0],
        eff_state[0],
        eff_line[0],
        eff_date[1],
        eff_state[1],
        eff_line[1],
    )


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
    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
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

    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
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

    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
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

    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/lines/list_policy_types", json=policy_types_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)
