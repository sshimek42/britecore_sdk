"""Wrapper for BriteCore API calls"""

import sys
from json import dumps, loads

import pyinputplus as py_menu
import sclogging.sclogging_main as scl
import urllib3
from urllib3.exceptions import ProtocolError, RequestError, ResponseError
from urllib3.exceptions import TimeoutError as urlTimeoutError
from urllib3.util import Retry, Timeout, Url

from bclibs import settings
from bcoauth import OAuthToken

run_on = "wausau"
site_settings = settings.__getattr__("default")
site_settings += settings.__getattr__(run_on)

logger = scl.get_logger(__file__)
updated_logger = False
timers = True
bad_url_error = "Invalid URL"

if site_settings.base_url:
    base_url = Url(scheme="https", host=site_settings.base_url, path=None).url
    if base_url.endswith("/"):
        base_url = base_url[:-1]
else:
    logger.critical(bad_url_error)
    sys.exit(bad_url_error)

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


def process_result(response: urllib3.HTTPResponse, logs: bool = False) -> any:
    """Processes BriteCore response
    :param response: Request to parse
    :type response: HTTPResponse
    :param logs: Write full result to log
    :type logs: bool
    :return: Parsed data
    :rtype: any
    """
    logger.debug("Processing result")

    bc_data = None

    if response is None:
        logger.error("Error - No response")
        return None

    if response.status != 200:
        logger.error(f"Error - {response.status} - {response.reason}")
        return None

    json_result = loads(response.data.decode("utf-8"))

    bc_result = json_result.get("success", False)
    try:
        bc_message = json_result["message"]
    except KeyError:
        bc_message = json_result["messages"]

    if not bc_result:
        logger.error(f"Error - {bc_message}")
    else:
        bc_data = json_result.get("data")
        if logs:
            logger.debug(bc_data)

    if bc_data is None:
        logger.warning("No data returned")

    return bc_data


