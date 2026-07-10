"""Interactive CLI menu utilities for line selection.

This module provides interactive menu functionality for selecting BriteCore
line/policy parameters. It uses questionary for user interaction and is
only loaded when interactive functionality is needed.
"""

from logging import Logger
from typing import Any, Unpack

from britecore_sdk import logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger
API_CLIENT: BritecoreAPIClient = api_client


def _select_option(title: str, choices: list[str]) -> str:
    """Select a choice with questionary when available, else use plain stdin."""
    try:
        import questionary

        selected = questionary.select(f"Choose {title.lower()}:", choices=choices).ask()
        if selected is None:
            raise KeyboardInterrupt
        if not isinstance(selected, str):
            raise ValueError("Menu selection returned a non-string value")
        return selected
    except Exception as err:  # skipcq PYL-W0703
        # PyCharm/IDE runners may not provide a Win32 console buffer for prompt_toolkit.
        LOGGER.debug("Falling back to plain menu input: %s", err)

    for idx, choice in enumerate(choices, start=1):
        print(f"{idx}. {choice}")

    while True:
        raw = input("Enter selection number: ").strip()
        if not raw.isdigit():
            print("Please enter a valid number.")
            continue
        selected_index = int(raw)
        if 1 <= selected_index <= len(choices):
            return choices[selected_index - 1]
        print(f"Please select a number between 1 and {len(choices)}.")


def line_menu(
    **kwargs: Unpack[RequestParameters],
) -> dict[str, Any]:
    """
    Creates menus for each different line option.

    This function generates interactive menus to select effective date, state, and line
    options from API data. It handles user input for choosing from multiple options
    and returns the selected values along with their identifiers.

    Parameters:
        **kwargs: Request parameters (timeout, retries, etc.) passed to API client.

    Returns:
        A dict with ``line`` and ``line_name`` keys.

        When a specific line is selected (normal case)::

            {"line": (date_id, state_id, line_id), "line_name": str}

        This form can be passed directly to
        ``lines.get_export_line_file(**selection)``.

        When **all** lines are selected (only offered when more than one line
        exists for the chosen date + location)::

            {"line": [(date_id, state_id, line_id), ...], "line_name": "all"}

        Here ``line`` is a list of tuples — one per available line — and
        ``line_name`` is the string ``"all"``.  Callers should check
        ``result["line_name"] == "all"`` to distinguish this case and iterate
        ``result["line"]``.

    Uses questionary when available and falls back to plain stdin input when
    a console backend is unavailable (for example in some IDE run consoles).
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
        of the selected option.

        Parameters:
            print_menu_title: The title to display above the menu options.
            print_menu_options: A dictionary mapping option names to their corresponding IDs.
            print_menu_default: The option used when only one choice exists.

        Returns:
            A tuple containing:
                - line_id: The ID of the selected option.
                - name: The selected option name.
        """
        line_id: Any
        name: Any

        print(f"\nChoose {print_menu_title.lower()}")
        print("=" * (len(print_menu_title) + 7))

        if len(print_menu_options) > 1:
            menu_options_list: list = list(print_menu_options.keys())

            tmp_line = _select_option(print_menu_title, menu_options_list)

            line_id = print_menu_options[tmp_line]
            name = tmp_line
        else:
            print("1. " + print_menu_default)
            tmp_line = print_menu_default
            line_id = print_menu_options[print_menu_default]
            name = print_menu_default
        print(f"{tmp_line} selected")
        return line_id, name

    LOGGER.debug("Getting dates")
    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_effective_dates", **kwargs
    )
    get_dates: Any = API_CLIENT.process_result(request_result)

    LOGGER.debug("Getting states")
    date_menu_options: dict[str, str] = {}
    date_menu_default: str = ""
    for make_menu in get_dates:
        # Prefer explicit effective_date in menus; fall back for older payloads.
        date_label = (
            make_menu.get("effective_date")
            or make_menu.get("description")
            or str(make_menu.get("id"))
        )
        date_menu_options.update({date_label: make_menu["id"]})
        date_menu_default = date_label
    eff_date = print_menu("Date", date_menu_options, date_menu_default)
    eff_date_json: dict[str, str | list[str]] | None = {
        "effective_date_id": eff_date[0]
    }

    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_states", json=eff_date_json, **kwargs
    )
    get_states: Any = API_CLIENT.process_result(request_result)

    state_menu_options: dict[str, str] = {}
    state_menu_default: str = ""
    for make_menu in get_states:
        state_menu_options.update({make_menu["name"]: make_menu["id"]})
        state_menu_default = make_menu["name"]
    eff_state = print_menu("State", state_menu_options, state_menu_default)
    eff_state_json: dict[str, str | list[str]] = {
        "effective_date_id": eff_date[0],
        "location_id": eff_state[0],
    }

    request_result = API_CLIENT.do_request(
        path="/api/v2/lines/get_all_lines", json=eff_state_json, **kwargs
    )
    all_lines: Any = API_CLIENT.process_result(request_result)
    line_menu_options: dict[str, str] = {}
    line_menu_names: list[str] = []
    for make_menu in all_lines:
        line_menu_options.update({make_menu["name"]: make_menu["id"]})
        line_menu_names.append(make_menu["name"])

    print("\nChoose line")
    print("=" * len("Choose line"))

    if len(line_menu_options) > 1:
        line_choices = line_menu_names + ["all"]
        selected_line = _select_option("Line", line_choices)
        if selected_line == "all":
            print("all selected")
            return {
                "line": [
                    (eff_date[0], eff_state[0], line_menu_options[name])
                    for name in line_menu_names
                ],
                "line_name": "all",
            }
        line_id = line_menu_options[selected_line]
        print(f"{selected_line} selected")
        return {
            "line": (eff_date[0], eff_state[0], line_id),
            "line_name": selected_line,
        }
    default_name = line_menu_names[0]
    print("1. " + default_name)
    line_id = line_menu_options[default_name]
    print(f"{default_name} selected")
    return {
        "line": (eff_date[0], eff_state[0], line_id),
        "line_name": default_name,
    }


