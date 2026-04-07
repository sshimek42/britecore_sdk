"""Interactive CLI menu utilities for line selection.

This module provides interactive menu functionality for selecting BriteCore
line/policy parameters. It uses pyinputplus for user interaction and is
only loaded when interactive functionality is needed.
"""

from logging import Logger
from typing import Any, Unpack

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger
API_CLIENT: BritecoreAPIClient = api_client


def line_menu(
    **kwargs: Unpack[RequestParameters],
) -> tuple[Any, Any, Any, Any, Any, Any]:
    """
    Creates menus for each different line option.

    This function generates interactive menus to select effective date, state, and line
    options from API data. It handles user input for choosing from multiple options
    and returns the selected values along with their identifiers.

    Parameters:
        **kwargs: Request parameters (timeout, retries, etc.) passed to API client.

    Returns:
        A tuple containing (
            effective_date_ids: list of selected effective date IDs,
            location_ids: list of selected location IDs,
            line_ids: list of selected line IDs,
            effective_date_name: str name of selected effective date,
            state_name: str name of selected state,
            line_name: str name of selected line,
        )

    Raises:
        ImportError: If pyinputplus is not installed (optional dependency).
    """
    from urllib3 import BaseHTTPResponse, HTTPResponse

    request_result: BaseHTTPResponse | HTTPResponse | None

    def print_menu(
        print_menu_title: str,
        print_menu_options: dict,
        print_menu_default: str,
    ) -> tuple[Any, Any]:
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
        line_id: Any
        name: Any

        import pyinputplus as py_menu

        LOGGER.info(
            "\nChoose %s\n%s",
            print_menu_title.lower(),
            "=" * (len(print_menu_title) + 7),
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
            line_id = print_menu_options[print_menu_default]
            name = print_menu_default
        LOGGER.info("%s selected", tmp_line)
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
    eff_date = print_menu("Date", menu_options, menu_default)
    eff_date_json: dict[str, str | list[str]] | None = {
        "effective_date_id": eff_date[0]
    }

    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_states", json=eff_date_json, **kwargs
    )
    get_states: Any = API_CLIENT.process_result(request_result)

    menu_options = {}
    for make_menu in get_states:
        menu_options.update({make_menu["name"]: make_menu["id"]})
        menu_default = make_menu["name"]
    eff_state = print_menu("State", menu_options, menu_default)
    eff_state_json: dict[str, str | list[str]] = {
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
