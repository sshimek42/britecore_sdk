import os
from datetime import datetime
from json import loads
from typing import Any, Callable, Dict

import pyinputplus as py_menu
from api.britecore_api_client import _LOGGER, BritecoreAPIClient
from urllib3 import HTTPResponse
from urllib3.util import Retry, Timeout

web_timeout_long = BritecoreAPIClient.web_timeout_long


def init_api_client(target_site=None):
    if not target_site:
        target_site = os.environ.get("target_site")
    _api_client = BritecoreAPIClient(target_site).init_client()


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
    _LOGGER.info(f"Retrieving %f.yellow%{line_name}%f% lines")

    if line_type == "Line":
        web_request_json = {
            "curr_eff_date_id": line[0],
            "curr_line_id": line[2],
            "curr_state_id": line[1],
        }

        request_result = BritecoreAPIClient.do_request(
            path="/api/v2/lines/get_export_line_file",
            json=web_request_json,
            **kwargs,
        )
    elif line_type == "Policy":
        request_result = BritecoreAPIClient.do_request(
            path="/api/v2/policies/get_policies"
        )

    _LOGGER.info(f"Finished retrieving %f.yellow%{line_name}%f% lines")

    BritecoreAPIClient.process_results = BritecoreAPIClient.process_result(
        request_result
    )
    if BritecoreAPIClient.process_results is not None:
        return loads(BritecoreAPIClient.process_results)

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

    _LOGGER.debug("Getting dates")
    request_results = BritecoreAPIClient.do_request(
        path="/api/v2/lines/get_all_effective_dates",
    )
    get_dates = BritecoreAPIClient.process_result(request_results)

    _LOGGER.debug("Getting states")
    menu_options = {}
    menu_default = ""
    for make_menu in get_dates:
        menu_options.update({make_menu["description"]: make_menu["id"]})
        menu_default = make_menu["description"]
    eff_date = print_menu("Date", menu_options, menu_default)
    eff_date_json = {"effective_date_id": eff_date[0]}

    request_results = BritecoreAPIClient.do_request(
        path="/api/v2/lines/get_all_states",
        json=eff_date_json,
    )
    get_states = BritecoreAPIClient.process_result(request_results)

    menu_options = {}
    for make_menu in get_states:
        menu_options.update({make_menu["name"]: make_menu["id"]})
        menu_default = make_menu["name"]
    eff_state = print_menu("State", menu_options, menu_default)
    eff_state_json = {
        "effective_date_id": eff_date[0],
        "location_id": eff_state[0],
    }

    request_results = BritecoreAPIClient.do_request(
        path="/api/v2/lines/get_all_lines",
        json=eff_state_json,
    )
    all_lines = BritecoreAPIClient.process_result(request_results)
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


def get_policies_with_line_item(line: str, **kwargs) -> dict:
    """Gets polices containing a single line item
    :param line: Line ID to search for
    :type line: str
    :return: Dictionary of policy numbers
    :rtype: dict
    """
    _LOGGER.debug("Searching for ID")
    policy_request_json = {"item_id": str(line)}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/lines/get_policies_with_line_item",
        json=policy_request_json,
        **kwargs,
    )
    policy_json = BritecoreAPIClient.process_result(request_result)

    return policy_json["policies"]


def add_line_item(revision: str, line: str, **kwargs) -> bool:
    """Attempts to add specified line to a policy
    :param revision: Policy revision ID
    :type revision: str
    :param line: Line ID to add
    :type line: str
    :return: Result
    :rtype: bool
    """
    _LOGGER.debug("Adding line")
    line_add_json = {
        "item_id": str(line),
        "revision_id": str(revision),
    }
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/add_line_item",
        json=line_add_json,
        **kwargs,
    )
    line_json = BritecoreAPIClient.process_result(request_result)

    if line_json is not None:
        _LOGGER.debug(line_json["added_items"])
        return bool(line_json["added_items"])

    return False


def retrieve_policy_ids(policy: str, **kwargs) -> tuple[str, str]:
    """Retrieve a single policy and return data needed to add item to
    policy
    :param policy:Policy Number
    :type policy: str
    :return: Revision ID, Property ID
    :rtype: tuple[str, str]
    """
    _LOGGER.debug("Getting policy info")
    policy_json = retrieve_policy(policy, **kwargs)
    active_revision = policy_json["active_revision"]
    revision_id = active_revision["id"]
    property_id = active_revision["primary_property_id"]

    return revision_id, property_id


