from logging import Logger
from typing import Any, Literal, Optional, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse, Timeout

from britecore_libraries import BritecoreError, logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
    web_timeout_long,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def retrieve_policy(
    policy_number: Optional[str] = None,
    policy_id: Optional[str] = None,
    revision_state: Optional[str] = None,
    revision_id: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Get policy information from Policy Number, Policy ID or Revision ID (
    Priority order if multiple parameters are provided: Revision ID, Policy
    ID, Policy
    Number)
    :param policy_number: Policy number
    :type policy_number: str
    :param policy_id: Policy ID
    :type policy_id: str
    :param revision_id: Revision ID
    :type revision_id: str
    :param revision_state: Required Policy State
    :type revision_state: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Policy information
    :rtype: Any
    """
    LOGGER.debug("Retrieving policy")

    verification_list: list[dict[str, str | None]] = [
        {"policy_number": policy_number},
        {"policy_id": policy_id},
        {"revision_id": revision_id},
    ]

    priority_list: list[str] = ["revision_id", "policy_id", "policy_number"]

    policy_request_json: dict[str, str | None] = (
        api_client.multiple_parameter_verification(
            verification_list, priority_list)
    )

    if revision_state:
        policy_request_json.update({"revision_state": revision_state})

    provided_timeout: Optional[Timeout] = kwargs.get("request_timeout", None)
    if not provided_timeout:
        kwargs.update({"request_timeout": Timeout(web_timeout_long)})

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_policy",
        json=policy_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def add_line_item(
    revision_id: str,
    item_id: str,
    property_id: Optional[str] = "",
    sub_line_id: Optional[str] = "",
    link_id: Optional[str] = "",
    check_for_subline: Optional[bool] = False,
    **kwargs: Unpack[RequestParameters],
) -> bool:
    """
    Attempts to add specified line item to a policy
    :param revision_id: The UUID of an existing Revision
    :type revision_id: str
    :param item_id: The UUID of an existing Item
    :type item_id: str
    :param property_id: The UUID of an existing Property. Only needed for line items with property category
    :type property_id: Optional[str]
    :param sub_line_id: The UUID of an existing SubLine. Only needed if adding to an existing subline
    :type sub_line_id: Optional[str]
    :param link_id: The UUID of an existing link. Only needed if being added by another item's Underwriting Rules.
    :type link_id: Optional[str]
    :param check_for_subline: Set this to true if this item belongs in a subline that may not exist yet (Default: False)
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Result
    :rtype: bool
    """
    local_env: dict[str, Any] = locals()
    LOGGER.debug("Adding line")
    line_add_json: dict[str, Any] = api_client.json_dict_builder({**local_env})
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/add_line_item",
        json=line_add_json,
        **kwargs,
    )
    line_json = API_CLIENT.process_result(request_result)

    if line_json is not None:
        LOGGER.debug(line_json["added_items"])
        return bool(line_json["added_items"])

    return False


def retrieve_policy_ids(
    policy_number: str, **kwargs: Unpack[RequestParameters]
) -> tuple[str, str]:
    """Retrieve a single policy and return data needed to add item to
    policy
    :param policy_number:Policy Number
    :type policy_number: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Revision ID, Property ID
    :rtype: tuple[str, str]
    """
    LOGGER.debug("Getting policy info")
    policy_json = retrieve_policy(policy_number, **kwargs)
    active_revision = policy_json["active_revision"]
    revision_id = active_revision["id"]
    property_id = active_revision["primary_property_id"]

    return revision_id, property_id


def retrieve_policy_list_from_user(
    contact_name: str, check_name: bool = True, **kwargs: Unpack[RequestParameters]
) -> list:
    """Get policy list for user
    :param contact_name: Contact to search for
    :type contact_name: str
    :param check_name: Match results to contact name
    :type contact_name: bool
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: List of polices
    :rtype: list
    """
    LOGGER.debug(f"Searching for %f.yellow%{contact_name}%f%")
    user_request_json = {
        "sort_obj": {"field": "policy_number", "order": "asc"},
        "current_page": 1,
        "page_size": 100,
        "search_string": contact_name,
    }
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/search",
        json=user_request_json,
        **kwargs,
    )
    user_json = API_CLIENT.process_result(request_result)["records"]

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


def retrieve_policy_contact_info(
    policy_number: str, **kwargs: Unpack[RequestParameters]
) -> list:
    """Get contact information from policy
    :param policy_number: Policy number
    :type policy_number: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: List of insured attached to the policy
    :rtype: list
    """
    LOGGER.debug("Getting contact info")
    contact_json = retrieve_policy(policy_number, **kwargs)

    return contact_json["active_revision"]["named_insureds"]


def create_policy(
    policy_number: Optional[str] = "",
    policy_type_id: Optional[str] = "",
    inception_date: Optional[str] = "",
    term_type: Optional[
        Literal[
            "Custom",
            "3 Years",
            "18 Months",
            "1 Year",
            "9 Months",
            "6 Months",
            "3 Months",
        ]
    ] = "1 Year",
    expiration_date: Optional[str] = "",  # Required if term_type is "Custom"
    renewal_term_type: Optional[
        Literal["3 Years", "18 Months", "1 Year",
                "9 Months", "6 Months", "3 Months"]
    ] = "1 Year",
    is_renewal: Optional[bool] = False,
    as_agent: Optional[bool] = False,
    manual_policy_number: Optional[bool] = True,
    effective_date: Optional[str] = "",
    property_zip: Optional[str] = "",
    underwriting_questions: Optional[list] = None,
    underwriting_options: Optional[list] = None,
    external_system_reference: Optional[str] = "",
    **kwargs: Unpack[RequestParameters],
) -> tuple[Any, str]:
    """
    Creates a new policy
    :param policy_number: Defaults to the next system generated policy number is not specified
    :type policy_number: Optional[str]
    :param inception_date: Defaults to today (yyyy-mm-dd)
    :type inception_date: Optional[str]
    :param term_type: Policy term length - Options are "Custom","3 Years","18 Months","1 Year","9 Months","6 Months","3 Months" (Defaults to "1 Year")
    :type term_type: str
    :param expiration_date: Required if term_type is "Custom"
    :type expiration_date: Optional[str]
    :param renewal_term_type: Policy term length on renewal - Options are "3 Years","18 Months","1 Year","9 Months","6 Months","3 Months" (Defaults to "1 Year")
    :type renewal_term_type: str
    :param is_renewal: Create policy as a renewal (Default: False)
    :type is_renewal: bool
    :param underwriting_questions: Underwriting questions
    :type underwriting_questions: Optional[list]
    :param underwriting_options: Underwriting Options
    :type underwriting_options: Optional[list]
    :param as_agent: If true, creator and agent relations are based on logged in user (Default: False)
    :type as_agent: bool
    :param manual_policy_number: Indicates whether the policy number was manually assigned (Default: True)
    :type manual_policy_number: bool
    :param policy_type_id: Policy type UUID
    :type policy_type_id: Optional[str]
    :param effective_date: Required if effective_date is different from inception_date. Defaults to inception date (yyyy-mm-dd)
    :type effective_date: Optional[str]
    :param external_system_reference: External system reference
    :type external_system_reference: Optional[str]
    :param property_zip: Used to determine if there are suspensions for this zip code
    :type property_zip: Optional[str]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Policy JSON and revision_id
    :rtype: tuple[Any,str]
    """
    LOGGER.debug(f"Creating policy %f.yellow%{policy_number}%f%")
    local_env: dict[str, Any] = locals()
    policy_request_json: dict[str, Any] = api_client.json_dict_builder({
                                                                       **local_env})
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_policy",
        json=policy_request_json,
        **kwargs,
    )

    policy_json = API_CLIENT.process_result(request_result)

    return policy_json, policy_json["revision_id"]


def retrieve_policy_terms(
    policy_id: Optional[str] = "",
    policy_number: Optional[str] = "",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Gets term information from policy
    :param policy_id: Policy ID
    :type policy_id: Optional[str]
    :param policy_number: Policy number
    :type policy_number: Optional[str]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Policy terms
    :rtype: Any
    """
    LOGGER.debug("Retrieving terms")
    if not policy_number and policy_id:
        BritecoreError.MissingParameter(
            "Either policy_id or policy_number is required")

    parameter_list: list[dict[str, str]] = [
        {"policy_id": policy_id},
        {"policy_number": policy_number},
    ]
    parameter_priority: list[str] = ["policy_id", "policy_number"]

    policy_retrieve_json: dict[str, str] = api_client.multiple_parameter_verification(
        parameter_list, parameter_priority
    )
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_policy_terms",
        json=policy_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def rate_revision(revision_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Re-rates policy revision
    :param revision_id: Revision UUID
    :type revision_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Revision result
    :rtype: dict
    """
    LOGGER.debug(f"Re-rating revision %f.yellow%{revision_id}%f%")
    policy_retrieve_json = {"revision_id": revision_id}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/rate_revision",
        json=policy_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def retrieve_revision_details(
    revision_id: str,
    include_contact_details: Optional[bool] = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Get revision details from revision
    :param revision_id: Revision ID
    :type revision_id: str
    :param include_contact_details: Whether or not revision contact details are required (Default: True)
    :type include_contact_details: Optional[bool]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Revision details
    :rtype: Any
    """

    if not kwargs.get("request_timeout"):
        kwargs.update({"request_timeout": Timeout(web_timeout_long)})

    LOGGER.debug("Getting revision")
    revision_retrieve_json = {
        "revision_id": revision_id,
        "include_contact_details": include_contact_details,
    }
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_revision_details",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def retrieve_risks(
    revision_id: str,
    page: Optional[int] = 0,
    page_size: Optional[int] = 10,
    retrieve_remaining: Optional[bool] = True,
    order_by: Optional[str] = "name",
    risk_types: Optional[list[str]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieves paginated/filtered risks for a revision
    :param revision_id: The UUID of an existing Revision
    :type revision_id: str
    :param page: The page number of results (Default: 0)
    :type page: Optional[int]
    :param page_size: The maximum number of results per page (Default: 10)
    :type page_size: Optional[int]
    :param retrieve_remaining: Override page_size and get all remaining properties (Default: True)
    :type retrieve_remaining: Optional[bool]
    :param order_by: The attribute used to sort properties (Default: "name")
    :type order_by: Optional[str]
    :param risk_types: The types of risks to retrieve, defaults to None, meaning that it will return all types of risks (Default: None)
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: List of risks
    :rtype: Any
    """
    local_env = locals()
    LOGGER.debug("Getting risks")
    revision_retrieve_json = api_client.json_dict_builder({**local_env})
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_risks",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def retrieve_risk_details(risk_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieves rick details
    :param risk_id: Risk ID
    :type risk_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Risk details
    :rtype: Any
    """
    LOGGER.debug("Getting risk details")
    revision_retrieve_json = {"risk_id": risk_id}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_risk_details",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def update_rating_information(
    property_id: Optional[str] = "",
    revision_id: Optional[str] = "",
    items: list[dict[str, Any]] = None,
    reset_premium: Optional[bool] = True,
    **kwargs: Unpack[RequestParameters],
) -> list:
    """
    Updates an existing property/revision's rating information.
    :param property_id: Property UUID
    :type property_id: Optional[str]
    :param revision_id: Revision UUID
    :type revision_id: Optional[str]
    :param items: Items to update -
    If any key is empty, we assume you want to clear it.
    If you do not want to clear a field, leave the key out of your request.
    In other words, every key/value pair you send will be checked for discrepancies
    with the current data, and changes will be made.
    :type items: list[dict[str,Any]]
    :param reset_premium: Set to False if premiums should not be reset (Default: True)
    :type reset_premium: Optional[bool]
    :param kwargs:
    :type kwargs:
    :return: Update information
    :rtype: Any
    """
    local_env = locals()
    LOGGER.debug("Updating line item")
    revision_retrieve_json = api_client.json_dict_builder({**local_env})
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_rating_information",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


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
    LOGGER.debug("Re-rating policy")
    revision_retrieve_json = {"risk_id": risk_id}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/rate_risk",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


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
    LOGGER.debug("Getting billing schedule")
    billing_search = {"policy_number": policy}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_billing_schedule_options",
        json=billing_search,
        **kwargs,
    )
    return API_CLIENT.process_result(request_result)


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
    LOGGER.debug("Adding contact")

    contact_add = {
        "revision_id": revision_id,
        "role": contact_role,
    }

    if not x_id:
        request_result = API_CLIENT.do_request(
            path="/api/v2/policies/new_revision_contact", json=contact_add, **kwargs
        )

        contact_add_result = API_CLIENT.process_result(request_result)
    else:
        contact_add_result = {"x_revisions_contact_id": x_id}

    if contact_add_result:
        x_contact = contact_add_result["x_revisions_contact_id"]
        update_revision_json = {
            "x_revisions_contact_id": x_contact,
            "contact_id": contact_id,
        }

        request_result = API_CLIENT.do_request(
            path="/api/v2/policies/update_revision_contact",
            json=update_revision_json,
            **kwargs,
        )

    return API_CLIENT.process_result(request_result)


def create_risk(rev_id: str, **kwargs):
    risk_json = {"revision_id": rev_id}

    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_risk", json=risk_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)


def update_property_location(prop_dict, **kwargs):
    prop_json = {"location": prop_dict}

    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_property_location", json=prop_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)


def new_mortgagee(property_id: str, **kwargs):
    new_mort_json = {"property_id": property_id}
    result_request = API_CLIENT.do_request(
        "/api/v2/policies/new_mortgagee", json=new_mort_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def store_mortgagee(property_contact_id: str, mortgagee_contact_id: str, **kwargs):
    store_mort_json = {
        "x_properties_contact_id": property_contact_id,
        "mortgagee_contact_id": mortgagee_contact_id,
    }
    result_request = API_CLIENT.do_request(
        "/api/v2/policies/store_mortgagee", json=store_mort_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def retrieve_policy_snapshot(policy_number, snapshot_date, **kwargs):
    required_json = {"policy_number": policy_number,
                     "snapshot_date": snapshot_date}

    result_request = API_CLIENT.do_request(
        "/api/v2/policies/retrieve_policy_snapshot", json=required_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)
