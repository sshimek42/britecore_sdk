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
    Retrieves policy information based on provided criteria.

    This function fetches policy details from the API using either policy number,
    policy ID, or revision ID. It supports additional parameters and timeout
    configuration.

    Parameters:
        policy_number: Optional string representing the policy number.
        policy_id: Optional string representing the policy ID.
        revision_state: Optional string representing the revision state.
        revision_id: Optional string representing the revision ID.
        **kwargs: Additional keyword arguments passed to the API client.

    Returns:
        The result of the API request processing, typically containing policy data.

    Raises:
        Any exceptions raised by the underlying API client or request processing.

    Note:
        The function uses multiple parameter verification to determine which
        identifier to use for the request, prioritizing revision_id, then policy_id,
        then policy_number. If revision_state is provided, it's included in the
        request payload.
    """
    LOGGER.debug("Retrieving policy")

    verification_list: list[dict[str, str | None]] = [
        {"policy_number": policy_number},
        {"policy_id": policy_id},
        {"revision_id": revision_id},
    ]

    priority_list: list[str] = ["revision_id", "policy_id", "policy_number"]

    policy_request_json: dict[str, str | None] = (
        API_CLIENT.multiple_parameter_verification(
            verification_list, priority_list)
    )

    if revision_state:
        policy_request_json.update({"revision_state": revision_state})

    provided_timeout: Optional[Timeout] = kwargs.get("request_timeout")
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
    Add a line item to a revision.

    This function adds a line item to a specified revision using the API client.
    It constructs a JSON payload with the provided parameters and sends a request
    to the API endpoint for adding line items.

    Args:
        revision_id: The ID of the revision to add the line item to.
        item_id: The ID of the item to add.
        property_id: The ID of the property associated with the item. Defaults to empty string.
        sub_line_id: The ID of the sub-line item. Defaults to empty string.
        link_id: The ID of the link associated with the item. Defaults to empty string.
        check_for_subline: Whether to check for sub-line items. Defaults to False.
        **kwargs: Additional keyword arguments to pass to the API request.

    Returns:
        True if the line item was successfully added, False otherwise.

    Raises:
        Any exceptions raised by the API client during the request or processing.
    """
    local_env: dict[str, Any] = locals()
    LOGGER.debug("Adding line")
    line_add_json: dict[str, Any] = API_CLIENT.json_dict_builder({**local_env})
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
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
    """
    Retrieve policy IDs from policy information.

    This function fetches policy details using the provided policy number and
    extracts the revision ID and primary property ID from the active revision
    of the policy.

    Args:
        policy_number: The policy number to retrieve information for
        **kwargs: Additional request parameters to pass to the retrieval function

    Returns:
        A tuple containing the revision ID and property ID as strings

    Raises:
        Any exceptions raised by the underlying retrieve_policy function

    """
    LOGGER.debug("Getting policy info")
    policy_json: Any = retrieve_policy(policy_number, **kwargs)
    active_revision: Any = policy_json["active_revision"]
    revision_id: Any = active_revision["id"]
    property_id: Any = active_revision["primary_property_id"]

    return revision_id, property_id