def policy_menu(**kwargs: Unpack[RequestParameters]) -> Any:
    """Interactive menu for selecting a policy from the retrieved policy list.

    Retrieves policies via ``/api/v2/policies/get_policies`` and presents an
    interactive menu so the user can select a policy by its policy number.
    Returns the selected policy object, or ``None`` when no policies are
    returned.

    Parameters:
        **kwargs: Request parameters forwarded to
            ``britecore_sdk.api.api_calls.v2.policies.get_policies``
            (filters, pagination, timeout, etc.).

    Returns:
        The selected policy ``dict`` from the API response, or ``None`` if
        the API returns no policies.

    Uses questionary when available and falls back to plain stdin input when
    a console backend is unavailable (for example in some IDE run consoles).
    """
    from britecore_sdk.api.api_calls.v2 import policies as _policies

    result = _policies.get_policies(**kwargs)
    policy_list: list[Any] = (
        result.get("policies", []) if isinstance(result, dict) else []
    )

    if not policy_list:
        LOGGER.warning("No policies returned from API")
        return None

    policy_labels: list[str] = [
        str(p.get("policyNumber") or p.get("policy_number") or p) for p in policy_list
    ]

    selected_label = _select_option("Policy", policy_labels)
    return next(
        (
            p
            for p in policy_list
            if str(p.get("policyNumber") or p.get("policy_number") or p)
            == selected_label
        ),
        None,
    )


def config_menu() -> None:
    """Interactive menu for site configuration management.

    Delegates to ConfigManager's interactive menu for adding, updating,
    deleting, and viewing site configurations.
    """
    from britecore_sdk.utils.config_manager import interactive_config_menu

    interactive_config_menu()