def get_property_information_and_photos(property_id: str, **kwargs) -> dict:
    """Retrieve a single property and return data needed to add item to
    policy
    :param property_id:Property ID
    :type property_id: str
    :return: Property data
    :rtype: dict
    """
    _LOGGER.debug("Getting property info")
    property_json = BritecoreAPIClient.do_request(
        path="/api/v2/insured/get_property_information_and_photos",
        json={"property_id": property_id},
        **kwargs,
    )
    property_json = BritecoreAPIClient.process_result(property_json)

    return property_json


def retrieve_contact_list(
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
    contact_request_json = {
        "searchString": search_str,
        "filter": search_filter,
        "currentPage": 1,
        "pageSize": 10,
    }
    request_result = BritecoreAPIClient.do_request(
        path="/api/v1/contacts/retrieveContactList",
        json=contact_request_json,
        **kwargs,
    )

    contact_json = loads(request_result.data.decode("utf-8"))

    return contact_json["records"]


def retrieve_policy_list_from_user(
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
    _LOGGER.debug(f"Searching for {contact_name}")
    user_request_json = {
        "sort_obj": {"field": "policy_number", "order": "asc"},
        "current_page": 1,
        "page_size": 100,
        "search_string": contact_name,
    }
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/search",
        json=user_request_json,
        **kwargs,
    )
    user_json = BritecoreAPIClient.process_result(request_result)["records"]

    policy_list = []

    contact_name = contact_name.strip().lower()

    if check_name:
        for each_policy in user_json:
            named_split = each_policy["namedInsured"].split(", ")
            for each_contact in named_split:
                match_contact = each_contact.strip().lower()
                if contact_name in (match_contact, "*"):
                    policy_list.append(each_policy["policyNumber"])
    else:
        for each_policy in user_json:
            policy_list.append(each_policy["policyNumber"])

    return list(dict.fromkeys(policy_list))


def retrieve_policy_contact_info(policy: str, **kwargs) -> list:
    """Get contact information from policy
    :param policy: Policy number
    :type policy: str
    :return: List of insured attached to the policy
    :rtype: list
    """
    _LOGGER.debug("Getting contact info")
    contact_json = retrieve_policy(policy, **kwargs)

    return contact_json["active_revision"]["named_insureds"]


def new_contact(
    name: str,
    address: list,
    phone: list,
    email: list,
    contact_type: str = "individual",
    **kwargs,
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
    :param contact_type: Contact type (Defaults to "individual")
    :type contact_type: str
    """
    _LOGGER.debug("Creating contact")
    if not phone:
        phone = [{}]
    if not email:
        email = [{}]
    contact_request_json = {
        "name": name,
        "addresses": address,
    }
    contact_request_json.update(**kwargs)
    if email[0] != {}:
        contact_request_json.update({"emails": email})
    if phone[0] != {}:
        contact_request_json.update({"phones": phone})

    contact_request_json.update({"type": contact_type})

    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/contacts/new_contact",
        json=contact_request_json,
    )

    contact_json = BritecoreAPIClient.process_result(request_result)

    try:
        new_id = contact_json.get("contact_id", "Fail")
    except AttributeError:
        new_id = "Fail"

    if new_id == "Fail":
        _LOGGER.error(f"Failed to add contact - {name}")
        return None, None

    _LOGGER.debug(f"Added {name}")
    return contact_json, new_id


def add_contact_to_role(contact_id, role="Named Insured", **kwargs) -> dict:
    """Adds role to existing contact
    :param contact_id: Contact ID
    :type contact_id: str
    :param role: Requested role (Defaults to "Named Insured")
    :type role: str
    :return: Results of request
    :rtype: dict
    """
    _LOGGER.debug("Adding role")
    role_request_json = {"contact_id": contact_id, "role_name": role}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/contacts/add_contact_to_role",
        json=role_request_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def update_contact(contact: dict, **kwargs) -> dict:
    """Updates contact
    :param contact: Dictionary with changes
    :type contact: dict
    :return: Request result
    :rtype: dict
    """
    _LOGGER.debug("Updating contact")
    update_request_json = {"contact": contact}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/contacts/update_contact",
        json=update_request_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def create_policy(
    policy_number: str,
    policy_type_id: str,
    inception_date: str = "",
    term_type: str = "1 Year",
    renewal_term_type: str = "1 Year",
    is_renewal: bool = True,
    as_agent: bool = False,
    manual_policy_number: bool = True,
    effective_date: str = "",
    **kwargs,
):
    # revision_id = None
    # policy_id = None
    # x_id = None
    # a_id = None
    # prop_id = None
    _LOGGER.debug("Creating policy")
    policy_request_json = {
        "policy_number": policy_number,
        "policy_type_id": policy_type_id,
        "inception_date": inception_date,
        "term_type": term_type,
        "renewal_term_type": renewal_term_type,
        "is_renewal": is_renewal,
        "as_agent": as_agent,
        "manual_policy_number": manual_policy_number,
        "effective_date": effective_date,
    }
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/create_policy",
        json=policy_request_json,
        **kwargs,
    )

    # policy_create = False

    policy_json = BritecoreAPIClient.process_result(request_result)
    # if policy_json:
    #     # revision_id = policy_json["revision_id"]
    #     # policy_id = policy_json["policy_id"]
    #     # x_id = policy_json["revision_data"]["named_insureds"][0]
    #     # a_id = policy_json["revision_data"]["agents"][0]
    #     # prop_id = policy_json["revision_data"]["primary_property_id"]
    #     policy_create = True
    # try:
    #     policy_exists = (
    #         loads(request_result.data.decode("utf-8")).get("data").get(
    #         "exists")
    #     )
    # except AttributeError:
    #     policy_exists = False
    # if policy_json is None and not policy_exists:
    #     policy_create = False

    return policy_json, policy_json["revision_id"]


def retrieve_policy(policy_number: str, **kwargs) -> dict:
    """Get policy information
    :param policy_number: Policy number
    :type policy_number: str
    :return: Request result
    :rtype: dict
    """
    _LOGGER.debug("Retrieving policy")
    policy_request_json = {"policy_number": policy_number}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/retrieve_policy",
        json=policy_request_json,
        request_timeout=Timeout(web_timeout_long),
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def get_contact(contact_id: str, **kwargs) -> dict:
    """
    Gets contact info
    :param contact_id: Contact ID to lookup
    :type contact_id: str
    :param kwargs:
    :type kwargs:
    :return: Contact info
    :rtype: dict
    """
    _LOGGER.debug("Retrieving contact")
    contact_retrieve_json = {"contact_id": contact_id}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/contacts/get_contact",
        json=contact_retrieve_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def get_available_function_names(**kwargs) -> dict:
    """
    Get available functions
    :param kwargs:
    :type kwargs:
    :return: Functions
    :rtype: dict
    """
    _LOGGER.debug("Retrieving functions")
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/utils/get_available_function_names",
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def retrieve_policy_terms(policy_id: str, **kwargs) -> list[dict[str, list[dict]]]:
    """
    Gets term information from policy
    :param policy_id: Policy ID to retrieve
    :type policy_id: str
    :param kwargs:
    :type kwargs:
    :return: Policy info
    :rtype: list[dict[str, list[dict]]]
    """
    _LOGGER.debug("Retrieving terms")
    policy_retrieve_json = {"policy_id": policy_id}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/retrieve_policy_terms",
        json=policy_retrieve_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def rate_revision(revision: str, **kwargs) -> dict:
    """
    Re-rates policy revision
    :param revision: Revision ID
    :type revision: str
    :param kwargs:
    :type kwargs:
    :return:
    :rtype: dict
    """
    _LOGGER.debug("Re-rating policy")
    policy_retrieve_json = {"revision_id": revision}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/rate_revision",
        json=policy_retrieve_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def retrieve_revision_details(revision: str, **kwargs) -> dict:
    """
    Get revision details from revision
    :param revision: Revision ID
    :type revision: str
    :param kwargs:
    :type kwargs:
    :return: Revision details
    :rtype: dict
    """
    _LOGGER.debug("Getting revision")
    revision_retrieve_json = {"revision_id": revision}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/retrieve_revision_details",
        json=revision_retrieve_json,
        request_timeout=Timeout(web_timeout_long),
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def retrieve_risks(revision: str, **kwargs) -> dict:
    """
    Get risk IDs from revision
    :param revision: Revision ID
    :type revision: str
    :param kwargs:
    :type kwargs:
    :return: Risk ID
    :rtype: dict
    """
    _LOGGER.debug("Getting risks")
    revision_retrieve_json = {"revision_id": revision}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/retrieve_risks",
        json=revision_retrieve_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def retrieve_risk_details(risk: str, **kwargs) -> dict:
    """
    Retrieves rick details
    :param risk: Risk ID
    :type risk: str
    :param kwargs:
    :type kwargs:
    :return: Risk details
    :rtype: dict
    """
    _LOGGER.debug("Getting risk details")
    revision_retrieve_json = {"risk_id": risk}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/retrieve_risk_details",
        json=revision_retrieve_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def update_rating_information(
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
    _LOGGER.debug("Updating line item")
    revision_retrieve_json = {
        "property_id": property_id,
        "items": [{"id": line, "limit": limit}],
    }
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/update_rating_information",
        json=revision_retrieve_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def rate_risk(risk_id: str, **kwargs) -> dict[str, float]:
    """
    Re-rates risk
    :param risk_id: Risk ID
    :type risk_id: str
    :param kwargs:
    :type kwargs:
    :return: Re-rated premium
    :rtype: Dict[str, float]
    """
    _LOGGER.debug("Re-rating policy")
    revision_retrieve_json = {"risk_id": risk_id}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/rate_risk",
        json=revision_retrieve_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def rebuild_search_index(index_to_rebuild: list, **kwargs) -> bool:
    """
    Rebuild BriteCore search indexes
    :param index_to_rebuild:
    :type index_to_rebuild: list
    :param kwargs:
    :type kwargs:
    :return: Result
    :rtype: bool
    """
    _LOGGER.debug("Rebuilding index")
    rebuild_index = {"only_build": index_to_rebuild}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/utils/rebuild_search_index",
        json=rebuild_index,
        **kwargs,
    )
    return BritecoreAPIClient.process_result(request_result)


def retrieve_policy_billing_schedule(policy: str, **kwargs) -> dict:
    """
    Retrieve policy billing information
    :param policy: Policy Number
    :type policy: str
    :param kwargs:
    :type kwargs:
    :return: Result
    :rtype: bool
    """
    _LOGGER.debug("Getting billing schedule")
    billing_search = {"policy_number": policy}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/retrieve_billing_schedule_options",
        json=billing_search,
        **kwargs,
    )
    return BritecoreAPIClient.process_result(request_result)


def get_claim(claim_id: str, **kwargs) -> dict:
    """
    Retrieve policy claim information
    :param claim_id: Claim Number
    :type claim_id: str
    :param kwargs:
    :type kwargs:
    :return: Result
    :rtype: bool
    """
    _LOGGER.debug("Getting claim information")
    claim_search = {"claim_id": claim_id}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/claims/get_claim", json=claim_search, **kwargs
    )
    return BritecoreAPIClient.process_result(request_result)


def retrieve_notes(policy_id: str) -> list:
    """
    Retrieve policy notes
    :param policy_id: Policy ID
    :type policy_id: str
    :return: Notes
    :rtype: list
    """
    _LOGGER.debug("Getting notes")
    notes_search = {
        "id": policy_id,
        "pageSize": 1000,
        "page": 0,
        "ascending": False,
    }
    request_result = BritecoreAPIClient.do_request(
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


def list_attachments(policy_id: str, **kwargs) -> list:
    """
    Retrieve policy attachments
    :param policy_id: Policy Id
    :type policy_id: str
    :param kwargs:
    :type kwargs:
    :return: Attachments
    :rtype: list
    """
    _LOGGER.debug("Getting attachments")
    attachments_search = {"policy_id": policy_id}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/deliverables/list_attachments",
        json=attachments_search,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def get_attachment(file_id: str, **kwargs) -> dict:
    """
    Retrieve policy attachment
    :param file_id: Attachment ID
    :type file_id: str
    :param kwargs:
    :type kwargs:
    :return: Attachment
    :rtype: dict
    """
    _LOGGER.debug("Getting attachment")
    file_search = {"file_id": file_id}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/deliverables/get_attachment", json=file_search, **kwargs
    )

    return BritecoreAPIClient.process_result(request_result)


def new_revision_contact(
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
    :param x_id: x_id
    :param kwargs:
    :type kwargs:
    :return: Attachment
    :rtype: dict
    """
    request_result = None
    _LOGGER.debug("Adding contact")

    contact_add = {
        "revision_id": revision_id,
        "role": contact_role,
    }

    if not x_id:
        request_result = BritecoreAPIClient.do_request(
            path="/api/v2/policies/new_revision_contact", json=contact_add, **kwargs
        )

        contact_add_result = BritecoreAPIClient.process_result(request_result)
    else:
        contact_add_result = {"x_revisions_contact_id": x_id}

    if contact_add_result:
        x_contact = contact_add_result["x_revisions_contact_id"]
        update_revision_json = {
            "x_revisions_contact_id": x_contact,
            "contact_id": contact_id,
        }

        request_result = BritecoreAPIClient.do_request(
            path="/api/v2/policies/update_revision_contact",
            json=update_revision_json,
            **kwargs,
        )

    return BritecoreAPIClient.process_result(request_result)


def create_risk(rev_id: str, **kwargs):
    risk_json = {"revision_id": rev_id}

    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/create_risk", json=risk_json, **kwargs
    )

    return BritecoreAPIClient.process_result(request_result)


def update_property_location(prop_dict, **kwargs):
    prop_json = {"location": prop_dict}

    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/policies/update_property_location", json=prop_json, **kwargs
    )

    return BritecoreAPIClient.process_result(request_result)


