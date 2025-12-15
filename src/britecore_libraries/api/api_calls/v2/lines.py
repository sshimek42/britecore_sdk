from json import loads
from logging import Logger
from typing import Any, Optional, Unpack

import pyinputplus as py_menu
from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger, BritecoreError
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def get_export_line_file(
    line: tuple, line_type: str, line_name: str, include_custom_sequences: Optional[bool] = False, **kwargs: Unpack[RequestParameters]
) -> Any:
    """Gets line export
    :param line: Line ID
    :type line: str
    :param line_type: Export type (Line or Policy)
    :type line_type: str
    :param line_name: Name of line
    :type line_name: str
    :param include_custom_sequences: Whether or not to include any non-default data from custom_sequences that is associated with the policy types (Default False)
    :type include_custom_sequences: bool
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Export of selected line
    :rtype: Any
    """
    request_result: Optional[BaseHTTPResponse, HTTPResponse] = None
    LOGGER.info(f"Retrieving %f.yellow%{line_name}%f% lines")

    if line_type == "Line":
        web_request_json: dict[str, str | bool] = {
            "curr_eff_date_id": line[0],
            "curr_line_id": line[2],
            "curr_state_id": line[1],
            "include_custom_sequences":include_custom_sequences
            }

        request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
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


def line_menu(**kwargs: Unpack[RequestParameters]) -> tuple[list, list, list, str, str, str]:
    """Generates ids needed for get_lines.
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: effective date id, state id, line id(s), date name, state name, line name
    :rtype: tuple[list, list, list, list, list, list]
    """
    request_result: Optional[BaseHTTPResponse, HTTPResponse]

    def print_menu(
        print_menu_title: str,
        print_menu_options: dict,
        print_menu_default: str,
    ) -> tuple[list, str]:
        """Creates menus for each different line option
        :param print_menu_title: Title
        :type print_menu_title: str
        :param print_menu_options: Dictionary of options
        :type print_menu_options: dict
        :param print_menu_default: Default selection
        :type print_menu_default: str
        :return:
        :rtype: tuple[list[Any], list[Any]] or tuple[list[Any], str]
        """
        line_id: str | list[str]
        name: str | list[str]

        print(
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
            print("1. " + print_menu_default)
            tmp_line = print_menu_default
            line_id = print_menu_options[menu_default]
            name = menu_default
        print(f"{tmp_line} selected")
        return line_id, name

    LOGGER.debug("Getting dates")
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_effective_dates",
        **kwargs
    )
    get_dates: Any = API_CLIENT.process_result(request_result)

    LOGGER.debug("Getting states")
    menu_options: dict[str, str] = {}
    menu_default: str = ""
    for make_menu in get_dates:
        menu_options.update({make_menu["description"]: make_menu["id"]})
        menu_default = make_menu["description"]
    eff_date: tuple[list[str], str] = print_menu("Date", menu_options, menu_default)
    eff_date_json: Optional[dict[str, list[str]]] = {"effective_date_id": eff_date[0]}

    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_states",
        json=eff_date_json,
        **kwargs
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
        path="/api/v2/lines/get_all_lines",
        json=eff_state_json,
        **kwargs
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
    """Get all effective dates
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: All effective line dates
    :rtype: Any
    """
    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_effective_dates",
        **kwargs
    )

    return API_CLIENT.process_result(request_result)


def get_all_states(effective_date_id: Optional[str] = None, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Returns all states using effective date
    :param effective_date_id: Effective Date ID
    :type effective_date_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: All active states
    :rtype: Any
    """

    effective_date_json: Optional[dict[str,str]] = {}

    if effective_date_id:
        effective_date_json = {"effective_date_id": effective_date_id}

    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_states",
        json=effective_date_json,
        **kwargs
    )

    return API_CLIENT.process_result(request_result)


def get_all_lines(effective_date_id: str, location_id: Optional[str] = None, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Gets all active lines from provided effective date_id and state_id
    :param effective_date_id: Effective Date ID
    :type effective_date_id: str
    :param location_id: State ID
    :type location_id: Optional[str]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: line_ids for provided effective_date_id and location_id
    :rtype: Any
    """
    current_lines_json: dict[str, str] = {
        "effective_date_id": effective_date_id,
    }

    if location_id:
        current_lines_json.update({"location_id": location_id})

    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_lines",
        json=current_lines_json,
        **kwargs
    )

    return API_CLIENT.process_result(request_result)


def list_policy_types(location_id: str, effective_date_id: Optional[str] = None,  effective_date: Optional[str] = None, **kwargs:Unpack[RequestParameters]) -> Any:
    """
    Gets all active policy types from provided effective date (or effective date id) and state id
    :param effective_date_id: Effective Date ID
    :type effective_date_id: str
    :param effective_date: Effective Date (yyyy-mm-dd)
    :type effective_date: str
    :param location_id: State ID
    :type location_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: policy_ids for provided effective_date_id and location_id
    :rtype: Any
    """

    if not effective_date and effective_date_id:
        BritecoreError.MissingParameter("Either effective_date or effective_date is required")

    parameter_list: list[dict[str, str | None]] = [{"effective_date": effective_date},
                                                {"effective_date_id": effective_date_id}]
    parameter_priority: list[str] = ["effective_date_id", "effective_date"]

    policy_types_json: dict[str, str] = api_client.multiple_parameter_varification(parameter_list,parameter_priority)

    policy_types_json.update({"location_id": location_id})

    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/lines/list_policy_types",
        json=policy_types_json,
        **kwargs
    )

    return API_CLIENT.process_result(request_result)
