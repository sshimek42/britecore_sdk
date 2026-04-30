"""BriteCore v2 Policies API endpoint wrappers.

Provides helpers for the full policy lifecycle: retrieval, creation,
endorsements, cancellations, reinstatements, renewals, line items,
and revision management.

Key functions:
    retrieve_policy         -- Fetch a policy by number or ID.
    retrieve_policy_ids     -- Convenience wrapper returning (revision_id, property_id).
    add_line_item           -- Add a coverage line item to a revision.
    cancel_policy           -- Initiate a policy cancellation.
    reinstate_policy        -- Reinstate a previously cancelled policy.
    renew_policy            -- Create a renewal for a policy term.
    get_policies            -- List all policies (paginated).
"""

from logging import Logger
from typing import Any, Literal, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse, Timeout

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
    web_timeout_long,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def retrieve_policy(
    policy_number: str | None = None,
    policy_id: str | None = None,
    revision_state: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy information by policy ID or policy number.

    This wrapper calls ``/api/v2/policies/retrieve_policy`` with identifier
    priority of ``policy_id`` then ``policy_number``. It optionally includes
    ``revision_state`` and returns the normalized ``process_result(...)``
    payload. ``**kwargs`` accepts ``RequestParameters`` overrides and a long
    timeout is applied when not provided.
    """
    LOGGER.debug("Retrieving policy")

    verification_list: list[dict[str, str | None]] = [
        {"policy_number": policy_number},
        {"policy_id": policy_id},
    ]

    priority_list: list[str] = ["policy_id", "policy_number"]

    policy_request_json: dict[str, str | None] = (
        API_CLIENT.multiple_parameter_verification(verification_list, priority_list)
    )

    if revision_state:
        policy_request_json.update({"revision_state": revision_state})

    provided_timeout: Timeout | None = kwargs.get("request_timeout")
    if not provided_timeout:
        kwargs.update({"request_timeout": Timeout(web_timeout_long)})

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_policy",
        json=policy_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_policy"
    )


def add_line_item(
    revision_id: str,
    item_id: str,
    property_id: str | None = "",
    sub_line_id: str | None = "",
    link_id: str | None = "",
    check_for_subline: bool | None = False,
    **kwargs: Unpack[RequestParameters],
) -> bool:
    """Add a line item to a revision or property context.

    This wrapper sends line item fields to ``/api/v2/policies/add_line_item``.
    It returns ``True`` when the normalized ``process_result(...)`` payload
    contains non-empty ``added_items`` and ``False`` otherwise.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    local_env: dict[str, Any] = locals()
    LOGGER.debug("Adding line")
    line_add_json: dict[str, Any] = API_CLIENT.json_dict_builder({**local_env})
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
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
    """Retrieve active revision and primary property identifiers for a policy.

    This helper delegates to ``retrieve_policy``
    (``/api/v2/policies/retrieve_policy``) and extracts
    ``active_revision.id`` and ``active_revision.primary_property_id`` from the
    normalized ``process_result(...)`` payload.

    Raises:
        BritecoreError.MissingParameter: If policy_number is missing.
    """
    # Validate required parameters
    if not policy_number or not policy_number.strip():
        raise BritecoreError.MissingParameter("policy_number is required")

    LOGGER.debug("Getting policy info")
    policy_json: Any = retrieve_policy(policy_number, **kwargs)
    active_revision: Any = policy_json["active_revision"]
    revision_id: Any = active_revision["id"]
    property_id: Any = active_revision["primary_property_id"]

    return revision_id, property_id


def retrieve_policy_list_from_user(
    contact_name: str, check_name: bool = True, **kwargs: Unpack[RequestParameters]
) -> list:
    """Search policies by contact name and return matching policy numbers.

    This helper calls ``/api/v2/policies/search`` with the provided
    ``contact_name`` and returns a de-duplicated list of matching
    ``policyNumber`` values. When ``check_name`` is ``True``, it filters results
    against ``namedInsured`` entries before returning values.
    """
    LOGGER.debug("Searching for '%s'", contact_name)
    user_request_json: dict[str, Any] = {
        "sort_obj": {"field": "policy_number", "order": "asc"},
        "current_page": 1,
        "page_size": 100,
        "search_string": contact_name,
    }
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/search",
        json=user_request_json,
        **kwargs,
    )
    user_json = API_CLIENT.process_result(request_result)["records"]

    policy_list: list[str] = []

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
    """Retrieve named insured contact info for a policy.

    This helper delegates to ``retrieve_policy``
    (``/api/v2/policies/retrieve_policy``) and returns
    ``active_revision.named_insureds`` from the normalized
    ``process_result(...)`` payload.
    """
    LOGGER.debug("Getting contact info")
    contact_json = retrieve_policy(policy_number, **kwargs)

    return contact_json["active_revision"]["named_insureds"]


