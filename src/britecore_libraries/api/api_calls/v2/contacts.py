"""BriteCore v2 Contacts API endpoint wrappers.

This module provides wrappers for contact creation, updates, role assignment,
lookup by identifier, and filtered contact search.
"""

from logging import Logger
from typing import Any, Literal, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_libraries.models.contact import ROLETYPES

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def new_contact(
    name: str,
    address: list[dict[str, str]],
    phone: list[dict[str, str] | None] | None = None,
    email: list[dict[str, str] | None] | None = None,
    contact_type: Literal["individual", "organization"] | None = "individual",
    **kwargs: Unpack[RequestParameters],
) -> tuple[str | None, str | None]:
    """Create a contact record.

    This wrapper sends the contact name, addresses, optional phone and email
    lists, and ``contact_type`` to ``/api/v2/contacts/new_contact``. It returns
    the normalized ``process_result(...)`` payload together with the extracted
    ``contact_id`` as an SDK-specific convenience tuple of
    ``(contact_data, contact_id)``. ``**kwargs`` accepts ``RequestParameters``
    overrides.
    """
    LOGGER.debug("Creating contact '%s'", name)
    if not phone:
        phone = [{}]
    if not email:
        email = [{}]
    contact_request_json: dict[str, str | list] = {
        "name": name,
        "addresses": address,
    }
    if email[0] != {}:
        contact_request_json.update({"emails": email})
    if phone[0] != {}:
        contact_request_json.update({"phones": phone})

    contact_request_json.update({"type": contact_type})

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/new_contact", json=contact_request_json, **kwargs
    )

    contact_json: Any = API_CLIENT.process_result(
        request_result, endpoint="/api/v2/contacts/new_contact"
    )

    try:
        new_id: str = contact_json.get("contact_id", "Fail")
    except AttributeError:
        new_id: str = "Fail"

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

    This wrapper sends ``contact_id`` and ``role`` to
    ``/api/v2/contacts/add_contact_to_role`` and returns the normalized
    ``process_result(...)`` payload for the role-assignment request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Adding role '%s' to '%s'", role, contact_id)
    role_request_json: dict[
        Literal["contact_id", "role_name"], str | ROLETYPES | None
    ] = {"contact_id": contact_id, "role_name": role}
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

    This wrapper sends ``contact`` inside the request body to
    ``/api/v2/contacts/update_contact`` and returns the normalized
    ``process_result(...)`` payload for the update request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
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

    This wrapper sends ``contact_id`` to ``/api/v2/contacts/get_contact`` and
    returns the normalized ``process_result(...)`` payload for the matching
    contact record. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
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

    This wrapper sends ``name`` together with the optional ``role_name`` and
    ``dob`` filters to ``/api/v2/contacts/find_contact_by_params`` and returns
    the normalized ``process_result(...)`` payload for the contact search.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Finding contact '%s'", name)
    contact_retrieve_json: dict[str, str | None] = {
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