def do_request(
        path: str,
        json: dict = None,
        request_timeout: urllib3.util.Timeout = timeout,
        request_retries: urllib3.util.Retry = retries,
        request_headers=None,
        timer: bool = timers,
        timer_start_note: str = "",
        timer_end_note: str = "",
        method: str = "POST",
) -> urllib3.response:
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
    :rtype: HTTPResponse
    """
    if request_headers is None:
        request_headers = {}
    if not request_headers:
        request_headers = token_class.get_token()
    request_timer = ""
    global updated_logger  # skipcq: PYL-W0603
    global logger  # skipcq: PYL-W0603

    if not updated_logger:
        temp_logger = scl.get_parent_logger()
        if temp_logger is not None:
            logger = temp_logger
            updated_logger = True

    if timer:
        if not request_timer:
            request_timer = scl.Timer()
        request_timer.start_timer(timer_start_note)
    request_result = None
    try:
        if json:
            request_result = http.request(
                method=method,
                url=Url(host=base_url, path=path).url,
                headers=request_headers,
                body=dumps(json).encode("utf-8"),
                timeout=request_timeout,
                retries=request_retries,
            )
        else:
            request_result = http.request(
                method=method,
                url=Url(host=base_url, path=path).url,
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

    if timer:
        request_timer.stop_timer(timer_end_note)

    if not request_result:
        logger.error("Error getting request")

    return request_result


def get_bc_lines(
        bc_line: tuple, bc_type: str, line_name: str, **kwargs
) -> [dict[any, any], str]:
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
        return loads(process_results)

    return request_result


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
    ) -> [tuple[list[any], list[any]], tuple[list[any], str]]:
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
            f"\nChoose {print_menu_title.lower()}\n"
            f"{'=' * (len(print_menu_title) + 7)}"
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
            bc_id = print_menu_options.get(menu_default)
            bc_name = menu_default
        print(f"{tmp_line} selected")
        return bc_id, bc_name

    logger.debug("Getting dates")
    request_results = do_request(
        path="/api/v2/lines/get_all_effective_dates", timer=False
    )
    get_dates = process_result(request_results)

    logger.debug("Getting states")
    menu_options = {}
    menu_default = ""
    for make_menu in get_dates:
        menu_options.update({make_menu.get("description"): make_menu.get("id")})
        menu_default = make_menu.get("description")
    eff_date = print_menu("Date", menu_options, menu_default)
    eff_date_json = {"effective_date_id": eff_date[0]}

    request_results = do_request(
        path="/api/v2/lines/get_all_states",
        json=eff_date_json,
        timer=False,
    )
    get_states = process_result(request_results)

    menu_options = {}
    for make_menu in get_states:
        menu_options.update({make_menu.get("name"): make_menu.get("id")})
        menu_default = make_menu.get("name")
    eff_state = print_menu("State", menu_options, menu_default)
    eff_state_json = {
        "effective_date_id": eff_date[0],
        "location_id": eff_state[0],
    }

    request_results = do_request(
        path="/api/v2/lines/get_all_lines",
        json=eff_state_json,
        timer=False,
    )
    all_lines = process_result(request_results)
    menu_options = {}
    menu_name = []
    for make_menu in all_lines:
        menu_options.update({make_menu.get("name"): make_menu.get("id")})
        menu_name.append(make_menu.get("name"))
    eff_line = print_menu("Line", menu_options, menu_name[0])

    return (
        eff_date[0],
        eff_state[0],
        eff_line[0],
        eff_date[1],
        eff_state[1],
        eff_line[1],
    )


def get_bc_polices_w_line(line: str, **kwargs) -> dict:
    """Gets polices containing a single line item
    :param line: Line ID to search for
    :type line: str
    :return: Dictionary of policy numbers
    :rtype: dict
    """
    logger.debug("Searching for ID")
    policy_request_json = {"item_id": str(line)}
    request_result = do_request(
        path="/api/v2/lines/get_policies_with_line_item",
        json=policy_request_json,
        **kwargs,
    )
    policy_json = process_result(request_result)

    return policy_json.get("policies")


def add_bc_line(bc_revision: str, bc_line: str, **kwargs) -> bool:
    """Attempts to add specified line to a policy
    :param bc_revision: Policy revision ID
    :type bc_revision: str
    :param bc_line: Line ID to add
    :type bc_line: str
    :return: Result
    :rtype: bool
    """
    logger.debug("Adding line")
    line_add_json = {
        "item_id": str(bc_line),
        "revision_id": str(bc_revision),
    }
    request_result = do_request(
        path="/api/v2/policies/add_line_item",
        json=line_add_json,
        **kwargs,
    )
    line_json = process_result(request_result)

    if line_json is not None:
        logger.debug(line_json.get("added_items"))
        return bool(line_json.get("added_items"))

    return False


def retrieve_bc_policy_ids(policy: str, **kwargs) -> tuple[str, str]:
    """Retrieve a single policy and return data needed to add item to policy
    :param policy:Policy Number
    :type policy: str
    :return: Revision ID, Property ID
    :rtype: tuple[str, str]
    """
    logger.debug("Getting policy info")
    policy_json = get_bc_policy(policy, **kwargs)
    revision_id = policy_json["active_revision"]["id"]
    property_id = policy_json["active_revision"]["primary_property_id"]

    return revision_id, property_id


def get_bc_property_information(property_id: str, **kwargs) -> dict:
    """Retrieve a single property and return data needed to add item to policy
    :param property_id:Property ID
    :type property_id: str
    :return: Property data
    :rtype: dict
    """
    logger.debug("Getting property info")
    property_json = do_request(
        path="/api/v2/insured/get_property_information_and_photos",
        json={"property_id": property_id},
        **kwargs,
    )
    property_json = process_result(property_json)

    return property_json


def get_bc_contacts(
        search_str: str, search_filter: str = "Named Insured", **kwargs
) -> dict:
    """Retrieve named insured contacts
    :param search_str: Name to search for
    :type search_str: str
    :param search_filter: Name to search for
    :type search_filter: str
    :return: Contacts
    :rtype: dict
    """
    logger.debug(f"Searching for {search_str}")
    contact_request_json = {
        "searchString": search_str,
        "filter": search_filter,
        "currentPage": 1,
        "pageSize": 10000,
    }
    request_result = do_request(
        path="/api/v1/contacts/retrieveContactList",
        json=contact_request_json,
        **kwargs,
    )

    contact_json = loads(request_result.data.decode("utf-8"))

    return contact_json.get("records")


def retrieve_policy_list_user(
        contact_name: str, check_name: bool = True, **kwargs
) -> list:
    """Search for user
    :param contact_name: Contact to search for
    :type contact_name: str
    :param check_name: Match results to contact name
    :type contact_name: bool
    :return: List of polices
    :rtype: list
    """
    logger.debug(f"Searching for {contact_name}")
    user_request_json = {
        "sort_obj": {"field": "policy_number", "order": "asc"},
        "current_page": 1,
        "page_size": 10000,
        "search_string": contact_name,
    }
    request_result = do_request(
        path="/api/v2/policies/search",
        json=user_request_json,
        **kwargs,
    )
    user_json = process_result(request_result).get("records")

    policy_list = []

    contact_name = contact_name.strip().lower()

    if check_name:
        for each_policy in user_json:
            named_split = each_policy.get("namedInsured").split(", ")
            for each_contact in named_split:
                match_contact = each_contact.strip().lower()
                if contact_name in (match_contact, "*"):
                    policy_list.append(each_policy.get("policyNumber"))
    else:
        for each_policy in user_json:
            policy_list.append(each_policy.get("policyNumber"))

    return list(dict.fromkeys(policy_list))


def retrieve_bc_policy_contact_info(policy: str, **kwargs) -> list:
    """Get contact information from policy
    :param policy: Policy number
    :type policy: str
    :return: List of insured attached to the policy
    :rtype: list
    """
    logger.debug("Getting contact info")
    contact_json = get_bc_policy(policy, **kwargs)

    return contact_json.get("active_revision").get("named_insureds")


def add_bc_contact(
        name: str, address: list, phone: list, email: list, **kwargs
) -> tuple:
    """Add contact
    :param name: Contact name
    :type name: str
    :param address: List of contact's address dictionary
    :type address: list
    :param phone: List of contact's phone dictionary
    :type phone: list
    :param email: List of contact's email dictionary
    :type email: list
    :return: Full request result, new contact id
    :rtype: tuple
    """
    logger.debug("Creating contact")
    contact_request_json = {
        "name": name,
        "addresses": address,
    }
    contact_request_json.update(**kwargs)
    if email[0] != {}:
        contact_request_json.update({"emails": email})
    if phone[0] != {}:
        contact_request_json.update({"phones": phone})

    request_result = do_request(
        path="/api/v2/contacts/new_contact",
        json=contact_request_json,
    )

    contact_json = process_result(request_result)

    new_id = contact_json.get("contact_id", "Fail")
    if new_id == "Fail":
        logger.error(f"Failed to add contact - {name}")
        sys.exit(f"Failed to add contact - {name}")

    logger.debug(f"Added {name}")
    return contact_json, new_id


def add_bc_contact_role(contact_id, role="Named Insured", **kwargs) -> dict:
    """Adds role to existing contact
    :param contact_id: Contact ID
    :type contact_id: str
    :param role: Requested role (Defaults to "Named Insured")
    :type role: str
    :return: Results of request
    :rtype: dict
    """
    logger.debug("Adding role")
    role_request_json = {"contact_id": contact_id, "role_name": role}
    request_result = do_request(
        path="/api/v2/contacts/add_contact_to_role",
        json=role_request_json,
        **kwargs,
    )

    return process_result(request_result)


def update_bc_contact(contact: dict, **kwargs) -> dict:
    """Updates contact
    :param contact: Dictionary with changes
    :type contact: dict
    :return: Request result
    :rtype: dict
    """
    logger.debug("Updating contact")
    update_request_json = {"contact": contact}
    request_result = do_request(
        path="/api/v2/contacts/update_contact",
        json=update_request_json,
        **kwargs,
    )

    return process_result(request_result)


def new_bc_policy(policy: dict, **kwargs) -> tuple[bool, any]:
    """Creates new policy
    :param policy: Policy number
    :type policy: dict
    :return: Request result
    :rtype: bool
    """
    revision_id = None
    policy_id = None
    x_id = None
    a_id = None
    prop_id = None
    logger.debug("Creating policy")
    policy_request_json = policy
    request_result = do_request(
        path="/api/v2/policies/create_policy",
        json=policy_request_json,
        **kwargs,
    )

    policy_json = process_result(request_result)
    if policy_json:
        revision_id = policy_json["revision_id"]
        policy_id = policy_json["policy_id"]
        x_id = policy_json["revision_data"]["named_insureds"][0]
        a_id = policy_json["revision_data"]["agents"][0]
        prop_id = policy_json["revision_data"]["primary_property_id"]
    policy_create = True
    try:
        policy_exists = (
            loads(request_result.data.decode("utf-8")).get("data").get("exists")
        )
    except AttributeError:
        policy_exists = False
    if policy_json is None and not policy_exists:
        policy_create = False

    return policy_create, revision_id, policy_id, x_id, a_id, prop_id


def get_bc_policy(policy_number: str, **kwargs) -> dict:
    """Get policy information
    :param policy_number: Policy number
    :type policy_number: str
    :return: Request result
    :rtype: dict
    """
    logger.debug("Retrieving policy")
    policy_request_json = {"policy_number": policy_number}
    request_result = do_request(
        path="/api/v2/policies/retrieve_policy",
        json=policy_request_json,
        request_timeout=Timeout(web_timeout_long),
        **kwargs,
    )

    return process_result(request_result)


def get_bc_contact(contact_id: str, **kwargs) -> dict:
    """
    Gets contact info
    :param contact_id: Contact ID to lookup
    :type contact_id: str
    :param kwargs:
    :type kwargs:
    :return: Contact info
    :rtype: dict
    """
    logger.debug("Retrieving contact")
    contact_retrieve_json = {"contact_id": contact_id}
    request_result = do_request(
        path="/api/v2/contacts/get_contact",
        json=contact_retrieve_json,
        **kwargs,
    )

    return process_result(request_result)


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


def get_bc_policy_terms(policy_id: str, **kwargs) -> list[dict[str, list[dict]]]:
    """
    Gets term information from policy
    :param policy_id: Policy ID to retrieve
    :type policy_id: str
    :param kwargs:
    :type kwargs:
    :return: Policy info
    :rtype: list[dict[str, list[dict]]]
    """
    logger.debug("Retrieving terms")
    policy_retrieve_json = {"policy_id": policy_id}
    request_result = do_request(
        path="/api/v2/policies/retrieve_policy_terms",
        json=policy_retrieve_json,
        **kwargs,
    )

    return process_result(request_result)


def bc_rate_revision(revision: str, **kwargs) -> dict:
    """
    Re-rates policy revision
    :param revision: Revision ID
    :type revision: str
    :param kwargs:
    :type kwargs:
    :return:
    :rtype: dict
    """
    logger.debug("Re-rating policy")
    policy_retrieve_json = {"revision_id": revision}
    request_result = do_request(
        path="/api/v2/policies/rate_revision",
        json=policy_retrieve_json,
        **kwargs,
    )

    return process_result(request_result)


def retrieve_bc_revision(revision: str, **kwargs) -> dict:
    """
    Get revision details from revision
    :param revision: Revision ID
    :type revision: str
    :param kwargs:
    :type kwargs:
    :return: Revision details
    :rtype: dict
    """
    logger.debug("Getting revision")
    revision_retrieve_json = {"revision_id": revision}
    request_result = do_request(
        path="/api/v2/policies/retrieve_revision_details",
        json=revision_retrieve_json,
        request_timeout=Timeout(web_timeout_long),
        **kwargs,
    )

    return process_result(request_result)


def retrieve_bc_risks(revision: str, **kwargs) -> dict:
    """
    Get risk IDs from revision
    :param revision: Revision ID
    :type revision: str
    :param kwargs:
    :type kwargs:
    :return: Risk ID
    :rtype: dict
    """
    logger.debug("Getting risks")
    revision_retrieve_json = {"revision_id": revision}
    request_result = do_request(
        path="/api/v2/policies/retrieve_risks",
        json=revision_retrieve_json,
        **kwargs,
    )

    return process_result(request_result)


def retrieve_bc_risk_details(risk: str, **kwargs) -> dict:
    """
    Retrieves rick details
    :param risk: Risk ID
    :type risk: str
    :param kwargs:
    :type kwargs:
    :return: Risk details
    :rtype: dict
    """
    logger.debug("Getting risk details")
    revision_retrieve_json = {"risk_id": risk}
    request_result = do_request(
        path="/api/v2/policies/retrieve_risk_details",
        json=revision_retrieve_json,
        **kwargs,
    )

    return process_result(request_result)


def update_bc_rating_information(
        property_id: str, line: str, limit: int, **kwargs
) -> list:
    """
    Add/updates line item limit
    :param property_id Property ID
    :type property_id: str
    :param line: Line ID
    :type line: str
    :param limit: Line limit
    :type limit: int
    :param kwargs:
    :type kwargs:
    :return: Success/fail
    :rtype: list
    """
    logger.debug("Updating line item")
    revision_retrieve_json = {
        "property_id": property_id,
        "items": [{"id": line, "limit": limit}],
    }
    request_result = do_request(
        path="/api/v2/policies/update_rating_information",
        json=revision_retrieve_json,
        **kwargs,
    )

    return process_result(request_result)


def rate_bc_risk(risk_id: str, **kwargs) -> dict[str, float]:
    """
    Re-rates risk
    :param risk_id: Risk ID
    :type risk_id: str
    :param kwargs:
    :type kwargs:
    :return: Re-rated premium
    :rtype: Dict[str, float]
    """
    logger.debug("Re-rating policy")
    revision_retrieve_json = {"risk_id": risk_id}
    request_result = do_request(
        path="/api/v2/policies/rate_risk",
        json=revision_retrieve_json,
        **kwargs,
    )

    return process_result(request_result)


def rebuild_bc_search_index(index_to_rebuild: list, **kwargs) -> bool:
    """
    Rebuild BriteCore search indexes
    :param index_to_rebuild:
    :type index_to_rebuild: list
    :param kwargs:
    :type kwargs:
    :return: Result
    :rtype: bool
    """
    logger.debug("Rebuilding index")
    rebuild_index = {"only_build": index_to_rebuild}
    request_result = do_request(
        path="/api/v2/utils/rebuild_search_index",
        json=rebuild_index,
        **kwargs,
    )
    return process_result(request_result)


def retrieve_bc_policy_billing_schedule(policy: str, **kwargs) -> dict:
    """
    Retrieve policy billing information
    :param policy: Policy Number
    :type policy: str
    :param kwargs:
    :type kwargs:
    :return: Result
    :rtype: bool
    """
    logger.debug("Getting billing schedule")
    billing_search = {"policy_number": policy}
    request_result = do_request(
        path="/api/v2/policies/retrieve_billing_schedule_options",
        json=billing_search,
        **kwargs,
    )
    return process_result(request_result)


def get_bc_claim(claim_id: str, **kwargs) -> dict:
    """
    Retrieve policy claim information
    :param claim_id: Claim Number
    :type claim_id: str
    :param kwargs:
    :type kwargs:
    :return: Result
    :rtype: bool
    """
    logger.debug("Getting claim information")
    claim_search = {"claim_id": claim_id}
    request_result = do_request(
        path="/api/v2/claims/get_claim", json=claim_search, **kwargs
    )
    return process_result(request_result)


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


def get_bc_attachment(file_id: str, **kwargs) -> dict:
    """
    Retrieve policy attachment
    :param file_id: Attachment ID
    :type file_id: str
    :param kwargs:
    :type kwargs:
    :return: Attachment
    :rtype: dict
    """
    logger.debug("Getting attachment")
    file_search = {"file_id": file_id}
    request_result = do_request(
        path="/api/v2/deliverables/get_attachment", json=file_search, **kwargs
    )

    return process_result(request_result)


def add_bc_revision_contact(
        revision_id: str,
        contact_id: str,
        x_id,
        contact_role: str = "namedInsured",
        **kwargs,
) -> dict:
    """
    Add contact to revision
    :param revision_id: Revision ID
    :type revision_id: std
    :param contact_id: Contact ID
    :type contact_id: std
    :param contact_role: Contact Role - Defaults to 'namedInsured'
    :type contact_role: std
    :param kwargs:
    :type kwargs:
    :return: Attachment
    :rtype: dict
    """
    update_revision = None
    request_result = None
    logger.debug("Adding contact")

    contact_add = {
        "revision_id": revision_id,
        "role": contact_role,
    }

    if not x_id:
        request_result = do_request(
            path="/api/v2/policies/new_revision_contact", json=contact_add, **kwargs
        )

        contact_add_result = process_result(request_result)
    else:
        contact_add_result = {"x_revisions_contact_id": x_id}

    if contact_add_result:
        x_contact = contact_add_result.get("x_revisions_contact_id")
        update_revision_json = {
            "x_revisions_contact_id": x_contact,
            "contact_id": contact_id,
        }

        request_result = do_request(
            path="/api/v2/policies/update_revision_contact",
            json=update_revision_json,
            **kwargs,
        )

    return process_result(request_result)


def create_risk(rev_id: str, **kwargs):
    risk_json = {"revision_id": rev_id}

    request_result = do_request(
        path="/api/v2/policies/create_risk", json=risk_json, **kwargs
    )

    return process_result(request_result)


def update_property_location(prop_dict, **kwargs):
    prop_json = {"location": prop_dict}

    request_result = do_request(
        path="/api/v2/policies/update_property_location", json=prop_json, **kwargs
    )

    return process_result(request_result)


def update_inspection_dates(policy_num, insp_dict, **kwargs):
    insp_json = {"policy_number": policy_num, "payload": insp_dict}
    insp_json.update(insp_dict)

    request_result = do_request(
        path="/api/v2/inspections/update_inspection_dates", json=insp_json, **kwargs
    )

    return process_result(request_result)


def new_mortgagee(property_id: str, **kwargs):
    new_mort_json = {"property_id": property_id}
    result_request = do_request(
        "/api/v2/policies/new_mortgagee", json=new_mort_json, **kwargs
    )

    return process_result(result_request)


def store_mortgagee(property_contact_id: str, mortgagee_contact_id: str, **kwargs):
    store_mort_json = {
        "x_properties_contact_id": property_contact_id,
        "mortgagee_contact_id": mortgagee_contact_id,
    }
    result_request = do_request(
        "/api/v2/policies/store_mortgagee", json=store_mort_json, **kwargs
    )

    return process_result(result_request)


def get_tb_list(from_date, to_date, **kwargs):
    required_json = {"json_dict": {"from_date": from_date, "to_date": to_date, "ignore_state": True}}
    request_timeout = Timeout(120)
    request_retries = Retry(total=3, status_forcelist=frozenset({502, 503, 504}))

    result_request = do_request(
        "/api/v1/printing/getToBePrinted",
        json=required_json,
        request_timeout=request_timeout,
        request_retries=request_retries,
        **kwargs,
    )

    return_data = None
    if result_request:
        return_data = loads(result_request.data.decode("utf-8"))

    return return_data


def get_edeliverables(date_from, date_to, **kwargs):
    required_json = {"date_from": date_from, "date_to": date_to, "unprocessed_only": False}

    result_request = do_request(
        "/api/v2/deliverables/get_edeliverables",
        json=required_json,
        **kwargs,
    )

    return process_result(result_request)


def mark_as_printed(file_ids, **kwargs):
    required_json = {"file_ids": file_ids}

    result_request = do_request(
        "/api/v1/printing/markAsPrinted",
        json=required_json,
        **kwargs,
    )

    return process_result(result_request)


def list_files(report_id, **kwargs):
    required_json = {"report_id": report_id}

    result_request = do_request(
        "/api/v2/reports/list_files",
        json=required_json,
        **kwargs,
    )

    return process_result(result_request)


def retrieve_reports(**kwargs):
    required_json = None

    result_request = do_request(
        "/api/v2/reports/retrieve_reports"
    )

    return process_result(result_request)