def update_inspection_dates(policy_number, inspection_dict, **kwargs):
    inspection_json = {"policy_number": policy_number,
                       "payload": inspection_dict}
    # inspection_json.update(inspection_json)

    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/inspections/update_inspection_dates",
        json=inspection_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def new_mortgagee(property_id: str, **kwargs):
    new_mort_json = {"property_id": property_id}
    result_request = BritecoreAPIClient.do_request(
        "/api/v2/policies/new_mortgagee", json=new_mort_json, **kwargs
    )

    return BritecoreAPIClient.process_result(result_request)


def store_mortgagee(property_contact_id: str, mortgagee_contact_id: str, **kwargs):
    store_mort_json = {
        "x_properties_contact_id": property_contact_id,
        "mortgagee_contact_id": mortgagee_contact_id,
    }
    result_request = BritecoreAPIClient.do_request(
        "/api/v2/policies/store_mortgagee", json=store_mort_json, **kwargs
    )

    return BritecoreAPIClient.process_result(result_request)


def get_to_be_printed(from_date, to_date, **kwargs):
    required_json = {
        "json_dict": {
            "from_date": from_date,
            "to_date": to_date,
            "ignore_state": True,
        }
    }
    request_timeout = Timeout(120)
    request_retries = Retry(
        total=3, status_forcelist=frozenset({502, 503, 504}))

    result_request = BritecoreAPIClient.do_request(
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
    required_json = {
        "date_from": date_from,
        "date_to": date_to,
        "unprocessed_only": False,
    }

    result_request = BritecoreAPIClient.do_request(
        "/api/v2/deliverables/get_edeliverables",
        json=required_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(result_request)


def mark_as_printed(file_ids, **kwargs):
    required_json = {"file_ids": file_ids}

    result_request = BritecoreAPIClient.do_request(
        "/api/v1/printing/markAsPrinted",
        json=required_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(result_request)


def list_files(report_id, **kwargs):
    required_json = {"report_id": report_id}

    result_request = BritecoreAPIClient.do_request(
        "/api/v2/reports/list_files",
        json=required_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(result_request)


def retrieve_reports(**kwargs):
    required_json = None

    result_request = BritecoreAPIClient.do_request(
        "/api/v2/reports/retrieve_reports", json=required_json, **kwargs
    )

    return BritecoreAPIClient.process_result(result_request)


def retrieve_report(report_id, **kwargs):
    required_json = {"report_id": report_id}

    result_request = BritecoreAPIClient.do_request(
        "/api/v2/reports/retrieve_report", json=required_json, **kwargs
    )

    return BritecoreAPIClient.process_result(result_request)


def retrieve_policy_snapshot(policy_number, snapshot_date, **kwargs):
    required_json = {"policy_number": policy_number,
                     "snapshot_date": snapshot_date}

    result_request = BritecoreAPIClient.do_request(
        "/api/v2/policies/retrieve_policy_snapshot", json=required_json, **kwargs
    )

    return BritecoreAPIClient.process_result(result_request)


def find_contact_by_params(name, **kwargs):
    _LOGGER.debug("Retrieving contact")
    contact_retrieve_json = {"name": name}
    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/contacts/find_contact_by_params",
        json=contact_retrieve_json,
        **kwargs,
    )

    return BritecoreAPIClient.process_result(request_result)


def create_full_quote(
    number,
    policy_type_id,
    agency_id,
    named_insureds,
    risks,
    policy_number_origin="manual",
    underwriting_questions=None,
    transaction_type="renewal",
    term_type="1 Year",
    inception_date=datetime.today().strftime("%Y-%m-%d"),
    **kwargs,
):
    if not underwriting_questions:
        underwriting_questions = []

    quote_json = {
        "number": number,
        "number_origin": policy_number_origin,
        "underwriting_questions": underwriting_questions,
        "effective_date": datetime.today().strftime("%Y-%m-%d"),
        "policy_type_id": policy_type_id,
        "transaction_type": transaction_type,
        "term_type": term_type,
        "agency_id": agency_id,
        "named_insureds": named_insureds,
        "risks": risks,
        "inception_date": inception_date,
    }

    request_result = BritecoreAPIClient.do_request(
        path="/api/v2/quotes/create_full_quote", json=quote_json, **kwargs
    )

    json_info = BritecoreAPIClient.process_result(request_result)

    if not json_info:
        return None, None

    return json_info, json_info["id"]