def create_policy(
    policy_number: str | None = "",
    policy_type_id: str | None = "",
    inception_date: str | None = "",
    term_type: (
        Literal[
            "Custom",
            "3 Years",
            "18 Months",
            "1 Year",
            "9 Months",
            "6 Months",
            "3 Months",
        ]
        | None
    ) = "1 Year",
    expiration_date: str | None = "",  # Required if term_type is "Custom"
    renewal_term_type: (
        Literal["3 Years", "18 Months", "1 Year", "9 Months", "6 Months", "3 Months"]
        | None
    ) = "1 Year",
    is_renewal: bool | None = False,
    as_agent: bool | None = False,
    manual_policy_number: bool | None = True,
    effective_date: str | None = "",
    property_zip: str | None = "",
    underwriting_questions: list | None = None,
    underwriting_options: list | None = None,
    external_system_reference: str | None = "",
    **kwargs: Unpack[RequestParameters],
) -> tuple[Any, str]:
    """Create a policy.

    This wrapper sends policy creation fields to
    ``/api/v2/policies/create_policy`` and returns a tuple of
    ``(policy_data, revision_id)`` from the normalized ``process_result(...)``
    payload. For ``term_type='Custom'``, ``expiration_date`` is required.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    if term_type == "Custom" and not expiration_date:
        BritecoreError.MissingParameter("expiation_date needed with 'Custom' term_type")

    LOGGER.debug("Creating policy '%s'", policy_number)
    local_env: dict[str, Any] = locals()
    policy_request_json: dict[str, Any] = API_CLIENT.json_dict_builder({**local_env})
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/create_policy",
        json=policy_request_json,
        **kwargs,
    )

    policy_json = API_CLIENT.process_result(request_result)

    return policy_json, policy_json["revision_id"]


def retrieve_policy_terms(
    policy_id: str | None = "",
    policy_number: str | None = "",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy terms by policy identifier.

    This wrapper calls ``/api/v2/policies/retrieve_policy_terms`` using either
    ``policy_id`` or ``policy_number`` and returns the normalized
    ``process_result(...)`` payload for terms and revision context.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Retrieving terms")
    if not policy_number and not policy_id:
        BritecoreError.MissingParameter("Either policy_id or policy_number is required")

    parameter_list: list[dict[str, str | None]] = [
        {"policy_id": policy_id},
        {"policy_number": policy_number},
    ]
    parameter_priority: list[str] = ["policy_id", "policy_number"]

    policy_retrieve_json: dict[str, str | None] = (
        API_CLIENT.multiple_parameter_verification(parameter_list, parameter_priority)
    )
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_policy_terms",
        json=policy_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_policy_terms"
    )


def rate_revision(revision_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Rate a revision.

    This wrapper sends ``revision_id`` to ``/api/v2/policies/rate_revision``
    and returns the normalized ``process_result(...)`` payload for the rating
    request. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Re-rating revision '%s'", revision_id)
    policy_retrieve_json = {"revision_id": revision_id}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/rate_revision",
        json=policy_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/rate_revision"
    )


def retrieve_revision_details(
    revision_id: str,
    include_contact_details: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve detailed revision information.

    This wrapper sends ``revision_id`` and ``include_contact_details`` to
    ``/api/v2/policies/retrieve_revision_details`` and returns the normalized
    ``process_result(...)`` payload for revision details. ``**kwargs`` accepts
    ``RequestParameters`` overrides and a long timeout is applied when not
    provided.
    """
    if not kwargs.get("request_timeout"):
        kwargs.update({"request_timeout": Timeout(web_timeout_long)})

    LOGGER.debug("Getting revision")
    revision_retrieve_json = {
        "revision_id": revision_id,
        "include_contact_details": include_contact_details,
    }
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_revision_details",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_revision_details"
    )