def retrieve_policy_list_from_user(
    contact_name: str, check_name: bool = True, **kwargs: Unpack[RequestParameters]
) -> list:
    """
    Retrieves a list of policy numbers associated with a specified contact name.

    This function searches for policies linked to a given contact name by querying
    an API endpoint. It supports optional filtering based on the contact name
    and ensures that duplicate policy numbers are removed from the result.

    Args:
        contact_name: The name of the contact to search for within policy records.
        check_name: A flag indicating whether to perform a detailed name matching
            check. If True, the function will verify that the contact name matches
            the named insured field in the policy records. Defaults to True.
        **kwargs: Additional keyword arguments to pass to the API request, such as
            headers or authentication parameters.

    Returns:
        A list of unique policy numbers associated with the specified contact name.
        The list is sorted in ascending order by policy number.

    Raises:
        Any exceptions raised by the underlying API client or JSON processing functions are propagated as-is.
    """
    LOGGER.debug(f"Searching for %f.yellow%{contact_name}%f%")
    user_request_json: dict[str, Any] = {
        "sort_obj": {"field": "policy_number", "order": "asc"},
        "current_page": 1,
        "page_size": 100,
        "search_string": contact_name,
    }
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
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
    """
    Retrieve contact information for policyholders based on policy number.

    This function fetches the contact details of named insureds associated with a
    given policy number by retrieving the policy data and extracting the relevant
    contact information from the active revision.

    Parameters
    ----------
    policy_number : str
        The unique identifier for the policy
    **kwargs : Unpack[RequestParameters]
        Additional keyword arguments for the request parameters

    Returns
    -------
    list
        A list of contact information for the named insureds associated with the policy

    Raises
    ------
    Any exceptions raised by the underlying retrieve_policy function

    Notes
    -----
    The function logs a debug message before retrieving policy data. The returned
    contact information is extracted from the "active_revision" section of the
    policy data under "named_insureds".
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
    Creates a policy with the specified parameters and returns the policy JSON and revision ID.

    This function constructs a policy request using the provided parameters and sends it to the
    API endpoint for policy creation. It handles validation of required fields based on the
    term type and processes the API response to extract the policy data and revision ID.

    Parameters:
        policy_number: The policy number, optional.
        policy_type_id: The ID of the policy type, optional.
        inception_date: The inception date of the policy, optional.
        term_type: The term type of the policy, defaults to "1 Year". Must be one of:
            "Custom", "3 Years", "18 Months", "1 Year", "9 Months", "6 Months", "3 Months".
        expiration_date: The expiration date of the policy, required if term_type is "Custom".
        renewal_term_type: The renewal term type, defaults to "1 Year".
        is_renewal: Indicates if the policy is a renewal, defaults to False.
        as_agent: Indicates if the policy is created as an agent, defaults to False.
        manual_policy_number: Indicates if the policy number is manually entered, defaults to True.
        effective_date: The effective date of the policy, optional.
        property_zip: The zip code of the property, optional.
        underwriting_questions: List of underwriting questions, optional.
        underwriting_options: List of underwriting options, optional.
        external_system_reference: Reference to an external system, optional.
        **kwargs: Additional keyword arguments passed to the API client request.

    Returns:
        A tuple containing the policy JSON data and the revision ID.

    Raises:
        BritecoreError.MissingParameter: If term_type is "Custom" and expiration_date is not provided.
    """

    if term_type == "Custom" and not expiration_date:
        BritecoreError.MissingParameter(
            "expiation_date needed with 'Custom' term_type")

    LOGGER.debug(f"Creating policy %f.yellow%{policy_number}%f%")
    local_env: dict[str, Any] = locals()
    policy_request_json: dict[str, Any] = API_CLIENT.json_dict_builder({
                                                                       **local_env})
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
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
    Retrieve policy terms based on policy ID or policy number.

    This function fetches policy terms from the API using either a policy ID or policy number.
    It validates that at least one of these parameters is provided and constructs the appropriate
    request payload for the API call.

    Args:
        policy_id: Optional string representing the policy ID
        policy_number: Optional string representing the policy number
        **kwargs: Additional keyword arguments passed to the underlying API client

    Returns:
        The result of processing the API response, typically containing policy terms data

    Raises:
        BritecoreError.MissingParameter: When neither policy_id nor policy_number is provided
    """
    LOGGER.debug("Retrieving terms")
    if not policy_number and not policy_id:
        BritecoreError.MissingParameter(
            "Either policy_id or policy_number is required")

    parameter_list: list[dict[str, str]] = [
        {"policy_id": policy_id},
        {"policy_number": policy_number},
    ]
    parameter_priority: list[str] = ["policy_id", "policy_number"]

    policy_retrieve_json: dict[str, str] = API_CLIENT.multiple_parameter_verification(
        parameter_list, parameter_priority
    )
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_policy_terms",
        json=policy_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def rate_revision(revision_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Rate a revision by ID using the API client.

    This function sends a request to rate a specific revision identified by its ID.
    It constructs a policy retrieval JSON object with the revision ID and makes
    a request to the '/api/v2/policies/rate_revision' endpoint. The function logs
    the operation using the LOGGER debug level.

    Parameters:
        revision_id (str): The unique identifier of the revision to be rated.
        **kwargs (Unpack[RequestParameters]): Additional keyword arguments that
            are passed to the API client's do_request method for configuring
            the HTTP request.

    Returns:
        Any: The processed result from the API client's response handling.
    """
    LOGGER.debug(f"Re-rating revision %f.yellow%{revision_id}%f%")
    policy_retrieve_json = {"revision_id": revision_id}
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
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
    Retrieve detailed information about a specific revision.

    This function fetches comprehensive details about a revision identified by its ID.
    It allows optional inclusion of contact details in the response and supports
    additional request parameters through keyword arguments.

    Parameters:
        revision_id (str): Unique identifier of the revision to retrieve.
        include_contact_details (bool, optional): Flag indicating whether to include
            contact details in the response. Defaults to True.
        **kwargs: Additional keyword arguments passed to the underlying request
            implementation. These may include timeout settings and other request
            parameters.

    Returns:
        Any: The processed result from the API request, typically containing
            revision details and optionally contact information.

    Raises:
        Any exceptions raised by the underlying API client or request processing
            mechanisms are propagated as-is.
    """

    if not kwargs.get("request_timeout"):
        kwargs.update({"request_timeout": Timeout(web_timeout_long)})

    LOGGER.debug("Getting revision")
    revision_retrieve_json = {
        "revision_id": revision_id,
        "include_contact_details": include_contact_details,
    }
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
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
    Retrieve risks for a given revision with optional pagination and filtering.

    This function fetches risk information associated with a specific revision ID,
    allowing for customized retrieval through various parameters such as page size,
    ordering, and risk type filtering.

    Parameters:
        revision_id (str): The unique identifier of the revision for which risks are to be retrieved.
        page (Optional[int]): The page number to retrieve, starting from 0. Defaults to 0.
        page_size (Optional[int]): The number of risks to retrieve per page. Defaults to 10.
        retrieve_remaining (Optional[bool]): Whether to retrieve all remaining risks beyond the current page. Defaults to True.
        order_by (Optional[str]): The field to order results by. Defaults to "name".
        risk_types (Optional[list[str]]): A list of risk types to filter results by. Defaults to None.
        **kwargs (Unpack[RequestParameters]): Additional keyword arguments to pass to the underlying request.

    Returns:
        Any: The processed result from the API request, typically containing risk data.

    Raises:
        Any exceptions raised by the underlying API client or request processing.
    """
    local_env = locals()
    LOGGER.debug("Getting risks")
    revision_retrieve_json = API_CLIENT.json_dict_builder({**local_env})
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_risks",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def retrieve_risk_details(risk_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve detailed information about a specific risk identified by risk_id.

    This function fetches comprehensive details about a risk from the API by
    making a request to the /api/v2/policies/retrieve_risk_details endpoint.

    Parameters
    ----------
    risk_id : str
        Unique identifier of the risk to retrieve details for
    **kwargs : Unpack[RequestParameters]
        Additional keyword arguments to pass to the API request

    Returns
    -------
    Any
        The result of processing the API response, typically containing
        detailed risk information

    Notes
    -----
    - This function uses the global API_CLIENT instance to make requests
    - The function logs debug information before making the request
    - The request is made to the /api/v2/policies/retrieve_risk_details endpoint
    - The risk_id is included in the request payload as "risk_id"
    """
    LOGGER.debug("Getting risk details")
    revision_retrieve_json = {"risk_id": risk_id}
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
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
) -> Any:
    """
    Update rating information for a property.

    This function sends a request to update rating information for a specified property
    using the API client. It constructs a JSON payload with the provided parameters
    and makes a POST request to the update_rating_information endpoint.

    Args:
        property_id: The ID of the property for which rating information is being updated.
                     Defaults to empty string.
        revision_id: The revision ID associated with the rating information update.
                     Defaults to empty string.
        items: List of dictionaries containing rating information items to update.
               Defaults to empty list.
        reset_premium: Flag indicating whether to reset premium status during update.
                       Defaults to True.
        **kwargs: Additional keyword arguments to be passed to the API client request.

    Returns:
        The processed result from the API client after updating rating information.

    Raises:
        Any exceptions raised by the API client during the request or result processing.
    """
    local_env = locals()
    LOGGER.debug("Updating line item")
    revision_retrieve_json = API_CLIENT.json_dict_builder({**local_env})
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/policies/update_rating_information",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def rate_risk(risk_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Re-rates a risk item by making a request to the policy rating API endpoint.

    This function sends a request to re-rate a specific risk identified by its ID.
    It constructs a JSON payload with the risk ID and forwards additional
    keyword arguments to the API client for the request.

    Parameters:
        risk_id (str): The unique identifier of the risk item to be re-rated.
        **kwargs (Unpack[RequestParameters]): Additional parameters to be passed
            to the API client's request method, such as headers, timeout settings,
            or authentication details.

    Returns:
        Any: The result of processing the API response, typically containing
            the updated risk rating information or status.

    Raises:
        Any exceptions that may occur during the API request or result processing
            are propagated from the underlying API client methods.
    """
    LOGGER.debug("Re-rating policy")
    revision_retrieve_json = {"risk_id": risk_id}
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/policies/rate_risk",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def retrieve_billing_schedule_options(
    policy_number: Optional[str] = "",
    policy_term_id: Optional[str] = "",
    ignore_billing_schedule_roles: Optional[bool] = False,
    **kwargs,
) -> dict:
    """
    Retrieve billing schedule options for a policy.

    This function fetches the available billing schedule options for a given policy
    either by policy number or policy term ID. It constructs a request with the
    provided parameters and returns the processed API response.

    Parameters:
        policy_number: The policy number to retrieve billing schedule options for
        policy_term_id: The policy term ID to retrieve billing schedule options for
        ignore_billing_schedule_roles: Flag to ignore billing schedule roles when
            retrieving options
        **kwargs: Additional keyword arguments to pass to the API client

    Returns:
        Dictionary containing the billing schedule options

    Raises:
        BritecoreError.MissingParameter: When neither policy_number nor policy_term_id
            is provided
    """

    if not policy_term_id and not policy_term_id:
        BritecoreError.MissingParameter(
            "Either policy_number or policy_term_id is needed"
        )

    local_env = locals()

    LOGGER.debug("Getting billing schedule")
    billing_search_json: dict[str, Any] = API_CLIENT.json_dict_builder({
                                                                       **local_env})
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_billing_schedule_options",
        json=billing_search_json,
        **kwargs,
    )
    return API_CLIENT.process_result(request_result)


