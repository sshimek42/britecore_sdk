"""Wrapper for BriteCore API calls"""

import sys
from json import dumps, loads
from typing import Any, Dict, Optional  # added typing

import bcexceptions
import pyinputplus as py_menu
import sclogging.sclogging_main as scl
import urllib3
from o_auth_token_manager import OAuthToken
from urllib3.exceptions import ProtocolError, RequestError, ResponseError
from urllib3.exceptions import TimeoutError as urlTimeoutError
from urllib3.util import Retry, Timeout, Url

from bclibs import settings

run_on = "wausau"
site_settings = settings.__getattr__("default")
site_settings += settings.__getattr__(run_on)

logger = scl.get_logger(__file__)
LOGGER_UPDATED = False  # renamed from updated_logger
ENABLE_TIMERS = True  # renamed from timers
BAD_URL_ERROR = "Invalid URL"  # renamed from bad_url_error

if site_settings.base_url:
    base_url = Url(scheme="https", host=site_settings.base_url, path=None).url
    if base_url.endswith("/"):
        base_url = base_url[:-1]
else:
    logger.critical(BAD_URL_ERROR)
    sys.exit(BAD_URL_ERROR)

web_timeout = site_settings.web_timeout
if not web_timeout:
    web_timeout = 5

web_timeout_long = site_settings.web_timeout_long
if not web_timeout_long:
    web_timeout_long = web_timeout * 10

web_retry = site_settings.web_retry
if not web_retry:
    web_retry = 5

timeout = Timeout(web_timeout)
retries = Retry(total=web_retry, status_forcelist=frozenset({502, 503, 504}))
http = urllib3.PoolManager(retries=retries, timeout=timeout, maxsize=5, num_pools=5)

token_class = OAuthToken(site_settings.client_id, site_settings.client_secret, base_url)


# helper utilities
def _full_url(path: str) -> str:
    """Build a full URL using the configured base_url."""
    return Url(host=base_url, path=path).url


def _ensure_logger() -> None:
    """Ensure the module logger uses the parent logger if available (
    one-time)."""
    global LOGGER_UPDATED  # skipcq: PYL-W0603
    global logger  # skipcq: PYL-W0603
    if not LOGGER_UPDATED:
        plogger = scl.get_parent_logger()
        if plogger is not None:
            logger = plogger
            LOGGER_UPDATED = True


# ... existing code ...


def process_result(response: urllib3.HTTPResponse, logs: bool = False) -> Any:
    """Processes BriteCore response
    :param response: Request to parse
    :type response: HTTPResponse
    :param logs: Write full result to log
    :type logs: bool
    :return: Parsed data
    :rtype: any
    """
    logger.debug("Processing result")

    if response is None:
        logger.error("Error - No response")
        return None

    if response.status != 200:
        logger.error(f"Error - {response.status} - {response.reason}")
        return None

    json_result = loads(response.data.decode("utf-8"))

    bc_result = json_result.get("success", False)
    bc_message = json_result.get(
        "message", json_result.get("messages", "Unknown error")
    )

    if not bc_result:
        logger.error(f"Error - {bc_message}")
        raise bcexceptions.NoDataReturned(
            f"Error - {bc_message}",
            response.status,
        )

    bc_data = json_result.get("data")
    if logs:
        logger.debug(bc_data)

    if bc_data is None:
        logger.warning("No data returned")

    return bc_data


# ... existing code ...


def do_request(
    path: str,
    json: dict = None,
    request_timeout: urllib3.util.Timeout = timeout,
    request_retries: urllib3.util.Retry = retries,
    request_headers: Optional[Dict[str, Any]] = None,
    timer: bool = ENABLE_TIMERS,
    timer_start_note: str = "",
    timer_end_note: str = "",
    method: str = "POST",
) -> Optional[urllib3.HTTPResponse | None]:
    """Do web request
    :param path: URL to request
    :type path: str
    :param json: Request options
    :type json: dict
    :param request_timeout: urllib3 Timeout object
    :type request_timeout: urllib3.util.Timeout
    :param request_retries: urllib3 Retry object
    :type request_retries: urllib3.util.Retry
    :param request_headers: Headers (defaults to retrieving auth token)
    :type request_headers: dict
    :param timer: Option to time request
    :type timer: bool
    :param timer_start_note: Note for start timer
    :type timer_start_note: str
    :param timer_end_note: Note for stop timer
    :type timer_end_note: str
    :param method: POST, GET, etc.
    :type method: str
    :return: Request result
    :rtype: HTTPResponse | None
    """
    if request_headers is None:
        request_headers = {}
    if not request_headers:
        request_headers = token_class.get_authorization_headers()

    _ensure_logger()

    request_timer: Optional[scl.Timer] = None
    if timer:
        request_timer = scl.Timer()
        request_timer.start_timer(timer_start_note)
    request_result: Optional[urllib3.HTTPResponse] = None
    try:
        if json:
            request_result = http.request(
                method=method,
                url=_full_url(path),
                headers=request_headers,
                body=dumps(json).encode("utf-8"),
                timeout=request_timeout,
                retries=request_retries,
            )
        else:
            request_result = http.request(
                method=method,
                url=_full_url(path),
                headers=request_headers,
                timeout=request_timeout,
                retries=request_retries,
            )
    except (
        ProtocolError,
        ResponseError,
        urlTimeoutError,
        RequestError,
    ) as request_error:
        logger.error(request_error)

    if timer and request_timer is not None:
        request_timer.stop_timer(timer_end_note)

    if not request_result:
        logger.error("Error getting request")

    return request_result


