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

    POST /api/v2/policies/retrieve_policy
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

    POST /api/v2/policies/add_line_item
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
    user_json = search_policies(
        sort_obj={"field": "policy_number", "order": "asc"},
        current_page=1,
        page_size=100,
        search_string=contact_name,
        **kwargs,
    )["records"]

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


def search_policies(
    sort_obj: dict[str, Any] | None = None,
    current_page: int | None = None,
    page_size: int | None = None,
    search_string: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Search policies.

    POST /api/v2/policies/search
    """
    request_json: dict[str, Any] = {
        "sort_obj": sort_obj,
        "current_page": current_page,
        "page_size": page_size,
        "search_string": search_string,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/policies/search",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(request_result, endpoint="/api/v2/policies/search")


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
    client: BritecoreAPIClient | None = None,
    effective_date: str | None = "",
    property_zip: str | None = "",
    underwriting_questions: list | None = None,
    underwriting_options: list | None = None,
    external_system_reference: str | None = "",
    **kwargs: Unpack[RequestParameters],
) -> tuple[Any, str]:
    """Create a policy.

    POST /api/v2/policies/create_policy
    """
    if term_type == "Custom" and not expiration_date:
        raise BritecoreError.MissingParameter(
            "expiration_date needed with 'Custom' term_type"
        )

    LOGGER.debug("Creating policy '%s'", policy_number)
    effective_client: BritecoreAPIClient = client or API_CLIENT
    local_env: dict[str, Any] = locals()
    local_env.pop("client", None)
    local_env.pop("effective_client", None)
    policy_request_json: dict[str, Any] = effective_client.json_dict_builder(
        {**local_env}
    )
    request_result: BaseHTTPResponse | HTTPResponse | None = (
        effective_client.do_request(
            path="/api/v2/policies/create_policy",
            json=policy_request_json,
            **kwargs,
        )
    )

    policy_json = effective_client.process_result(request_result)

    return policy_json, policy_json["revision_id"]


def retrieve_policy_terms(
    policy_id: str | None = "",
    policy_number: str | None = "",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve policy terms by policy identifier.

    POST /api/v2/policies/retrieve_policy_terms
    """
    LOGGER.debug("Retrieving terms")
    if not policy_number and not policy_id:
        raise BritecoreError.MissingParameter(
            "Either policy_id or policy_number is required"
        )

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

    POST /api/v2/policies/rate_revision
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

    POST /api/v2/policies/retrieve_revision_details
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

    POST /api/v2/policies/retrieve_risks
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

    POST /api/v2/policies/retrieve_risk_details
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

    POST /api/v2/policies/update_rating_information
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

    POST /api/v2/policies/rate_risk
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

    POST /api/v2/policies/retrieve_billing_schedule_options
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

    POST /api/v2/policies/new_revision_contact
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
    client: BritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a risk for a revision.

    POST /api/v2/policies/create_risk
    """
    effective_client: BritecoreAPIClient = client or API_CLIENT
    local_env: dict[str, Any] = locals()
    local_env.pop("client", None)
    local_env.pop("effective_client", None)

    risk_json: dict[str, Any] = effective_client.json_dict_builder({**local_env})

    request_result: BaseHTTPResponse | HTTPResponse | None = (
        effective_client.do_request(
            path="/api/v2/policies/create_risk", json=risk_json, **kwargs
        )
    )

    return effective_client.process_result(
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

    POST /api/v2/policies/update_property_location
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

    POST /api/v2/policies/new_mortgagee
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

    POST /api/v2/policies/store_mortgagee
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

    POST /api/v2/policies/retrieve_policy_snapshot
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


# --- Autogenerated spec wrappers ---
# Some wrapper signatures intentionally preserve API field names even when they
# shadow Python built-ins (for compatibility with existing keyword-callers).


def add_external_policies_to_existing_groups(
    external_policies: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add External Policies To Existing Groups.

    POST /api/v2/policies/add_external_policies_to_existing_groups
    """
    request_json: dict[str, Any] = {
        "external_policies": external_policies,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/add_external_policies_to_existing_groups",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/policies/add_external_policies_to_existing_groups",
    )


def add_policies_to_existing_groups(
    field: str | None = None,
    Returns: str | None = None,
    messages: list[str] | None = None,
    success: bool | None = None,
    policies: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add Policies To Existing Groups.

    POST /api/v2/policies/add_policies_to_existing_groups
    """
    request_json: dict[str, Any] = {
        "-------": field,
        "Returns": Returns,
        "messages": messages,
        "success": success,
        "policies": policies,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/add_policies_to_existing_groups",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/add_policies_to_existing_groups"
    )


def add_policies_to_new_group(
    policies: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add Policies To New Group.

    POST /api/v2/policies/add_policies_to_new_group
    """
    request_json: dict[str, Any] = {
        "policies": policies,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/add_policies_to_new_group",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/add_policies_to_new_group"
    )


def add_sub_line(
    revision_id: str | None = None,
    sub_line_id: str | None = None,
    property_id: str | None = None,
    link_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add Sub Line.

    POST /api/v2/policies/add_sub_line
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "sub_line_id": sub_line_id,
        "property_id": property_id,
        "link_id": link_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/add_sub_line",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/add_sub_line"
    )


def application_signature_event_callback(
    event_type: str | None = None,
    file_id: str | None = None,
    signer_name: str | None = None,
    signature_url: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Application Signature Event Callback.

    POST /api/v2/policies/application_signature_event_callback
    """
    request_json: dict[str, Any] = {
        "event_type": event_type,
        "file_id": file_id,
        "signer_name": signer_name,
        "signature_url": signature_url,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/application_signature_event_callback",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/application_signature_event_callback"
    )


def apply_pnc_lockbox_payment_transactions(
    transactions: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Apply Pnc Lockbox Payment Transactions.

    POST /api/v2/policies/apply_pnc_lockbox_payment_transactions
    """
    request_json: dict[str, Any] = {
        "transactions": transactions,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/apply_pnc_lockbox_payment_transactions",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/policies/apply_pnc_lockbox_payment_transactions",
    )


def async_create_policy_from_britequote(
    quote: Any | None = None,
    postback: Any | None = None,
    inception_date: Any | None = None,
    transaction_type: Any | None = None,
    user: Any | None = None,
    term_type: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Async Create Policy From Britequote.

    POST /api/v2/policies/async_create_policy_from_britequote
    """
    request_json: dict[str, Any] = {
        "quote": quote,
        "postback": postback,
        "inception_date": inception_date,
        "transaction_type": transaction_type,
        "user": user,
        "term_type": term_type,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/async_create_policy_from_britequote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/async_create_policy_from_britequote"
    )


def async_create_revision_from_britequote(
    quote: Any | None = None,
    postback: Any | None = None,
    transaction_type: Any | None = None,
    revision_date: Any | None = None,
    user: Any | None = None,
    policy_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Async Create Revision From Britequote.

    POST /api/v2/policies/async_create_revision_from_britequote
    """
    request_json: dict[str, Any] = {
        "quote": quote,
        "postback": postback,
        "transaction_type": transaction_type,
        "revision_date": revision_date,
        "user": user,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/async_create_revision_from_britequote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/policies/async_create_revision_from_britequote",
    )


def async_request_loss_analysis(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Async Request Loss Analysis.

    POST /api/v2/policies/async_request_loss_analysis
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/async_request_loss_analysis",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/async_request_loss_analysis"
    )


def bind(
    bind_info: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Bind a policy to convert it from a quote to an active policy.

    Initiates the binding process, which finalizes underwriting and activates coverage.
    Requires complete bind information including policy holder, coverage selections,
    and endorsement details.

    Args:
        bind_info: The complete binding information dictionary (required).
            Typically includes policy_id, premium amount, effective_date, and coverage details.
        **kwargs: Additional request parameters (timeout, retry, headers, etc.).

    Returns:
        API response containing the bound policy details and confirmation.

    Raises:
        BritecoreError.MissingParameter: If ``bind_info`` is not provided or invalid.

    Example:
        >>> bind_info = {"policy_id": "...", "premium": 1500, ...}
        >>> bind(bind_info=bind_info)

    POST /api/v2/policies/bind
    """
    if not bind_info or not isinstance(bind_info, dict):
        raise BritecoreError.MissingParameter(
            "bind_info is required and must be a dict"
        )

    request_json: dict[str, Any] = {"bind_info": bind_info}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/bind",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(request_result, endpoint="/api/v2/policies/bind")


def cancel_policy(
    cancel_reason: str | None = None,
    cancel_pending_date: str | None = None,
    policy_term_id: str | None = None,
    cancel_date: str | None = None,
    cancel_reason_id: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Cancel an active policy.

    Initiates policy cancellation with specified reason and effective date.
    Either ``policy_id`` or ``policy_term_id`` must be provided.

    Args:
        policy_id: The policy ID to cancel (takes priority if both IDs provided).
        policy_term_id: The policy term ID to cancel.
        cancel_date: The cancellation effective date (ISO date format, e.g., "2024-08-01").
        cancel_reason: Human-readable cancellation reason (e.g., "Customer Request").
        cancel_reason_id: The cancellation reason code/ID from the system.
        cancel_pending_date: Optional date for pending cancellations.
        **kwargs: Additional request parameters (timeout, retry, headers, etc.).

    Returns:
        API response containing cancellation confirmation and details.

    Raises:
        BritecoreError.MissingParameter: If neither ``policy_id`` nor ``policy_term_id`` is provided.

    Example:
        >>> cancel_policy(policy_id="POL-123", cancel_date="2024-08-15", cancel_reason="Customer Request")

    POST /api/v2/policies/cancel_policy
    """
    verification_list = [
        {"policy_id": policy_id},
        {"policy_term_id": policy_term_id},
    ]
    priority_list = ["policy_id", "policy_term_id"]
    request_json = API_CLIENT.multiple_parameter_verification(
        verification_list, priority_list
    )

    if cancel_reason is not None:
        request_json["cancel_reason"] = cancel_reason
    if cancel_reason_id is not None:
        request_json["cancel_reason_id"] = cancel_reason_id
    if cancel_date is not None:
        request_json["cancel_date"] = cancel_date
    if cancel_pending_date is not None:
        request_json["cancel_pending_date"] = cancel_pending_date

    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/cancel_policy",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/cancel_policy"
    )


def cancel_policy_v2(
    policy_term_external_system_reference: str | None = None,
    cancellation_reason_id: str | None = None,
    additional_description: str | None = None,
    policy_term_id: str | None = None,
    cancellation_date: str | None = None,
    cancellation_pending_date: str | None = None,
    print_description: str | None = None,
    cancellation_reason: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Cancel Policy V2.

    POST /api/v2/policies/cancel_policy_v2
    """
    request_json: dict[str, Any] = {
        "policy_term_external_system_reference": policy_term_external_system_reference,
        "cancellation_reason_id": cancellation_reason_id,
        "additional_description": additional_description,
        "policy_term_id": policy_term_id,
        "cancellation_date": cancellation_date,
        "cancellation_pending_date": cancellation_pending_date,
        "print_description": print_description,
        "cancellation_reason": cancellation_reason,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/cancel_policy_v2",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/cancel_policy_v2"
    )


def copy_risk(
    copy_address: str | None = None,
    copy_rating: str | None = None,
    copy_tenants: str | None = None,
    copy_mortgagees: str | None = None,
    from_risk_id: str | None = None,
    to_risk_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Copy Risk.

    POST /api/v2/policies/copy_risk
    """
    request_json: dict[str, Any] = {
        "copy_address": copy_address,
        "copy_rating": copy_rating,
        "copy_tenants": copy_tenants,
        "copy_mortgagees": copy_mortgagees,
        "from_risk_id": from_risk_id,
        "to_risk_id": to_risk_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/copy_risk",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/copy_risk"
    )


def copy_sub_line(
    sub_line_instance_id: str | None = None,
    revision_id: str | None = None,
    sub_line_id: str | None = None,
    property_id: str | None = None,
    link_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Copy Sub Line.

    POST /api/v2/policies/copy_sub_line
    """
    request_json: dict[str, Any] = {
        "sub_line_instance_id": sub_line_instance_id,
        "revision_id": revision_id,
        "sub_line_id": sub_line_id,
        "property_id": property_id,
        "link_id": link_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/copy_sub_line",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/copy_sub_line"
    )


def create_from_stateless_quote(
    stateless_quote_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create From Stateless Quote.

    POST /api/v2/policies/create_from_stateless_quote
    """
    request_json: dict[str, Any] = {"stateless_quote_id": stateless_quote_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_from_stateless_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_from_stateless_quote"
    )


def create_loss_dispute(
    reason: str | None = None,
    property_id: str | None = None,
    case_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create Loss Dispute.

    POST /api/v2/policies/create_loss_dispute
    """
    request_json: dict[str, Any] = {
        "reason": reason,
        "property_id": property_id,
        "case_number": case_number,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_loss_dispute",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_loss_dispute"
    )


def create_new_policy(
    quote_info: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create New Policy.

    POST /api/v2/policies/create_new_policy
    """
    request_json: dict[str, Any] = {"quote_info": quote_info}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_new_policy",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_new_policy"
    )


def create_new_policy_extended(
    quote_info: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create New Policy Extended.

    POST /api/v2/policies/create_new_policy_extended
    """
    request_json: dict[str, Any] = {"quote_info": quote_info}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_new_policy_extended",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_new_policy_extended"
    )


def create_policy_from_britequote(
    quote: dict[str, Any] | None = None,
    postback: str | None = None,
    term_type: str | None = None,
    inception_date: str | None = None,
    transaction_type: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a policy directly from a BriteCore quote.

    Converts a quote into an active policy in a single operation. This is a convenience
    wrapper that bypasses manual binding steps for automated workflows.

    Args:
        quote: The complete quote dictionary (required).
        inception_date: The policy effective date (ISO date format).
        term_type: The term length (e.g., "1 Year", "3 Years").
        transaction_type: The type of transaction (e.g., "New Business", "Renewal").
        postback: Optional postback URL for async notifications.
        **kwargs: Additional request parameters (timeout, retry, headers, etc.).

    Returns:
        API response containing the created policy details.

    Raises:
        BritecoreError.MissingParameter: If ``quote`` is not provided or invalid.

    Example:
        >>> quote_data = {"insured": {...}, "coverage": {...}, ...}
        >>> create_policy_from_britequote(quote=quote_data, inception_date="2024-09-01")

    POST /api/v2/policies/create_policy_from_britequote
    """
    if not quote or not isinstance(quote, dict):
        raise BritecoreError.MissingParameter("quote is required and must be a dict")

    request_json: dict[str, Any] = {"quote": quote}
    if inception_date is not None:
        request_json["inception_date"] = inception_date
    if term_type is not None:
        request_json["term_type"] = term_type
    if transaction_type is not None:
        request_json["transaction_type"] = transaction_type
    if postback is not None:
        request_json["postback"] = postback

    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_policy_from_britequote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_policy_from_britequote"
    )


def create_quote(
    quote_info: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create Quote.

    POST /api/v2/policies/create_quote
    """
    request_json: dict[str, Any] = {
        "quote_info": quote_info,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_quote"
    )


def create_quote_async(
    success: bool | None = None,
    field: str | None = None,
    Returns: str | None = None,
    quote_info: dict[str, Any] | None = None,
    message: list[str] | None = None,
    data: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create Quote Async.

    POST /api/v2/policies/create_quote_async
    """
    request_json: dict[str, Any] = {
        "success": success,
        "-------": field,
        "Returns": Returns,
        "quote_info": quote_info,
        "message": message,
        "data": data,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_quote_async",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_quote_async"
    )


def create_quote_extended(
    quote_info: dict[str, Any] | None = None,
    requote: bool | None = None,
    run_uw_rules: bool | None = None,
    run_stateless: bool | str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create Quote Extended.

    POST /api/v2/policies/create_quote_extended
    """
    request_json: dict[str, Any] = {
        "quote_info": quote_info,
        "requote": requote,
        "run_uw_rules": run_uw_rules,
        "run_stateless": run_stateless,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_quote_extended",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_quote_extended"
    )


def create_quote_extended_async(
    success: bool | None = None,
    field: str | None = None,
    Returns: str | None = None,
    run_uw_rules: bool | None = None,
    quote_info: dict[str, Any] | None = None,
    message: list[str] | None = None,
    data: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create Quote Extended Async.

    POST /api/v2/policies/create_quote_extended_async
    """
    request_json: dict[str, Any] = {
        "success": success,
        "-------": field,
        "Returns": Returns,
        "run_uw_rules": run_uw_rules,
        "quote_info": quote_info,
        "message": message,
        "data": data,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_quote_extended_async",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_quote_extended_async"
    )


def create_revision_from_britequote(
    transaction_type: str | None = None,
    quote: str | None = None,
    revision_date: str | None = None,
    postback: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create Revision From Britequote.

    POST /api/v2/policies/create_revision_from_britequote
    """
    request_json: dict[str, Any] = {
        "transaction_type": transaction_type,
        "quote": quote,
        "revision_date": revision_date,
        "postback": postback,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/create_revision_from_britequote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/create_revision_from_britequote"
    )


def delete_external_policies(
    policies: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete External Policies.

    POST /api/v2/policies/delete_external_policies
    """
    request_json: dict[str, Any] = {
        "policies": policies,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/delete_external_policies",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/delete_external_policies"
    )


def delete_loss_dispute(
    dispute_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete Loss Dispute.

    POST /api/v2/policies/delete_loss_dispute
    """
    request_json: dict[str, Any] = {
        "dispute_id": dispute_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/delete_loss_dispute",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/delete_loss_dispute"
    )


def evaluate_cancellation(
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Evaluate cancellation eligibility and penalties for a policy.

    Checks whether a policy can be cancelled and calculates any penalties,
    prorations, or other financial impacts of cancellation.

    Args:
        policy_id: The policy ID to evaluate (required).
        **kwargs: Additional request parameters (timeout, retry, headers, etc.).

    Returns:
        API response containing cancellation eligibility, penalties, and prorations.

    Raises:
        BritecoreError.MissingParameter: If ``policy_id`` is not provided.

    Example:
        >>> evaluate_cancellation(policy_id="POL-123")

    POST /api/v2/policies/evaluate_cancellation
    """
    if not policy_id or not policy_id.strip():
        raise BritecoreError.MissingParameter("policy_id is required")

    request_json: dict[str, Any] = {"policy_id": policy_id}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/evaluate_cancellation",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/evaluate_cancellation"
    )


def export_auto_policies(
    property_ids: list[str] | None = None,
    revision_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Export Auto Policies.

    POST /api/v2/policies/export_auto_policies
    """
    request_json: dict[str, Any] = {
        "property_ids": property_ids,
        "revision_ids": revision_ids,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/export_auto_policies",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/export_auto_policies"
    )


def export_policies(
    property_ids: list[str] | None = None,
    revision_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Export Policies.

    POST /api/v2/policies/export_policies
    """
    request_json: dict[str, Any] = {
        "property_ids": property_ids,
        "revision_ids": revision_ids,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/export_policies",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/export_policies"
    )


def get_loss_disputes(
    property_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Loss Disputes.

    POST /api/v2/policies/get_loss_disputes
    """
    request_json: dict[str, Any] = {
        "property_id": property_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/get_loss_disputes",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/get_loss_disputes"
    )


def get_policy_groups(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Policy Groups.

    POST /api/v2/policies/get_policy_groups
    """
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/get_policy_groups",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/get_policy_groups"
    )


def get_revision_data_for_stp(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Revision Data For Stp.

    POST /api/v2/policies/get_revision_data_for_stp
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/get_revision_data_for_stp",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/get_revision_data_for_stp"
    )


def get_underlying_policy_changes(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Underlying Policy Changes.

    POST /api/v2/policies/get_underlying_policy_changes
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/get_underlying_policy_changes",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/get_underlying_policy_changes"
    )


def get_underwriting_review_workflow(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Underwriting Review Workflow.

    POST /api/v2/policies/get_underwriting_review_workflow
    """
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/get_underwriting_review_workflow",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/get_underwriting_review_workflow"
    )


def import_iso_protection_classes(
    county_fips: Any | None = None,
    retrieval_date: Any | None = None,
    distance_to_coast_range_name: Any | None = None,
    protection_class: Any | None = None,
    distance_to_coast_range_code: Any | None = None,
    bcegs_year: Any | None = None,
    distance_to_coast_county_name: Any | None = None,
    bcegs_positive_hit: Any | None = None,
    bcegs_code: Any | None = None,
    county_name: Any | None = None,
    effective_date: Any | None = None,
    distance_to_coast_fips: Any | None = None,
    fire_district: Any | None = None,
    property_id: Any | None = None,
    distance_to_coast_ocean_gulf_name: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Import Iso Protection Classes.

    POST /api/v2/policies/import_iso_protection_classes
    """
    request_json: dict[str, Any] = {
        "county_fips": county_fips,
        "retrieval_date": retrieval_date,
        "distance_to_coast_range_name": distance_to_coast_range_name,
        "protection_class": protection_class,
        "distance_to_coast_range_code": distance_to_coast_range_code,
        "bcegs_year": bcegs_year,
        "distance_to_coast_county_name": distance_to_coast_county_name,
        "bcegs_positive_hit": bcegs_positive_hit,
        "bcegs_code": bcegs_code,
        "county_name": county_name,
        "effective_date": effective_date,
        "distance_to_coast_fips": distance_to_coast_fips,
        "fire_district": fire_district,
        "property_id": property_id,
        "distance_to_coast_ocean_gulf_name": distance_to_coast_ocean_gulf_name,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/import_iso_protection_classes",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/import_iso_protection_classes"
    )


def import_munichre_eligibility(
    retrieval_date: Any | None = None,
    is_eligible: Any | None = None,
    score: Any | None = None,
    property_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Import Munichre Eligibility.

    POST /api/v2/policies/import_munichre_eligibility
    """
    request_json: dict[str, Any] = {
        "retrieval_date": retrieval_date,
        "is_eligible": is_eligible,
        "score": score,
        "property_id": property_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/import_munichre_eligibility",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/import_munichre_eligibility"
    )


def initialize_application_questions(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Initialize Application Questions.

    POST /api/v2/policies/initialize_application_questions
    """
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/initialize_application_questions",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/initialize_application_questions"
    )


def initiate_property_valuation(
    integration_instance_id: str | None = None,
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Initiate Property Valuation.

    POST /api/v2/policies/initiate_property_valuation
    """
    request_json: dict[str, Any] = {
        "integration_instance_id": integration_instance_id,
        "property_id": property_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/initiate_property_valuation",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/initiate_property_valuation"
    )


def issue(
    issue_info: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Issue.

    POST /api/v2/policies/issue
    """
    request_json: dict[str, Any] = {
        "issue_info": issue_info,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/issue",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(request_result, endpoint="/api/v2/policies/issue")


def ivr_lookup(
    digits: str | None = None,
    property_address_zip: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Ivr Lookup.

    POST /api/v2/policies/ivr_lookup
    """
    request_json: dict[str, Any] = {
        "digits": digits,
        "property_address_zip": property_address_zip,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/ivr_lookup",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/ivr_lookup"
    )


def link_underlying_policy(
    revision_id: str | None = None,
    underlying_policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Link Underlying Policy.

    POST /api/v2/policies/link_underlying_policy
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "underlying_policy_id": underlying_policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/link_underlying_policy",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/link_underlying_policy"
    )


def new_policy_information(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """New Policy Information.

    POST /api/v2/policies/new_policy_information
    """
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/new_policy_information",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/new_policy_information"
    )


def new_revision(
    policy_id: str | None = None,
    renewal_status: str | None = None,
    revision_date: str | None = None,
    override_effective_date_checks: bool | None = None,
    check_for_policy_changes: str | None = None,
    force_persistent_builder: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """New Revision.

    POST /api/v2/policies/new_revision
    """
    request_json: dict[str, Any] = {
        "policy_id": policy_id,
        "renewal_status": renewal_status,
        "revision_date": revision_date,
        "override_effective_date_checks": override_effective_date_checks,
        "check_for_policy_changes": check_for_policy_changes,
        "force_persistent_builder": force_persistent_builder,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/new_revision",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/new_revision"
    )


def post_external_policies(
    policies: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Post External Policies.

    POST /api/v2/policies/post_external_policies
    """
    request_json: dict[str, Any] = {
        "policies": policies,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/post_external_policies",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/post_external_policies"
    )


def rate_quote_revision(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Rate Quote Revision.

    POST /api/v2/policies/rate_quote_revision
    """
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/rate_quote_revision",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/rate_quote_revision"
    )


def remove_line_item(
    item_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove Line Item.

    POST /api/v2/policies/remove_line_item
    """
    request_json: dict[str, Any] = {
        "item_id": item_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/remove_line_item",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/remove_line_item"
    )


def requote_extended(
    quote_info: str | None = None,
    run_uw_rules: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Requote Extended.

    POST /api/v2/policies/requote_extended
    """
    request_json: dict[str, Any] = {
        "quote_info": quote_info,
        "run_uw_rules": run_uw_rules,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/requote_extended",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/requote_extended"
    )


def reset_revision_premium(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Reset Revision Premium.

    POST /api/v2/policies/reset_revision_premium
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/reset_revision_premium",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/reset_revision_premium"
    )


def reset_risk_premium(
    risk_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Reset Risk Premium.

    POST /api/v2/policies/reset_risk_premium
    """
    request_json: dict[str, Any] = {
        "risk_id": risk_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/reset_risk_premium",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/reset_risk_premium"
    )


def retrieve_account_history(
    current_page: int | None = None,
    policy_term_id: str | None = None,
    page_size: int | None = None,
    filter_dict: dict[str, Any] | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Account History.

    POST /api/v2/policies/retrieve_account_history
    """
    request_json: dict[str, Any] = {
        "current_page": current_page,
        "policy_term_id": policy_term_id,
        "page_size": page_size,
        "filter_dict": filter_dict,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_account_history",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_account_history"
    )


def retrieve_cancellation_info(
    revision_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Cancellation Info.

    POST /api/v2/policies/retrieve_cancellation_info
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_cancellation_info",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_cancellation_info"
    )


def retrieve_current_and_future_policies_terms_with_recurring_payment_method_id(
    payment_method_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Current And Future Policies Terms With Recurring Payment Method Id.

    POST /api/v2/policies/retrieve_current_and_future_policies_terms_with_recurring_payment_method_id
    """
    request_json: dict[str, Any] = {
        "payment_method_id": payment_method_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_current_and_future_policies_terms_with_recurring_payment_method_id",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/policies/retrieve_current_and_future_policies_terms_with_recurring_payment_method_id",
    )


def retrieve_files_pending_signature(
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Files Pending Signature.

    POST /api/v2/policies/retrieve_files_pending_signature
    """
    request_json: dict[str, Any] = {
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_files_pending_signature",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_files_pending_signature"
    )


def retrieve_ivans_billing_data(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Ivans Billing Data.

    POST /api/v2/policies/retrieve_ivans_billing_data
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_ivans_billing_data",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_ivans_billing_data"
    )


def retrieve_pnc_lockbox_matchfile_info(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Pnc Lockbox Matchfile Info.

    POST /api/v2/policies/retrieve_pnc_lockbox_matchfile_info
    """
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_pnc_lockbox_matchfile_info",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_pnc_lockbox_matchfile_info"
    )


def retrieve_policy_change_logs(
    transactions: list[str] | None = None,
    revision_ids: list[str] | None = None,
    filter_by: str | None = None,
    allow_timestamp: bool | None = None,
    from_date: str | None = None,
    to_date: str | None = None,
    policy_type_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Policy Change Logs.

    POST /api/v2/policies/retrieve_policy_change_logs
    """
    request_json: dict[str, Any] = {
        "transactions": transactions,
        "revision_ids": revision_ids,
        "filter_by": filter_by,
        "allow_timestamp": allow_timestamp,
        "from_date": from_date,
        "to_date": to_date,
        "policy_type_ids": policy_type_ids,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_policy_change_logs",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_policy_change_logs"
    )


def retrieve_potential_policies_payors(
    policy_numbers: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Potential Policies Payors.

    POST /api/v2/policies/retrieve_potential_policies_payors
    """
    request_json: dict[str, Any] = {
        "policy_numbers": policy_numbers,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_potential_policies_payors",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_potential_policies_payors"
    )


def retrieve_properties_by_coverage_name(
    revision_id: str | None = None,
    name: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Properties By Coverage Name.

    POST /api/v2/policies/retrieve_properties_by_coverage_name
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "name": name,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_properties_by_coverage_name",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_properties_by_coverage_name"
    )


def retrieve_properties_by_group(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Properties By Group.

    POST /api/v2/policies/retrieve_properties_by_group
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_properties_by_group",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_properties_by_group"
    )


def retrieve_rates_for_quote(
    revision_id: str | None = None,
    rating_specs: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Rates For Quote.

    POST /api/v2/policies/retrieve_rates_for_quote
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "rating_specs": rating_specs,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_rates_for_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_rates_for_quote"
    )


def retrieve_revision_analysis(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Revision Analysis.

    POST /api/v2/policies/retrieve_revision_analysis
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_revision_analysis",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_revision_analysis"
    )


def retrieve_revision_invoice_numbers(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Revision Invoice Numbers.

    POST /api/v2/policies/retrieve_revision_invoice_numbers
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_revision_invoice_numbers",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_revision_invoice_numbers"
    )


def retrieve_revision_property_group_numbers(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Revision Property Group Numbers.

    POST /api/v2/policies/retrieve_revision_property_group_numbers
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_revision_property_group_numbers",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/policies/retrieve_revision_property_group_numbers",
    )


def retrieve_revision_status(
    revision_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Revision Status.

    POST /api/v2/policies/retrieve_revision_status
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_revision_status",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_revision_status"
    )


def retrieve_underlying_policy(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Underlying Policy.

    POST /api/v2/policies/retrieve_underlying_policy
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/retrieve_underlying_policy",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/retrieve_underlying_policy"
    )


def rewrite_policy(
    term: str | None = None,
    policy_number: str | None = None,
    rewritten_revision_external_system_reference: str | None = None,
    expiration_date: str | None = None,
    reason_id: str | None = None,
    policy_number_option: str | None = None,
    effective_date: str | None = None,
    reason: str | None = None,
    revision_external_system_reference: str | None = None,
    rewritten_policy_number: str | None = None,
    revision_id: str | None = None,
    at_renewal_set_policy_term_to: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Rewrite Policy.

    POST /api/v2/policies/rewrite_policy
    """
    request_json: dict[str, Any] = {
        "term": term,
        "policy_number": policy_number,
        "rewritten_revision_external_system_reference": rewritten_revision_external_system_reference,
        "expiration_date": expiration_date,
        "reason_id": reason_id,
        "policy_number_option": policy_number_option,
        "effective_date": effective_date,
        "reason": reason,
        "revision_external_system_reference": revision_external_system_reference,
        "rewritten_policy_number": rewritten_policy_number,
        "revision_id": revision_id,
        "at_renewal_set_policy_term_to": at_renewal_set_policy_term_to,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/rewrite_policy",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/rewrite_policy"
    )


def run_property_lookup(
    dependencies: list[str] | None = None,
    integration_instance_id: str | None = None,
    property_id: str | None = None,
    headless: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Run Property Lookup.

    POST /api/v2/policies/run_property_lookup
    """
    request_json: dict[str, Any] = {
        "dependencies": dependencies,
        "integration_instance_id": integration_instance_id,
        "property_id": property_id,
        "headless": headless,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/run_property_lookup",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/run_property_lookup"
    )


def run_underwriting_rules(
    success: bool | None = None,
    field: str | None = None,
    Returns: str | None = None,
    exclude_modules: str | None = None,
    revision_id: str | None = None,
    use_new_rules_engine: str | None = None,
    message: str | None = None,
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Run Underwriting Rules.

    POST /api/v2/policies/run_underwriting_rules
    """
    request_json: dict[str, Any] = {
        "success": success,
        "-------": field,
        "Returns": Returns,
        "exclude_modules": exclude_modules,
        "revision_id": revision_id,
        "use_new_rules_engine": use_new_rules_engine,
        "message": message,
        "property_id": property_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/run_underwriting_rules",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/run_underwriting_rules"
    )


def set_binder_to_active(
    revision_id: str | None = None,
    external_system_reference: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set Binder To Active.

    POST /api/v2/policies/set_binder_to_active
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "external_system_reference": external_system_reference,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/set_binder_to_active",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/set_binder_to_active"
    )


def set_exclude_from_combined_billing(
    exclude: Any | None = None,
    policy_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set Exclude From Combined Billing.

    POST /api/v2/policies/set_exclude_from_combined_billing
    """
    request_json: dict[str, Any] = {
        "exclude": exclude,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/set_exclude_from_combined_billing",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/set_exclude_from_combined_billing"
    )


def store_policy_information(
    quote_info: Any | None = None,
    policy_data: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Store Policy Information.

    POST /api/v2/policies/store_policy_information
    """
    request_json: dict[str, Any] = {
        "quote_info": quote_info,
        "policy_data": policy_data,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/store_policy_information",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/store_policy_information"
    )


def store_policy_information_extended(
    quote_info: dict[str, Any] | None = None,
    run_uw_rules: bool | None = None,
    policy_data: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Store Policy Information Extended.

    POST /api/v2/policies/store_policy_information_extended
    """
    request_json: dict[str, Any] = {
        "quote_info": quote_info,
        "run_uw_rules": run_uw_rules,
        "policy_data": policy_data,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/store_policy_information_extended",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/store_policy_information_extended"
    )


def store_renewal_status(
    renewal_status_reason: Any | None = None,
    revision_id: Any | None = None,
    renewal_status: Any | None = None,
    renewal_status_description: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Store Renewal Status.

    POST /api/v2/policies/store_renewal_status
    """
    request_json: dict[str, Any] = {
        "renewal_status_reason": renewal_status_reason,
        "revision_id": revision_id,
        "renewal_status": renewal_status,
        "renewal_status_description": renewal_status_description,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/store_renewal_status",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/store_renewal_status"
    )


def store_revision_description(  # pylint: disable=redefined-builtin
    revision_id: str | None = None,
    type: str | None = None,
    description: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Store Revision Description.

    POST /api/v2/policies/store_revision_description
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "type": type,
        "description": description,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/store_revision_description",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/store_revision_description"
    )


def submit_quote(
    date_cursor: Any | None = None,
    json_dict: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Submit a quote for processing in the policy workflow.

    Sends a quote to the next stage in the underwriting or binding process.
    This is typically used after quote modifications or rate updates.

    Args:
        json_dict: The quote data dictionary to submit (required).
        date_cursor: Optional cursor for pagination or batch processing.
        **kwargs: Additional request parameters (timeout, retry, headers, etc.).

    Returns:
        API response containing confirmation of submission and next steps.

    Example:
        >>> quote_data = {"quote_id": "...", "status": "ready", ...}
        >>> submit_quote(json_dict=quote_data)

    POST /api/v2/policies/submit_quote
    """
    request_json: dict[str, Any] = {}
    if json_dict is not None:
        request_json["json_dict"] = json_dict
    if date_cursor is not None:
        request_json["date_cursor"] = date_cursor

    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/submit_quote",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/submit_quote"
    )


def sync_item_within_a_property_group(
    property_group_id: str | None = None,
    item_id: str | None = None,
    builder_obj: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Sync Item Within A Property Group.

    POST /api/v2/policies/sync_item_within_a_property_group
    """
    request_json: dict[str, Any] = {
        "property_group_id": property_group_id,
        "item_id": item_id,
        "builder_obj": builder_obj,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/sync_item_within_a_property_group",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/sync_item_within_a_property_group"
    )


def sync_underlying_policy_changes(
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Sync Underlying Policy Changes.

    POST /api/v2/policies/sync_underlying_policy_changes
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/sync_underlying_policy_changes",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/sync_underlying_policy_changes"
    )


def update_billing_schedule(
    billing_schedule: str | None = None,
    policy_term_id: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Billing Schedule.

    POST /api/v2/policies/update_billing_schedule
    """
    request_json: dict[str, Any] = {
        "billing_schedule": billing_schedule,
        "policy_term_id": policy_term_id,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_billing_schedule",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_billing_schedule"
    )


def update_builder_ready_to_rate(
    property_revision: dict[str, Any] | None = None,
    property_id: str | None = None,
    revision_id: str | None = None,
    is_completed: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Builder Ready To Rate.

    POST /api/v2/policies/update_builder_ready_to_rate
    """
    request_json: dict[str, Any] = {
        "property/revision": property_revision,
        "'property_id'": property_id,
        "'revision_id'": revision_id,
        "'is_completed'": is_completed,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_builder_ready_to_rate",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_builder_ready_to_rate"
    )


def update_contact_interest(
    x_revisions_contact_id: str | None = None,
    revision_id: str | None = None,
    interest: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Contact Interest.

    POST /api/v2/policies/update_contact_interest
    """
    request_json: dict[str, Any] = {
        "x_revisions_contact_id": x_revisions_contact_id,
        "revision_id": revision_id,
        "interest": interest,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_contact_interest",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_contact_interest"
    )


def update_effective_and_expiration_date(
    effective_date: str | None = None,
    expiration_date: str | None = None,
    policy_term_type: str | None = None,
    policy_type_id: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Effective And Expiration Date.

    POST /api/v2/policies/update_effective_and_expiration_date
    """
    request_json: dict[str, Any] = {
        "effective_date": effective_date,
        "expiration_date": expiration_date,
        "policy_term_type": policy_term_type,
        "policy_type_id": policy_type_id,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_effective_and_expiration_date",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_effective_and_expiration_date"
    )


def update_inactive_policy_groups(
    force_removal: str | None = None,
    group_ids: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Inactive Policy Groups.

    POST /api/v2/policies/update_inactive_policy_groups
    """
    request_json: dict[str, Any] = {
        "force_removal": force_removal,
        "group_ids": group_ids,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_inactive_policy_groups",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_inactive_policy_groups"
    )


def update_loss_dispute(
    dispute_id: Any | None = None,
    reason: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Loss Dispute.

    POST /api/v2/policies/update_loss_dispute
    """
    request_json: dict[str, Any] = {
        "dispute_id": dispute_id,
        "reason": reason,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_loss_dispute",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_loss_dispute"
    )


def update_mortgagee_information(
    x_contact_reference: str | None = None,
    mortgagee_info: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Mortgagee Information.

    POST /api/v2/policies/update_mortgagee_information
    """
    request_json: dict[str, Any] = {
        "x_contact_reference": x_contact_reference,
        "mortgagee_info": mortgagee_info,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_mortgagee_information",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_mortgagee_information"
    )


def update_policies_terms_payment_method_batch(
    policy_term_ids: Any | None = None,
    payment_method_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Policies Terms Payment Method Batch.

    POST /api/v2/policies/update_policies_terms_payment_method_batch
    """
    request_json: dict[str, Any] = {
        "policy_term_ids": policy_term_ids,
        "payment_method_id": payment_method_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_policies_terms_payment_method_batch",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/policies/update_policies_terms_payment_method_batch",
    )


def update_policy_contact(
    contact_role: str | None = None,
    contact_id: str | None = None,
    x_policy_contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Policy Contact.

    POST /api/v2/policies/update_policy_contact
    """
    request_json: dict[str, Any] = {
        "contact_role": contact_role,
        "contact_id": contact_id,
        "x_policy_contact_id": x_policy_contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_policy_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_policy_contact"
    )


def update_policy_last_visited(
    revision_id: str | None = None,
    params: dict[str, Any] | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Policy Last Visited.

    POST /api/v2/policies/update_policy_last_visited
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "params": params,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_policy_last_visited",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_policy_last_visited"
    )


def update_primary_property(
    property_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Primary Property.

    POST /api/v2/policies/update_primary_property
    """
    request_json: dict[str, Any] = {
        "property_id": property_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_primary_property",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_primary_property"
    )


def update_property_sub_line_name(
    property_sub_line_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Property Sub Line Name.

    POST /api/v2/policies/update_property_sub_line_name
    """
    request_json: dict[str, Any] = {
        "property_sub_line_id": property_sub_line_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_property_sub_line_name",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_property_sub_line_name"
    )


def update_property_valuation(
    integration_instance_external_id: str | None = None,
    replacement_cost_value: str | None = None,
    property_id: str | None = None,
    property_val: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Property Valuation.

    POST /api/v2/policies/update_property_valuation
    """
    request_json: dict[str, Any] = {
        "integration_instance_external_id": integration_instance_external_id,
        "replacement_cost_value": replacement_cost_value,
        "property_id": property_id,
        "property_val": property_val,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_property_valuation",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_property_valuation"
    )


def update_review_workflow(
    workflow_event: str | None = None,
    event_context: dict[str, Any] | None = None,
    revision_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Review Workflow.

    POST /api/v2/policies/update_review_workflow
    """
    request_json: dict[str, Any] = {
        "workflow_event": workflow_event,
        "event_context": event_context,
        "revision_id": revision_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_review_workflow",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_review_workflow"
    )


def update_underwriting_options(
    revision_id: str | None = None,
    underwriting_options: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Underwriting Options.

    POST /api/v2/policies/update_underwriting_options
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "underwriting_options": underwriting_options,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_underwriting_options",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_underwriting_options"
    )


def update_underwriting_questions(
    revision_id: str | None = None,
    underwriting_questions: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Underwriting Questions.

    POST /api/v2/policies/update_underwriting_questions
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "underwriting_questions": underwriting_questions,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/policies/update_underwriting_questions",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/policies/update_underwriting_questions"
    )


__all__ = [
    "add_external_policies_to_existing_groups",
    "add_policies_to_existing_groups",
    "add_policies_to_new_group",
    "add_sub_line",
    "application_signature_event_callback",
    "apply_pnc_lockbox_payment_transactions",
    "async_create_policy_from_britequote",
    "async_create_revision_from_britequote",
    "async_request_loss_analysis",
    "bind",
    "cancel_policy",
    "cancel_policy_v2",
    "copy_risk",
    "copy_sub_line",
    "create_from_stateless_quote",
    "create_loss_dispute",
    "create_new_policy",
    "create_new_policy_extended",
    "create_policy_from_britequote",
    "create_quote",
    "create_quote_async",
    "create_quote_extended",
    "create_quote_extended_async",
    "create_revision_from_britequote",
    "delete_external_policies",
    "delete_loss_dispute",
    "evaluate_cancellation",
    "export_auto_policies",
    "export_policies",
    "get_loss_disputes",
    "get_policy_groups",
    "get_revision_data_for_stp",
    "get_underlying_policy_changes",
    "get_underwriting_review_workflow",
    "import_iso_protection_classes",
    "import_munichre_eligibility",
    "initialize_application_questions",
    "initiate_property_valuation",
    "issue",
    "ivr_lookup",
    "link_underlying_policy",
    "new_policy_information",
    "new_revision",
    "post_external_policies",
    "rate_quote_revision",
    "remove_line_item",
    "requote_extended",
    "reset_revision_premium",
    "reset_risk_premium",
    "retrieve_account_history",
    "retrieve_cancellation_info",
    "retrieve_current_and_future_policies_terms_with_recurring_payment_method_id",
    "retrieve_files_pending_signature",
    "retrieve_ivans_billing_data",
    "retrieve_pnc_lockbox_matchfile_info",
    "retrieve_policy_change_logs",
    "retrieve_potential_policies_payors",
    "retrieve_properties_by_coverage_name",
    "retrieve_properties_by_group",
    "retrieve_rates_for_quote",
    "retrieve_revision_analysis",
    "retrieve_revision_invoice_numbers",
    "retrieve_revision_property_group_numbers",
    "retrieve_revision_status",
    "retrieve_underlying_policy",
    "rewrite_policy",
    "run_property_lookup",
    "run_underwriting_rules",
    "set_binder_to_active",
    "set_exclude_from_combined_billing",
    "store_policy_information",
    "store_policy_information_extended",
    "store_renewal_status",
    "store_revision_description",
    "submit_quote",
    "sync_item_within_a_property_group",
    "sync_underlying_policy_changes",
    "update_billing_schedule",
    "update_builder_ready_to_rate",
    "update_contact_interest",
    "update_effective_and_expiration_date",
    "update_inactive_policy_groups",
    "update_loss_dispute",
    "update_mortgagee_information",
    "update_policies_terms_payment_method_batch",
    "update_policy_contact",
    "update_policy_last_visited",
    "update_primary_property",
    "update_property_sub_line_name",
    "update_property_valuation",
    "update_review_workflow",
    "update_underwriting_options",
    "update_underwriting_questions",
]


def list_policies(
    page: int = 1,
    limit: int = 100,
    client: BritecoreAPIClient | None = None,
    **kwargs: Any,
) -> Any:
    """Return a paginated slice of policies via the search endpoint.

    This function is a pagination helper used by ``iter_policies``.
    It calls ``/api/v2/policies/search`` with ``current_page`` and
    ``page_size`` set from ``page`` / ``limit`` and returns the raw
    normalized response so the iterator can extract ``data``.

    Args:
        page: Page number (1-based).
        limit: Results per page.
        client: Optional explicit client; defaults to the module-level client.
        **kwargs: Additional request parameters.

    Returns:
        Normalized API response dict, typically ``{"data": [...], ...}``.
    """
    _client = client if client is not None else API_CLIENT
    if _client is API_CLIENT:
        raw = search_policies(
            sort_obj={"field": "policy_number", "order": "asc"},
            current_page=page,
            page_size=limit,
            **kwargs,
        )
    else:
        request_json: dict[str, Any] = {
            "sort_obj": {"field": "policy_number", "order": "asc"},
            "current_page": page,
            "page_size": limit,
        }
        request_result = _client.do_request(
            path="/api/v2/policies/search",
            json=request_json,
            **kwargs,
        )
        raw = _client.process_result(request_result)
    # Normalise to {"data": [...]} so iter_policies works uniformly
    if isinstance(raw, dict) and "records" in raw:
        return {"data": raw["records"]}
    if isinstance(raw, list):
        return {"data": raw}
    return {"data": []}