def new_revision_contact(
    revision_id: str,
    contact_id: str,
    x_id: Optional[str] = None,
    contact_role: Optional[
        Literal[
            "namedInsured", "addtlInterest", "financeCompany", "underwriter", "driver"
        ]
    ] = "namedInsured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Add a contact to a revision and update the revision with the contact information.

    This function associates a contact with a specific revision by first creating
    a contact entry and then updating the revision with the contact details.
    The contact can be assigned a specific role such as 'namedInsured', 'addtlInterest',
    'financeCompany', 'underwriter', or 'driver'. If an x_id is provided, the function
    will skip the initial contact creation step and directly use the provided x_id.

    Args:
        revision_id (str): The unique identifier of the revision to which the contact will be added.
        contact_id (str): The unique identifier of the contact to be associated with the revision.
        x_id (str, optional): The external revision contact ID. If provided, skips the initial
            contact creation step and uses this ID directly.
        contact_role (Literal["namedInsured", "addtlInterest", "financeCompany", "underwriter", "driver"], optional):
            The role of the contact within the revision. Defaults to "namedInsured".
        **kwargs (Unpack[RequestParameters]): Additional parameters to be passed to the API request.

    Returns:
        Any: The result of processing the API response, typically containing the updated
            revision contact information or the result of the API call.
    """
    contact_add_result: Any

    request_result: Any = None
    LOGGER.debug("Adding contact")

    contact_add_json: dict[
        Literal["revision_id", "role"],
        Literal[
            "namedInsured", "addtlInterest", "financeCompany", "underwriter", "driver"
        ]
        | str
        | None,
    ] = {
        "revision_id": revision_id,
        "role": contact_role,
    }

    if not x_id:
        request_result: Optional[BaseHTTPResponse | HTTPResponse] = (
            API_CLIENT.do_request(
                path="/api/v2/policies/new_revision_contact",
                json=contact_add_json,
                **kwargs,
            )
        )

        contact_add_result = API_CLIENT.process_result(request_result)
    else:
        contact_add_result = {"x_revisions_contact_id": x_id}

    if contact_add_result:
        x_contact: Any = contact_add_result["x_revisions_contact_id"]
        update_revision_json: dict[str, str] = {
            "x_revisions_contact_id": x_contact,
            "contact_id": contact_id,
        }

        request_result: Optional[BaseHTTPResponse | HTTPResponse] = (
            API_CLIENT.do_request(
                path="/api/v2/policies/update_revision_contact",
                json=update_revision_json,
                **kwargs,
            )
        )

    return API_CLIENT.process_result(request_result)


def create_risk(
    revision_id: str,
    property_group_number: Optional[int] = None,
    building_number: Optional[int] = None,
    force_categories: Optional[bool] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Create a risk assessment for a policy.

    This function generates a risk assessment by sending a request to the API endpoint
    for creating risk data. It accepts various parameters related to policy revision
    and property details, and returns the processed result from the API call.

    Parameters:
        revision_id (str): The unique identifier for the policy revision.
        property_group_number (int, optional): The property group number associated
            with the risk assessment. Defaults to None.
        building_number (int, optional): The building number related to the risk
            assessment. Defaults to None.
        force_categories (bool, optional): Flag to force category assignment for
            the risk assessment. Defaults to None.
        **kwargs (Unpack[RequestParameters]): Additional keyword arguments that
            are passed to the underlying HTTP request.

    Returns:
        Any: The processed result from the API request, typically containing
            the created risk assessment data or status information.
    """
    local_env: dict[str, Any] = locals()

    risk_json: dict[str, Any] = API_CLIENT.json_dict_builder({**local_env})

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/policies/create_risk", json=risk_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)


def update_property_location(
    location: dict[str, Any],
    soft_geoservice_bypass: Optional[bool] = None,
    hard_geoservice_bypass: Optional[bool] = None,
    reset_premiums: Optional[bool] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    The data input having the form:
    ::

        {
            'id': UUID,
            'name': str,
            'address_accuracy': str,
            'address_line1': str,
            'address_line2': str,
            'address_city': str,
            'address_state': str,
            'address_zip': str,
            'address_county': UUID,
            'county_specify': UUID,
            'latitude': float,
            'longitude': float,
            'copy_address': bool,
            'flood_zone_code': str,
            'distance_to_coast': str
            'year_built': str,
            'primary': bool,
            'acres': decimal,
            'legal_description': str
        }

    Note:
    Besides the UUID, if any key is empty, we assume you want to clear it.
    If you do not want to clear a field, leave the key out of your request.
    In other words, every key/value pair you send will be checked for discrepancies
    with the current data, and changes will be made.

    :param location: Location information
    :type location: dict[str,Any]
    :param soft_geoservice_bypass: If all location fields are present (lat/long, county, city, zip), then trust these values and do not hit the geo-service processes
    :type soft_geoservice_bypass: Optional[bool]
    :param hard_geoservice_bypass: Regardless of potentially-lacking address fields, do not hit geo-service processes
    :type hard_geoservice_bypass: Optional[bool]
    :param reset_premiums: If True, will reset the premiums for the revision and property
    :type reset_premiums: Optional[bool]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Updated property information
    :rtype: Any
    """

    local_env: dict[str, Any] = locals()

    prop_json: dict[str, dict[str, Any]] = {
        "location": API_CLIENT.json_dict_builder({**local_env})
    }

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/policies/update_property_location", json=prop_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)


def new_mortgagee(property_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Create a new mortgagee for a specified property.

    This function sends a request to create a new mortgagee associated with the given property ID.
    It constructs a JSON payload containing the property ID and makes a POST request to the
    API endpoint for creating new mortgagees. The function handles the response processing
    and returns the result from the API client.

    Parameters:
        property_id (str): The unique identifier of the property for which the mortgagee is being created
        **kwargs (Unpack[RequestParameters]): Additional keyword arguments to be passed to the API client's
            request method, such as headers, authentication tokens, or other request parameters

    Returns:
        Any: The processed result from the API client, typically containing the created mortgagee
            information or confirmation of the operation

    Raises:
        HTTPException: If the API request fails due to network issues, authentication problems,
            or server errors
        ValueError: If the property_id is empty or invalid
    """
    new_mort_json: dict[str, str] = {"property_id": property_id}
    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v2/policies/new_mortgagee", json=new_mort_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def store_mortgagee(
    property_contact_id: str,
    mortgagee_contact_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Store a mortgagee for a property contact.

    This function creates a relationship between a property contact and a mortgagee
    contact by making a request to the API endpoint for storing mortgagee information.

    Parameters
    ----------
    property_contact_id : str
        The unique identifier of the property contact
    mortgagee_contact_id : str
        The unique identifier of the mortgagee contact
    **kwargs : Unpack[RequestParameters]
        Additional keyword arguments to pass to the API request

    Returns
    -------
    Any
        The processed result from the API response

    Notes
    -----
    The function constructs a JSON payload with the property contact ID and mortgagee
    contact ID, then sends a POST request to the '/api/v2/policies/store_mortgagee'
    endpoint. The result is processed and returned as-is from the API client.
    """
    store_mort_json: dict[str, str] = {
        "x_properties_contact_id": property_contact_id,
        "mortgagee_contact_id": mortgagee_contact_id,
    }
    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v2/policies/store_mortgagee", json=store_mort_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def retrieve_policy_snapshot(
    policy_number: str, snapshot_date: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """
    Retrieve a policy snapshot for a given policy number and snapshot date.

    This function fetches the policy snapshot data from the API for the specified
    policy number and snapshot date. It constructs a request with the required
    parameters and processes the response.

    Parameters:
        policy_number (str): The unique identifier for the policy
        snapshot_date (str): The date for which to retrieve the policy snapshot
        **kwargs (Unpack[RequestParameters]): Additional request parameters

    Returns:
        Any: The processed result from the API response

    Raises:
        Any exceptions that may occur during the API request or response processing
    """
    retrieve_json: dict[str, str] = {
        "policy_number": policy_number,
        "snapshot_date": snapshot_date,
    }

    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v2/policies/retrieve_policy_snapshot", json=retrieve_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)
