"""BriteCore v2 Contacts API endpoint wrappers.

This module provides wrappers for contact creation, updates, role assignment,
lookup by identifier, and filtered contact search.
"""

from logging import Logger
from typing import Any, Literal, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk import BritecoreError, logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.constants import (
    DEFAULT_ADDRESS_TYPE,
    DEFAULT_EMAIL_TYPE,
    DEFAULT_PHONE_TYPE,
)
from britecore_sdk.models.contact import ROLETYPES
from britecore_sdk.validators.address_validator import _ADDRESS_TYPE_NORMALIZER
from britecore_sdk.validators.email_validator import _EMAIL_TYPE_NORMALIZER
from britecore_sdk.validators.phone_validator import _PHONE_TYPE_NORMALIZER

LOGGER: Logger = logger
API_CLIENT: BritecoreAPIClient = api_client


def new_contact(
    name: str,
    address: list[dict[str, str]],
    phone: list[dict[str, str] | None] | None = None,
    email: list[dict[str, str] | None] | None = None,
    contact_type: Literal["individual", "organization"] | None = "individual",
    client: BritecoreAPIClient | None = None,
    **kwargs: Unpack[RequestParameters],
) -> tuple[Any, str | None]:
    """Create a contact record.

    POST /api/v2/contacts/new_contact
    """
    # Validate required parameters
    if not name or not name.strip():
        raise BritecoreError.MissingParameter("contact name is required")
    if not address or len(address) == 0:
        raise BritecoreError.MissingParameter("contact address list is required")

    LOGGER.debug("Creating contact '%s'", name)
    if not phone:
        phone = [{}]
    if not email:
        email = [{}]

    # Normalise address types to BC-accepted quick-code values before sending.
    normalized_address: list[dict[str, str]] = []
    for entry in address:
        if not isinstance(entry, dict):
            normalized_address.append(entry)
            continue
        raw_type = entry.get("type", DEFAULT_ADDRESS_TYPE) or DEFAULT_ADDRESS_TYPE
        mapped_type = _ADDRESS_TYPE_NORMALIZER.get(raw_type.lower(), raw_type)
        normalized_address.append({**entry, "type": mapped_type})
    address = normalized_address

    # Normalise phone types to BC-accepted quick-code values before sending.
    # Entries that are empty dicts (placeholder) are left untouched.
    normalized_phone: list[dict[str, str] | None] = []
    for phone_entry in phone:
        if not phone_entry or not isinstance(phone_entry, dict):
            normalized_phone.append(phone_entry)
            continue
        raw_type = phone_entry.get("type", "") or ""
        if not raw_type:
            raw_type = DEFAULT_PHONE_TYPE
        mapped_type = _PHONE_TYPE_NORMALIZER.get(raw_type.lower(), raw_type)
        normalized_phone.append({**phone_entry, "type": mapped_type})
    phone = normalized_phone

    # Normalise email types to BC-accepted quick-code values before sending.
    # Entries that are empty dicts (placeholder) are left untouched.
    normalized_email: list[dict[str, str] | None] = []
    for email_entry in email:
        if not email_entry or not isinstance(email_entry, dict):
            normalized_email.append(email_entry)
            continue
        raw_type = email_entry.get("type", "") or ""
        if not raw_type:
            raw_type = DEFAULT_EMAIL_TYPE
        mapped_type = _EMAIL_TYPE_NORMALIZER.get(raw_type.lower(), raw_type)
        normalized_email.append({**email_entry, "type": mapped_type})
    email = normalized_email

    contact_request_json: dict[str, Any] = {
        "name": name,
        "addresses": address,
    }
    if email[0] != {}:
        contact_request_json.update({"emails": email})
    if phone[0] != {}:
        contact_request_json.update({"phones": phone})

    contact_request_json.update({"type": contact_type})

    effective_client: BritecoreAPIClient = client or API_CLIENT

    request_result: BaseHTTPResponse | HTTPResponse | None = (
        effective_client.do_request(
            path="/api/v2/contacts/new_contact", json=contact_request_json, **kwargs
        )
    )

    contact_json: Any = effective_client.process_result(
        request_result, endpoint="/api/v2/contacts/new_contact"
    )

    try:
        new_id = contact_json.get("contact_id", "Fail")
    except AttributeError:
        new_id = "Fail"

    if new_id == "Fail":
        LOGGER.error("Failed to add contact - '%s'", name)
        return None, None

    LOGGER.debug("Added '%s'", name)
    return contact_json, new_id