def retrieve_risks(
    revision_id: str,
    page: int | None = 0,
    page_size: int | None = 10,
    retrieve_remaining: bool | None = True,
    order_by: str | None = "name",
    risk_types: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve risks for a revision with paging and filter controls.

    This wrapper sends ``revision_id`` plus pagination, ordering, and optional
    ``risk_types`` filters to ``/api/v2/policies/retrieve_risks`` and returns
    the normalized ``process_result(...)`` payload for risk data.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    local_env = locals()
    LOGGER.debug("Getting risks")
    revision_retrieve_json = API_CLIENT.json_dict_builder({**local_env})
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_risks",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_risks"
    )


def retrieve_risk_details(risk_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve detailed risk information by risk identifier.

    This wrapper sends ``risk_id`` to
    ``/api/v2/policies/retrieve_risk_details`` and returns the normalized
    ``process_result(...)`` payload for the matching risk.
    """
    LOGGER.debug("Getting risk details")
    revision_retrieve_json = {"risk_id": risk_id}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_risk_details",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_risk_details"
    )


def update_rating_information(
    property_id: str | None = "",
    revision_id: str | None = "",
    items: list[dict[str, Any]] | None = None,
    reset_premium: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update rating information for a property or revision.

    This wrapper sends rating fields to
    ``/api/v2/policies/update_rating_information`` and returns the normalized
    ``process_result(...)`` payload for the update request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    local_env = locals()
    LOGGER.debug("Updating line item")
    revision_retrieve_json = API_CLIENT.json_dict_builder({**local_env})
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/update_rating_information",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_rating_information"
    )


def rate_risk(risk_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Rate a risk.

    This wrapper sends ``risk_id`` to ``/api/v2/policies/rate_risk`` and
    returns the normalized ``process_result(...)`` payload for the risk rating
    request. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Re-rating policy")
    revision_retrieve_json = {"risk_id": risk_id}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/rate_risk",
        json=revision_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/rate_risk"
    )


def retrieve_billing_schedule_options(
    policy_number: str | None = "",
    policy_term_id: str | None = "",
    ignore_billing_schedule_roles: bool | None = False,
    **kwargs,
) -> dict:
    """Retrieve billing schedule options for a policy context.

    This wrapper sends ``policy_number`` or ``policy_term_id`` and
    ``ignore_billing_schedule_roles`` to
    ``/api/v2/policies/retrieve_billing_schedule_options`` and returns the
    normalized ``process_result(...)`` payload for available schedules.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    if not policy_number and not policy_term_id:
        BritecoreError.MissingParameter(
            "Either policy_number or policy_term_id is needed"
        )

    local_env = locals()

    LOGGER.debug("Getting billing schedule")
    billing_search_json: dict[str, Any] = API_CLIENT.json_dict_builder({**local_env})
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_billing_schedule_options",
        json=billing_search_json,
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_billing_schedule_options"
    )