# ... existing code ...


def get_bc_lines(
    bc_line: tuple, bc_type: str, line_name: str, **kwargs
) -> [dict[Any, Any], str]:
    """Gets line export
    :param bc_line: Line ID
    :type bc_line: str
    :param bc_type: Export type (Line or Policy)
    :type bc_type: str
    :param line_name: Name of line
    :type line_name: str
    :return: Export of selected line
    :rtype: dict[any, any] or str
    """
    request_result = ""
    logger.info(f"Retrieving %f.yellow%{line_name}%f% lines")

    if bc_type == "Line":
        web_request_json = {
            "curr_eff_date_id": bc_line[0],
            "curr_line_id": bc_line[2],
            "curr_state_id": bc_line[1],
        }

        request_result = do_request(
            path="/api/v2/lines/get_export_line_file",
            json=web_request_json,
            **kwargs,
        )
    elif bc_type == "Policy":
        request_result = do_request(path="/api/v2/policies/get_policies")

    logger.info(f"Finished retrieving %f.yellow%{line_name}%f% lines")

    process_results = process_result(request_result)
    if process_results is not None:
        # Some endpoints may return JSON as a string; parse only when needed.
        return (
            loads(process_results)
            if isinstance(process_results, str)
            else process_results
        )

    return request_result


# ... existing code ...


def bc_line_menu() -> tuple[list, list, list, list, list, list]:
    """Generates ids needed for get_bc_lines.
    :return:effective date id, state id, line id(s),
    date name, state name, line name
    :rtype: tuple[list, list, list, list, list, list]
    """

    def print_menu(
        print_menu_title: str,
        print_menu_options: dict,
        print_menu_default: str,
    ) -> [tuple[list[Any], list[Any]], tuple[list[Any], str]]:
        """Creates menus for each different line option
        :param print_menu_title: Title
        :type print_menu_title: str
        :param print_menu_options: Dictionary of options
        :type print_menu_options: dict
        :param print_menu_default: Default selection
        :type print_menu_default: str
        :return:
        :rtype: tuple[list[any], list[any]] or tuple[list[any], str]
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
                bc_id = list(print_menu_options.values())
                bc_name = list(print_menu_options.keys())
            else:
                bc_id = print_menu_options.get(tmp_line)
                bc_name = tmp_line
        else:
            print("1. " + print_menu_default)
            tmp_line = print_menu_default
            bc_id = print_menu_options.get(print_menu_default)  # fixed variable name
            bc_name = print_menu_default  # fixed variable name
        print(f"{tmp_line} selected")
        return bc_id, bc_name

    logger.debug("Getting dates")
    request_results = do_request(
        path="/api/v2/lines/get_all_effective_dates", timer=False
    )
    get_dates = process_result(request_results)

    # ... existing code ...


def get_bc_functions(**kwargs) -> dict:
    """
    Get available functions
    :param kwargs:
    :type kwargs:
    :return: Functions
    :rtype: dict
    """
    logger.debug("Retrieving functions")
    request_result = do_request(
        path="/api/v2/utils/get_available_function_names",
        **kwargs,
    )

    return process_result(request_result)


# ... existing code ...


def retrieve_bc_notes(policy_id: str) -> list:
    """
    Retrieve policy notes
    :param policy_id: Policy ID
    :type policy_id: str
    :return: Notes
    :rtype: list
    """
    logger.debug("Getting notes")
    notes_search = {"id": policy_id, "pageSize": 1000, "page": 0, "ascending": False}
    request_result = do_request(
        path="/api/v2/notes/retrieveNotes",
        json=notes_search,
        request_timeout=Timeout(web_timeout_long),
    )
    if not request_result:
        return []
    try:
        return loads(request_result.data.decode("utf-8"))["records"]
    except KeyError:
        return []


# ... existing code ...


def list_bc_attachments(policy_id: str, **kwargs) -> list:
    """
    Retrieve policy attachments
    :param policy_id: Policy Id
    :type policy_id: str
    :param kwargs:
    :type kwargs:
    :return: Attachments
    :rtype: list
    """
    logger.debug("Getting attachments")
    attachments_search = {"policy_id": policy_id}
    request_result = do_request(
        path="/api/v2/deliverables/list_attachments", json=attachments_search, **kwargs
    )

    return process_result(request_result)


# ... existing code ...


def retrieve_reports(**kwargs):
    required_json = {"payload": ""}

    result_request = do_request(
        "/api/v2/reports/retrieve_reports",
        json=required_json,  # send structured payload
        **kwargs,
    )

    return process_result(result_request)


# ... existing code ...