def add_contact_to_role(
    contact_id: str,
    role: ROLETYPES | None = "Named Insured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Assign an existing contact to a role.

    POST /api/v2/contacts/add_contact_to_role
    """
    # Validate required parameters
    if not contact_id or not contact_id.strip():
        raise BritecoreError.MissingParameter("contact_id is required")

    LOGGER.debug("Adding role '%s' to '%s'", role, contact_id)
    role_request_json: dict[str, str | ROLETYPES | None] = {
        "contact_id": contact_id,
        "role_name": role,
    }
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/add_contact_to_role",
        json=role_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/add_contact_to_role"
    )


def update_contact(
    contact: dict[str, str | list[dict[str, str]]], **kwargs: Unpack[RequestParameters]
) -> Any:
    """Update an existing contact record.

    POST /api/v2/contacts/update_contact
    """
    LOGGER.debug("Updating contact information\n%s", contact)
    update_request_json: dict[str, dict] = {"contact": contact}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/update_contact",
        json=update_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/update_contact"
    )


def get_contact(contact_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a contact by identifier.

    POST /api/v2/contacts/get_contact
    """
    # Validate required parameters
    if not contact_id or not contact_id.strip():
        raise BritecoreError.MissingParameter("contact_id is required")

    LOGGER.debug("Retrieving contact id '%s'", contact_id)
    contact_retrieve_json: dict[str, str] = {"contact_id": contact_id}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact",
        json=contact_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contact"
    )


def find_contact_by_params(
    name: str,
    role_name: ROLETYPES | None = None,
    dob: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Search for contacts by name and optional filters.

    POST /api/v2/contacts/find_contact_by_params
    """
    LOGGER.debug("Finding contact '%s'", name)
    contact_retrieve_json: dict[str, str | ROLETYPES | None] = {
        "name": name,
        "role_name": role_name,
        "dob": dob,
    }
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/find_contact_by_params",
        json=contact_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/find_contact_by_params"
    )


def get_contacts_by_ids(
    contact_id_list: list[str], **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve contacts by a list of IDs.

    POST /api/v2/contacts/get_contacts_by_ids
    """
    if (
        not contact_id_list
        or not isinstance(contact_id_list, list)
        or not all(isinstance(x, str) for x in contact_id_list)
    ):
        raise BritecoreError.MissingParameter(
            "contact_id_list (list of str) is required"
        )
    LOGGER.debug("Retrieving contacts by ids: %s", contact_id_list)
    request_json: dict[str, str] = {"contact_id_list": ",".join(contact_id_list)}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contacts_by_ids",
        json=request_json,
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contacts_by_ids"
    )


__all__ = [
    "new_contact",
    "add_contact_to_role",
    "update_contact",
    "get_contact",
    "find_contact_by_params",
    "get_contacts_by_ids",
]

# --- Autogenerated spec wrappers ---
# Some wrapper signatures intentionally preserve API field names even when they
# shadow Python built-ins (for compatibility with existing keyword-callers).


