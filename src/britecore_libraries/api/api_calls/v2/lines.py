from json import loads
from typing import Any, Callable

import pyinputplus as py_menu
from urllib3 import HTTPResponse

from britecore_libraries.api.api_calls import api_client
from britecore_libraries import logger

LOGGER = logger

API_CLIENT = api_client


def get_export_line_file(
    line: tuple, line_type: str, line_name: str, **kwargs
) -> str | HTTPResponse | None | Any:
    """Gets line export
    :param line: Line ID
    :type line: str
    :param line_type: Export type (Line or Policy)
    :type line_type: str
    :param line_name: Name of line
    :type line_name: str
    :return: Export of selected line
    :rtype: dict[Any, Any] or str
    """
    request_result = ""
    LOGGER.info(f"Retrieving %f.yellow%{line_name}%f% lines")

    if line_type == "Line":
        web_request_json = {
            "curr_eff_date_id": line[0],
            "curr_line_id": line[2],
            "curr_state_id": line[1],
        }

        request_result = API_CLIENT.do_request(
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


def line_menu() -> tuple[
    Callable[[object], int],
    Callable[[object], int],
    Callable[[object], int],
    list[Any] | str | Any,
    list[Any] | str | Any,
    list[Any] | str | Any,
]:
    """Generates ids needed for get_lines.
    :return:effective date id, state id, line id(s),
    date name, state name, line name
    :rtype: tuple[list, list, list, list, list, list]
    """

    def print_menu(
        print_menu_title: str,
        print_menu_options: dict,
        print_menu_default: str,
    ) -> tuple[Callable[[object], int], list[Any] | str | Any]:
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
        print(
            f"\nChoose {print_menu_title.lower()}\n{'=' * (len(print_menu_title) + 7)}"
        )
        if len(print_menu_options) > 1:
            menu_options_list = list(print_menu_options.keys())
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
    request_results = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_effective_dates",
    )
    get_dates = API_CLIENT.process_result(request_results)

    LOGGER.debug("Getting states")
    menu_options = {}
    menu_default = ""
    for make_menu in get_dates:
        menu_options.update({make_menu["description"]: make_menu["id"]})
        menu_default = make_menu["description"]
    eff_date = print_menu("Date", menu_options, menu_default)
    eff_date_json = {"effective_date_id": eff_date[0]}

    request_results = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_states",
        json=eff_date_json,
    )
    get_states = API_CLIENT.process_result(request_results)

    menu_options = {}
    for make_menu in get_states:
        menu_options.update({make_menu["name"]: make_menu["id"]})
        menu_default = make_menu["name"]
    eff_state = print_menu("State", menu_options, menu_default)
    eff_state_json = {
        "effective_date_id": eff_date[0],
        "location_id": eff_state[0],
    }

    request_results = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_lines",
        json=eff_state_json,
    )
    all_lines = API_CLIENT.process_result(request_results)
    menu_options = {}
    menu_name = []
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


def get_all_effective_dates():
    request_results = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_effective_dates",
    )

    return API_CLIENT.process_result(request_results)


def get_all_states(effective_date_id):
    effective_date_json = {"effective_date_id": effective_date_id}

    request_results = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_states",
        json=effective_date_json,
    )

    return API_CLIENT.process_result(request_results)


def get_all_lines(effective_date_id, location_id):
    current_lines_json = {
        "effective_date_id": effective_date_id,
        "location_id": location_id,
    }

    request_results = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_lines",
        json=current_lines_json,
    )

    return API_CLIENT.process_result(request_results)


def list_policy_types(effective_date_id, location_id):
    policy_types_json = {
        "effective_date_id": effective_date_id,
        "location_id": location_id,
    }

    request_results = API_CLIENT.do_request(
        path="/api/v2/lines/list_policy_types",
        json=policy_types_json,
    )

    return API_CLIENT.process_result(request_results)