def new_revision_contact(
    revision_id: str,
    contact_id: str,
    x_id: str | None = None,
    contact_role: (
        Literal[
            "namedInsured", "addtlInterest", "financeCompany", "underwriter", "driver"
        ]
        | None
    ) = "namedInsured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add or update a revision contact assignment.

    This wrapper creates a revision contact through
    ``/api/v2/policies/new_revision_contact`` when ``x_id`` is not provided,
    then links the contact via ``/api/v2/policies/update_revision_contact``.
    It returns the normalized ``process_result(...)`` payload for the final
    request. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    contact_add_result: Any

    request_result: Any = None
    LOGGER.debug("Adding contact")

    contact_add_json: dict[str, str | None] = {
        "revision_id": revision_id,
        "role": contact_role,
    }

    if not x_id:
        request_result = API_CLIENT.do_request(
            path="/api/v2/policies/new_revision_contact",
            json=contact_add_json,
            **kwargs,
        )
        contact_add_result = API_CLIENT.process_result(request_result)
    else:
        contact_add_result = {"x_revisions_contact_id": x_id}

    update_request_result: BaseHTTPResponse | HTTPResponse | None = None
    if contact_add_result:
        x_contact: Any = contact_add_result["x_revisions_contact_id"]
        update_revision_json: dict[str, str] = {
            "x_revisions_contact_id": x_contact,
            "contact_id": contact_id,
        }
        update_request_result = API_CLIENT.do_request(
            path="/api/v2/policies/update_revision_contact",
            json=update_revision_json,
            **kwargs,
        )

    return API_CLIENT.process_result(
        update_request_result, endpoint="/api/v2/policies/update_revision_contact"
    )


def create_risk(
    revision_id: str,
    property_group_number: int | None = None,
    building_number: int | None = None,
    force_categories: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a risk for a revision.

    This wrapper sends ``revision_id`` plus optional property-group,
    building-number, and ``force_categories`` fields to
    ``/api/v2/policies/create_risk`` and returns the normalized
    ``process_result(...)`` payload for the created risk.
    """
    local_env: dict[str, Any] = locals()

    risk_json: dict[str, Any] = API_CLIENT.json_dict_builder({**local_env})

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/create_risk", json=risk_json, **kwargs
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_risk"
    )


def update_property_location(
    location: dict[str, Any],
    soft_geoservice_bypass: bool | None = None,
    hard_geoservice_bypass: bool | None = None,
    reset_premiums: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update property location details.

    This wrapper sends ``location`` and optional geo-service bypass flags to
    ``/api/v2/policies/update_property_location`` and returns the normalized
    ``process_result(...)`` payload for the updated location.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    local_env: dict[str, Any] = locals()

    prop_json: dict[str, dict[str, Any]] = {
        "location": API_CLIENT.json_dict_builder({**local_env})
    }

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/update_property_location", json=prop_json, **kwargs
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_property_location"
    )


def new_mortgagee(property_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Create a mortgagee entry for a property.

    This wrapper sends ``property_id`` to ``/api/v2/policies/new_mortgagee``
    and returns the normalized ``process_result(...)`` payload for the
    mortgagee creation request.
    """
    new_mort_json: dict[str, str] = {"property_id": property_id}
    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v2/policies/new_mortgagee", json=new_mort_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def store_mortgagee(
    property_contact_id: str,
    mortgagee_contact_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Store a mortgagee contact mapping for a property contact.

    This wrapper sends ``property_contact_id`` and ``mortgagee_contact_id`` to
    ``/api/v2/policies/store_mortgagee`` and returns the normalized
    ``process_result(...)`` payload for the mapping request.
    """
    store_mort_json: dict[str, str] = {
        "x_properties_contact_id": property_contact_id,
        "mortgagee_contact_id": mortgagee_contact_id,
    }
    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v2/policies/store_mortgagee", json=store_mort_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def retrieve_policy_snapshot(
    policy_number: str, snapshot_date: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve a policy snapshot for a snapshot date.

    This wrapper sends ``policy_number`` and ``snapshot_date`` to
    ``/api/v2/policies/retrieve_policy_snapshot`` and returns the normalized
    ``process_result(...)`` payload for the snapshot query.
    """
    retrieve_json: dict[str, str] = {
        "policy_number": policy_number,
        "snapshot_date": snapshot_date,
    }

    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v2/policies/retrieve_policy_snapshot", json=retrieve_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def get_policies(
    contact_id: str | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    sorting_order: Literal["asc", "desc"] | None = None,
    page_number: int | None = None,
    page_size: int | None = None,
    include_policy_photo: bool | None = None,
    include_canceled: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List policies with optional filtering and pagination.

    Calls ``/api/v2/policies/get_policies`` and returns the normalized
    ``process_result(...)`` payload containing paginated policy records.

    Parameters:
        contact_id: Filter policies by contact identifier.
        from_date: Filter policies where ``date_added > from_date`` (ISO date
            string, e.g. ``"2024-01-01"``).
        to_date: Filter policies where ``date_added < to_date`` (ISO date
            string).
        sorting_order: Sort direction for results; ``"asc"`` or ``"desc"``.
        page_number: Page number to retrieve, starting from ``1``.
        page_size: Number of records per page; must be ``> 0``.
        include_policy_photo: When ``True``, includes policy photo in each
            record (increases response payload size significantly).
        include_canceled: When ``True``, includes cancelled policies in
            results.
        **kwargs: Additional ``RequestParameters`` overrides (timeout,
            headers, etc.).

    Returns:
        Normalized ``process_result(...)`` payload with pagination metadata
        and a ``policies`` list of policy objects.
    """
    local_env: dict[str, Any] = locals()
    request_json: dict[str, Any] = API_CLIENT.json_dict_builder({**local_env})
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/get_policies",
        json=request_json,
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/get_policies"
    )