def add_member_to_agency(
    set_member_company: str | None = None,
    agency_id: str | None = None,
    member_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add Member To Agency.

    POST /api/v2/contacts/add_member_to_agency
    """
    request_json: dict[str, Any] = {
        "set_member_company": set_member_company,
        "agency_id": agency_id,
        "member_id": member_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/add_member_to_agency",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/add_member_to_agency"
    )


def assign_policy_contact(
    role: str | None = None,
    contact_id: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Assign Policy Contact.

    POST /api/v2/contacts/assign_policy_contact
    """
    request_json: dict[str, Any] = {
        "role": role,
        "contact_id": contact_id,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/assign_policy_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/assign_policy_contact"
    )


def assign_quote_contact(
    role: str | None = None,
    quote_id: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Assign Quote Contact.

    POST /api/v2/contacts/assign_quote_contact
    """
    request_json: dict[str, Any] = {
        "role": role,
        "quote_id": quote_id,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/assign_quote_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/assign_quote_contact"
    )


def assign_risk_contact(
    role: str | None = None,
    risk_id: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Assign Risk Contact.

    POST /api/v2/contacts/assign_risk_contact
    """
    request_json: dict[str, Any] = {
        "role": role,
        "risk_id": risk_id,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/assign_risk_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/assign_risk_contact"
    )


def check_username_availability(
    username: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check Username Availability.

    POST /api/v2/contacts/check_username_availability
    """
    request_json: dict[str, Any] = {
        "username": username,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/check_username_availability",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/check_username_availability"
    )


def create_contact(  # pylint: disable=redefined-builtin
    username: str | None = None,
    source_update_date: str | None = None,
    dba: str | None = None,
    phones: list[dict[str, Any]] | None = None,
    date_business_started: str | None = None,
    agency_number: str | None = None,
    company_id: str | None = None,
    agent_ids: list[str] | None = None,
    ssn_group: str | None = None,
    driver_license_date: str | None = None,
    commission_structure: str | None = None,
    agency_group_number: str | None = None,
    agency_inception_date: str | None = None,
    fein_tax_id: str | None = None,
    date_of_birth: str | None = None,
    agency_group_id: str | None = None,
    purchase_date: str | None = None,
    type: str | None = None,
    last_synched_date: str | None = None,
    added_by: str | None = None,
    producer_number: str | None = None,
    website: str | None = None,
    hicn_number: str | None = None,
    follow_agency_quoting_restriction: bool | None = None,
    date_of_death: str | None = None,
    ssn: str | None = None,
    agency_id: str | None = None,
    drivers_license: str | None = None,
    confirmation_email: str | None = None,
    agency_termination_date: str | None = None,
    emails: list[dict[str, Any]] | None = None,
    addresses: list[dict[str, Any]] | None = None,
    external_system_reference: str | None = None,
    name: str | None = None,
    roles: list[dict[str, Any]] | None = None,
    gender: str | None = None,
    license_state: str | None = None,
    legal_entity_type: str | None = None,
    position: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create Contact.

    POST /api/v2/contacts/create_contact
    """
    request_json: dict[str, Any] = {
        "username": username,
        "source_update_date": source_update_date,
        "dba": dba,
        "phones": phones,
        "date_business_started": date_business_started,
        "agency_number": agency_number,
        "company_id": company_id,
        "agent_ids": agent_ids,
        "ssn_group": ssn_group,
        "driver_license_date": driver_license_date,
        "commission_structure": commission_structure,
        "agency_group_number": agency_group_number,
        "agency_inception_date": agency_inception_date,
        "fein_tax_id": fein_tax_id,
        "date_of_birth": date_of_birth,
        "agency_group_id": agency_group_id,
        "purchase_date": purchase_date,
        "type": type,
        "last_synched_date": last_synched_date,
        "added_by": added_by,
        "producer_number": producer_number,
        "website": website,
        "hicn_number": hicn_number,
        "follow_agency_quoting_restriction": follow_agency_quoting_restriction,
        "date_of_death": date_of_death,
        "ssn": ssn,
        "agency_id": agency_id,
        "drivers_license": drivers_license,
        "confirmation_email": confirmation_email,
        "agency_termination_date": agency_termination_date,
        "emails": emails,
        "addresses": addresses,
        "external_system_reference": external_system_reference,
        "name": name,
        "roles": roles,
        "gender": gender,
        "license_state": license_state,
        "legal_entity_type": legal_entity_type,
        "position": position,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/create_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/create_contact"
    )


def create_credit_report_for_contact(
    policy_type_id: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create Credit Report For Contact.

    POST /api/v2/contacts/create_credit_report_for_contact
    """
    request_json: dict[str, Any] = {
        "policy_type_id": policy_type_id,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/create_credit_report_for_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/create_credit_report_for_contact"
    )


def credit_score_threshold_details(
    ref_contact_id: str | None = None,
    contact_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Credit Score Threshold Details.

    POST /api/v2/contacts/credit_score_threshold_details
    """
    request_json: dict[str, Any] = {
        "ref_contact_id": ref_contact_id,
        "contact_ids": contact_ids,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/credit_score_threshold_details",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/credit_score_threshold_details"
    )


def enable_or_disable_contact(
    active: bool | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Enable Or Disable Contact.

    POST /api/v2/contacts/enable_or_disable_contact
    """
    request_json: dict[str, Any] = {
        "active": active,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/enable_or_disable_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/enable_or_disable_contact"
    )


def generate_contact_number(
    contact_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Generate Contact Number.

    POST /api/v2/contacts/generate_contact_number
    """
    request_json: dict[str, Any] = {"contact_id": contact_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/generate_contact_number",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/generate_contact_number"
    )


def get_aspect_data(  # pylint: disable=redefined-builtin
    all: str | None = None,
    id: str | None = None,
    has_permissions: str | None = None,
    role_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Aspect Data.

    POST /api/v2/contacts/get_aspect_data
    """
    request_json: dict[str, Any] = {
        "all": all,
        "id": id,
        "has_permissions": has_permissions,
        "role_id": role_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_aspect_data",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_aspect_data"
    )


def get_aspect_data_settings(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Aspect Data Settings.

    POST /api/v2/contacts/get_aspect_data_settings
    """
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_aspect_data_settings",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_aspect_data_settings"
    )


def get_contact_associations(
    policy_type_ids: list[str] | None = None,
    contact_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Contact Associations.

    POST /api/v2/contacts/get_contact_associations
    """
    request_json: dict[str, Any] = {
        "policy_type_ids": policy_type_ids,
        "contact_ids": contact_ids,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact_associations",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contact_associations"
    )


def get_contact_by_agency(
    agency_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Contact By Agency.

    POST /api/v2/contacts/get_contact_by_agency
    """
    request_json: dict[str, Any] = {
        "agency_number": agency_number,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact_by_agency",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contact_by_agency"
    )


def get_contact_by_agency_group(
    agency_group_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Contact By Agency Group.

    POST /api/v2/contacts/get_contact_by_agency_group
    """
    request_json: dict[str, Any] = {
        "agency_group_number": agency_group_number,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact_by_agency_group",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contact_by_agency_group"
    )


def get_contact_by_agent(
    producer_number: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Contact By Agent.

    POST /api/v2/contacts/get_contact_by_agent
    """
    request_json: dict[str, Any] = {
        "producer_number": producer_number,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact_by_agent",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contact_by_agent"
    )


def get_contact_by_cognito_username(
    cognito_username: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Contact By Cognito Username.

    POST /api/v2/contacts/get_contact_by_cognito_username
    """
    request_json: dict[str, Any] = {
        "cognito_username": cognito_username,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact_by_cognito_username",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contact_by_cognito_username"
    )


def get_contact_by_credentials(
    username: str | None = None,
    password: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Contact By Credentials.

    POST /api/v2/contacts/get_contact_by_credentials
    """
    request_json: dict[str, Any] = {
        "username": username,
        "password": password,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact_by_credentials",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contact_by_credentials"
    )


def get_contact_for_migration(
    search_str: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Contact For Migration.

    POST /api/v2/contacts/get_contact_for_migration
    """
    request_json: dict[str, Any] = {
        "search_str": search_str,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact_for_migration",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_contact_for_migration"
    )


def get_payment_methods(
    payment_method_ids: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Payment Methods.

    POST /api/v2/contacts/get_payment_methods
    """
    request_json: dict[str, Any] = {
        "payment_method_ids": payment_method_ids,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_payment_methods",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_payment_methods"
    )


def get_resource_producer_id(
    revision_id: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Resource Producer Id.

    POST /api/v2/contacts/get_resource_producer_id
    """
    request_json: dict[str, Any] = {
        "revision_id": revision_id,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_resource_producer_id",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/get_resource_producer_id"
    )


def link_contact_to_cognito_user(
    cognito_username: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Link Contact To Cognito User.

    POST /api/v2/contacts/link_contact_to_cognito_user
    """
    request_json: dict[str, Any] = {
        "cognito_username": cognito_username,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/link_contact_to_cognito_user",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/link_contact_to_cognito_user"
    )


def list_all_contacts(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List All Contacts.

    POST /api/v2/contacts/list_all_contacts
    """
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/list_all_contacts",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/list_all_contacts"
    )


def list_contacts(
    page: int = 1,
    limit: int = 100,
    client: BritecoreAPIClient | None = None,
    **kwargs: Any,
) -> Any:
    """Return a paginated list of contacts.

    Pagination helper used by ``iter_contacts``.  Delegates to
    ``/api/v2/contacts/list_all_contacts`` and normalises the response
    to ``{"data": [...]}``.

    Args:
        page: Page number (1-based, passed in request payload).
        limit: Results per page, passed in request payload.
        client: Optional explicit client; defaults to module-level client.
        **kwargs: Additional request parameters.

    Returns:
        Normalized response dict ``{"data": [...]}``.
    """
    _client = client if client is not None else API_CLIENT
    request_json: dict[str, Any] = {"page": page, "limit": limit}
    request_result = _client.do_request(
        path="/api/v2/contacts/list_all_contacts",
        json=request_json,
        method="POST",
        **kwargs,
    )
    raw = _client.process_result(
        request_result, endpoint="/api/v2/contacts/list_all_contacts"
    )
    if isinstance(raw, list):
        return {"data": raw}
    if isinstance(raw, dict) and "data" not in raw:
        return {"data": []}
    return raw


def list_credit_reports_for_contact(
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List Credit Reports For Contact.

    POST /api/v2/contacts/list_credit_reports_for_contact
    """
    request_json: dict[str, Any] = {
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/list_credit_reports_for_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/list_credit_reports_for_contact"
    )


def list_emails_for_contact(
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List Emails For Contact.

    POST /api/v2/contacts/list_emails_for_contact
    """
    request_json: dict[str, Any] = {
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/list_emails_for_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/list_emails_for_contact"
    )


def modify_contact(  # pylint: disable=redefined-builtin
    username: str | None = None,
    drivers_license: str | None = None,
    dba: str | None = None,
    phones: list[dict[str, Any]] | None = None,
    date_business_started: str | None = None,
    agency_number: str | None = None,
    company_id: str | None = None,
    id: str | None = None,
    ssn_group: str | None = None,
    driver_license_date: str | None = None,
    commission_structure: str | None = None,
    agency_group_number: str | None = None,
    agency_inception_date: str | None = None,
    fein_tax_id: str | None = None,
    date_of_birth: str | None = None,
    purchase_date: str | None = None,
    type: str | None = None,
    last_synched_date: str | None = None,
    added_by: str | None = None,
    agent_ids: list[str] | None = None,
    website: str | None = None,
    hicn_number: str | None = None,
    follow_agency_quoting_restriction: bool | None = None,
    date_of_death: str | None = None,
    ssn: str | None = None,
    source_update_date: str | None = None,
    confirmation_email: str | None = None,
    agency_termination_date: str | None = None,
    emails: list[dict[str, Any]] | None = None,
    addresses: list[dict[str, Any]] | None = None,
    external_system_reference: str | None = None,
    name: str | None = None,
    roles: list[dict[str, Any]] | None = None,
    gender: str | None = None,
    license_state: str | None = None,
    legal_entity_type: str | None = None,
    position: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Modify Contact.

    POST /api/v2/contacts/modify_contact
    """
    request_json: dict[str, Any] = {
        "username": username,
        "drivers_license": drivers_license,
        "dba": dba,
        "phones": phones,
        "date_business_started": date_business_started,
        "agency_number": agency_number,
        "company_id": company_id,
        "id": id,
        "ssn_group": ssn_group,
        "driver_license_date": driver_license_date,
        "commission_structure": commission_structure,
        "agency_group_number": agency_group_number,
        "agency_inception_date": agency_inception_date,
        "fein_tax_id": fein_tax_id,
        "date_of_birth": date_of_birth,
        "purchase_date": purchase_date,
        "type": type,
        "last_synched_date": last_synched_date,
        "added_by": added_by,
        "agent_ids": agent_ids,
        "website": website,
        "hicn_number": hicn_number,
        "follow_agency_quoting_restriction": follow_agency_quoting_restriction,
        "date_of_death": date_of_death,
        "ssn": ssn,
        "source_update_date": source_update_date,
        "confirmation_email": confirmation_email,
        "agency_termination_date": agency_termination_date,
        "emails": emails,
        "addresses": addresses,
        "external_system_reference": external_system_reference,
        "name": name,
        "roles": roles,
        "gender": gender,
        "license_state": license_state,
        "legal_entity_type": legal_entity_type,
        "position": position,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/modify_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/modify_contact"
    )


def remove_contact_from_role(
    role_name: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove Contact From Role.

    POST /api/v2/contacts/remove_contact_from_role
    """
    request_json: dict[str, Any] = {
        "role_name": role_name,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/remove_contact_from_role",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/remove_contact_from_role"
    )


def remove_contact_information(
    contact_emails: list[str] | None = None,
    contact_addresses: list[str] | None = None,
    contact_phones: list[str] | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove Contact Information.

    POST /api/v2/contacts/remove_contact_information
    """
    request_json: dict[str, Any] = {
        "contact_emails": contact_emails,
        "contact_addresses": contact_addresses,
        "contact_phones": contact_phones,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/remove_contact_information",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/remove_contact_information"
    )


def remove_contact_system_tags(
    system_tags: list[str] | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove Contact System Tags.

    POST /api/v2/contacts/remove_contact_system_tags
    """
    request_json: dict[str, Any] = {
        "system_tags": system_tags,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/remove_contact_system_tags",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/remove_contact_system_tags"
    )


def remove_policy_contact(
    role: str | None = None,
    contact_id: str | None = None,
    policy_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove Policy Contact.

    POST /api/v2/contacts/remove_policy_contact
    """
    request_json: dict[str, Any] = {
        "role": role,
        "contact_id": contact_id,
        "policy_id": policy_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/remove_policy_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/remove_policy_contact"
    )


def remove_quote_contact(
    role: str | None = None,
    quote_id: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove Quote Contact.

    POST /api/v2/contacts/remove_quote_contact
    """
    request_json: dict[str, Any] = {
        "role": role,
        "quote_id": quote_id,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/remove_quote_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/remove_quote_contact"
    )


def remove_risk_contact(
    role: str | None = None,
    risk_id: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove Risk Contact.

    POST /api/v2/contacts/remove_risk_contact
    """
    request_json: dict[str, Any] = {
        "role": role,
        "risk_id": risk_id,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/remove_risk_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/remove_risk_contact"
    )


def retrieveaddressinfo(  # pylint: disable=redefined-builtin
    stateAbbr: str | None = None,
    zip: str | None = None,
    addressLine1: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieveaddressinfo.

    POST /api/v2/contacts/retrieveAddressInfo
    """
    request_json: dict[str, Any] = {
        "stateAbbr": stateAbbr,
        "zip": zip,
        "addressLine1": addressLine1,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieveAddressInfo",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieveAddressInfo"
    )


def retrieve_address_suggestions(
    address_line2: str | None = None,
    address_city: str | None = None,
    address_line1: str | None = None,
    address_state: str | None = None,
    policy_type_id: str | None = None,
    address_country: str | None = None,
    address_zip: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Address Suggestions.

    POST /api/v2/contacts/retrieve_address_suggestions
    """
    request_json: dict[str, Any] = {
        "address_line2": address_line2,
        "address_city": address_city,
        "address_line1": address_line1,
        "address_state": address_state,
        "policy_type_id": policy_type_id,
        "address_country": address_country,
        "address_zip": address_zip,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_address_suggestions",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_address_suggestions"
    )


def retrieve_addresses(
    address_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Addresses.

    POST /api/v2/contacts/retrieve_addresses
    """
    request_json: dict[str, Any] = {
        "address_ids": address_ids,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_addresses",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_addresses"
    )


def retrieve_agencies_near_zip(
    max_distance: int | None = None,
    zipcode: str | None = None,
    results: int | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Agencies Near Zip.

    POST /api/v2/contacts/retrieve_agencies_near_zip
    """
    request_json: dict[str, Any] = {
        "max_distance": max_distance,
        "zipcode": zipcode,
        "results": results,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_agencies_near_zip",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_agencies_near_zip"
    )


def retrieve_all_roles(
    login_only: bool | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve All Roles.

    POST /api/v2/contacts/retrieve_all_roles
    """
    request_json: dict[str, Any] = {
        "login_only": login_only,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_all_roles",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_all_roles"
    )


def retrieve_contact(
    external_system_reference: str | None = None,
    id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Contact.

    POST /api/v2/contacts/retrieve_contact
    """
    request_json: dict[str, Any] = {
        "external_system_reference": external_system_reference,
        "id": id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_contact"
    )


def retrieve_contact_info(
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Contact Info.

    POST /api/v2/contacts/retrieve_contact_info
    """
    request_json: dict[str, Any] = {
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_contact_info",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_contact_info"
    )


def retrieve_contact_motor_vehicle_reports(
    store_no_hit: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Contact Motor Vehicle Reports.

    POST /api/v2/contacts/retrieve_contact_motor_vehicle_reports
    """
    request_json: dict[str, Any] = {
        "store_no_hit": store_no_hit,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_contact_motor_vehicle_reports",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/contacts/retrieve_contact_motor_vehicle_reports",
    )


def retrieve_contact_system_tags(
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Contact System Tags.

    POST /api/v2/contacts/retrieve_contact_system_tags
    """
    request_json: dict[str, Any] = {
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_contact_system_tags",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_contact_system_tags"
    )


def retrieve_credit_score_tier(
    policy_type_id: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Credit Score Tier.

    POST /api/v2/contacts/retrieve_credit_score_tier
    """
    request_json: dict[str, Any] = {
        "policy_type_id": policy_type_id,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_credit_score_tier",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_credit_score_tier"
    )


def retrieve_dob_and_ssn(
    contact_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Dob And Ssn.

    POST /api/v2/contacts/retrieve_dob_and_ssn
    """
    request_json: dict[str, Any] = {
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_dob_and_ssn",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_dob_and_ssn"
    )


def retrieve_quoting_permissions(
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Quoting Permissions.

    POST /api/v2/contacts/retrieve_quoting_permissions
    """
    request_json: dict[str, Any] = {
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_quoting_permissions",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_quoting_permissions"
    )


def retrieve_related_contacts(
    result_structure: str | None = None,
    attributes_required: str | None = None,
    cognito_username: str | None = None,
    contact_id: str | None = None,
    relations_required: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Related Contacts.

    POST /api/v2/contacts/retrieve_related_contacts
    """
    request_json: dict[str, Any] = {
        "result_structure": result_structure,
        "attributes_required": attributes_required,
        "cognito_username": cognito_username,
        "contact_id": contact_id,
        "relations_required": relations_required,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/retrieve_related_contacts",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/retrieve_related_contacts"
    )


def search_names_emails(
    query: str | None = None,
    limit: int | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Search Names Emails.

    POST /api/v2/contacts/search_names_emails
    """
    request_json: dict[str, Any] = {
        "query": query,
        "limit": limit,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/search_names_emails",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/search_names_emails"
    )


def set_aspect_data(
    payments_issued: dict[str, Any] | None = None,
    agency_number: dict[str, Any] | None = None,
    login_information: dict[str, Any] | None = None,
    id: str | None = None,
    commission_payment: dict[str, Any] | None = None,
    agency_dates: dict[str, Any] | None = None,
    agency_group_number: dict[str, Any] | None = None,
    role_id: str | None = None,
    inactive_agency: bool | None = None,
    vendor_number: dict[str, Any] | None = None,
    producer_number: dict[str, Any] | None = None,
    notices: dict[str, Any] | None = None,
    commission_structure: dict[str, Any] | None = None,
    quoting_restriction: dict[str, Any] | None = None,
    default_surplus_lines_producer: dict[str, Any] | None = None,
    interest_content: dict[str, Any] | None = None,
    sweep_account: dict[str, Any] | None = None,
    agencies: dict[str, Any] | None = None,
    disallow_e2_value: bool | None = None,
    is_1099_reportable: dict[str, Any] | None = None,
    personal_information: dict[str, Any] | None = None,
    default_agency: dict[str, Any] | None = None,
    naic_number: dict[str, Any] | None = None,
    credit_score_account: dict[str, Any] | None = None,
    agency_group: dict[str, Any] | None = None,
    termination: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set Aspect Data.

    POST /api/v2/contacts/set_aspect_data
    """
    request_json: dict[str, Any] = {
        "payments_issued": payments_issued,
        "agency_number": agency_number,
        "login_information": login_information,
        "id": id,
        "commission_payment": commission_payment,
        "agency_dates": agency_dates,
        "agency_group_number": agency_group_number,
        "role_id": role_id,
        "inactive_agency": inactive_agency,
        "vendor_number": vendor_number,
        "producer_number": producer_number,
        "notices": notices,
        "commission_structure": commission_structure,
        "quoting_restriction": quoting_restriction,
        "default_surplus_lines_producer": default_surplus_lines_producer,
        "interest_content": interest_content,
        "sweep_account": sweep_account,
        "agencies": agencies,
        "disallow_e2_value": disallow_e2_value,
        "is_1099_reportable": is_1099_reportable,
        "personal_information": personal_information,
        "default_agency": default_agency,
        "naic_number": naic_number,
        "credit_score_account": credit_score_account,
        "agency_group": agency_group,
        "termination": termination,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/set_aspect_data",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/set_aspect_data"
    )


def set_contact_system_tags(
    system_tags: list[str] | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set Contact System Tags.

    POST /api/v2/contacts/set_contact_system_tags
    """
    request_json: dict[str, Any] = {
        "system_tags": system_tags,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/set_contact_system_tags",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/set_contact_system_tags"
    )


def set_quoting_permissions(
    states: str | None = None,
    policy_types: str | None = None,
    role: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set Quoting Permissions.

    POST /api/v2/contacts/set_quoting_permissions
    """
    request_json: dict[str, Any] = {
        "states": states,
        "policy_types": policy_types,
        "role": role,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/set_quoting_permissions",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/set_quoting_permissions"
    )


def store_contact_gender(
    gender: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Store Contact Gender.

    POST /api/v2/contacts/store_contact_gender
    """
    request_json: dict[str, Any] = {
        "gender": gender,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/store_contact_gender",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/store_contact_gender"
    )


def update_contact_number(
    contact_id: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Contact Number.

    POST /api/v2/contacts/update_contact_number
    """
    request_json: dict[str, Any] = {"contact_id": contact_id}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/update_contact_number",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/update_contact_number"
    )


def update_contacts(
    contacts: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update Contacts.

    POST /api/v2/contacts/update_contacts
    """
    request_json: dict[str, Any] = {
        "contacts": contacts,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/update_contacts",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/update_contacts"
    )


def validate_last_4_ssn_digits(
    last_4_ssn_digits: str | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Validate Last 4 Ssn Digits.

    POST /api/v2/contacts/validate_last_4_ssn_digits
    """
    request_json: dict[str, Any] = {
        "last_4_ssn_digits": last_4_ssn_digits,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/validate_last_4_ssn_digits",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/validate_last_4_ssn_digits"
    )


__all__.extend(
    [
        "add_member_to_agency",
        "assign_policy_contact",
        "assign_quote_contact",
        "assign_risk_contact",
        "check_username_availability",
        "create_contact",
        "create_credit_report_for_contact",
        "credit_score_threshold_details",
        "enable_or_disable_contact",
        "generate_contact_number",
        "get_aspect_data",
        "get_aspect_data_settings",
        "get_contact_associations",
        "get_contact_by_agency",
        "get_contact_by_agency_group",
        "get_contact_by_agent",
        "get_contact_by_cognito_username",
        "get_contact_by_credentials",
        "get_contact_for_migration",
        "get_payment_methods",
        "get_resource_producer_id",
        "link_contact_to_cognito_user",
        "list_all_contacts",
        "list_credit_reports_for_contact",
        "list_emails_for_contact",
        "modify_contact",
        "remove_contact_from_role",
        "remove_contact_information",
        "remove_contact_system_tags",
        "remove_policy_contact",
        "remove_quote_contact",
        "remove_risk_contact",
        "retrieveaddressinfo",
        "retrieve_address_suggestions",
        "retrieve_addresses",
        "retrieve_agencies_near_zip",
        "retrieve_all_roles",
        "retrieve_contact",
        "retrieve_contact_info",
        "retrieve_contact_motor_vehicle_reports",
        "retrieve_contact_system_tags",
        "retrieve_credit_score_tier",
        "retrieve_dob_and_ssn",
        "retrieve_quoting_permissions",
        "retrieve_related_contacts",
        "search_names_emails",
        "set_aspect_data",
        "set_contact_system_tags",
        "set_quoting_permissions",
        "store_contact_gender",
        "update_contact_number",
        "update_contacts",
        "validate_last_4_ssn_digits",
    ]
)
