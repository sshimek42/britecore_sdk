from urllib3 import Timeout

from britecore_libraries.api.api_calls import (_LOGGER, api_client,
                                                web_timeout_long)

API_CLIENT = api_client


def retrieve_policy(policy_number: str, **kwargs) -> dict:
    """Get policy information
    :param policy_number: Policy number
    :type policy_number: str
    :return: Request result
    :rtype: dict
    """
    _LOGGER.debug("Retrieving policy")
    policy_request_json = {"policy_number": policy_number}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_policy",
        json=policy_request_json,
        request_timeout=Timeout(web_timeout_long),
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


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
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/add_line_item",
        json=line_add_json,
        **kwargs,
    )
    line_json = API_CLIENT.process_result(request_result)

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
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_policy",
        json=policy_request_json,
        **kwargs,
    )

    policy_json = API_CLIENT.process_result(request_result)

    return policy_json, policy_json["revision_id"]


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
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_policy_terms",
        json=policy_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


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
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/rate_revision",
        json=policy_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


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
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_revision_details",
        json=revision_retrieve_json,
        request_timeout=Timeout(web_timeout_long),
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


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
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_risks",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def retrieve_risk_details(risk_id: str, **kwargs) -> dict:
    """
    Retrieves rick details
    :param risk_id: Risk ID
    :type risk_id: str
    :param kwargs:
    :type kwargs:
    :return: Risk details
    :rtype: dict
    """
    _LOGGER.debug("Getting risk details")
    revision_retrieve_json = {"risk_id": risk_id}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_risk_details",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


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
    _LOGGER.debug("Re-rating policy")
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
    _LOGGER.debug("Getting billing schedule")
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
    _LOGGER.debug("Adding contact")

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
