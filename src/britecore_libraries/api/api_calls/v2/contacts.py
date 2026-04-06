"""BriteCore v2 Contacts API endpoint wrappers.

Provides:
    new_contact            -- Create a new individual or organization contact.
    add_contact_to_role    -- Assign an existing contact to a named role.
    update_contact         -- Update fields on an existing contact record.
    get_contact            -- Retrieve a contact by its unique ID.
    find_contact_by_params -- Search for contacts by name, role, or date of birth.
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
    """
    Creates a new contact with the provided details and returns the contact JSON and ID.

    This function constructs a contact request using the provided name, address, and optional
    phone and email information. It sends the request to the API to create a new contact
    and returns the resulting contact data along with its ID.

    Parameters:
        name: The name of the contact to be created.
        address: A list of dictionaries containing address details for the contact.
        phone: An optional list of dictionaries containing phone details for the contact.
        email: An optional list of dictionaries containing email details for the contact.
        contact_type: The type of contact, either "individual" or  "organization". (Default: "individual")
        **kwargs: Additional keyword arguments to be passed to the API client request.

    Returns:
        A tuple containing the contact JSON data and the contact ID. If the creation fails,
        both values in the tuple will be None.
    """
    LOGGER.debug(f"Creating contact '{name}'")
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

    contact_json: Any = API_CLIENT.process_result(request_result)

    try:
        new_id: str = contact_json.get("contact_id", "Fail")
    except AttributeError:
        new_id: str = "Fail"

    if new_id == "Fail":
        LOGGER.error(f"Failed to add contact - '{name}'")
        return None, None

    LOGGER.debug(f"Added '{name}'")
    return contact_json, new_id


def add_contact_to_role(
    contact_id: str,
    role: ROLETYPES | None = "Named Insured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Add a contact to a specified role.

    This function adds a contact to a role within the system. It constructs a request
    with the contact ID and role information, then sends the request to the API endpoint
    for adding contacts to roles.

    Parameters:
        contact_id (str): The unique identifier of the contact to be added to the role.
        role (Optional[ROLETYPES]): The role to assign to the contact. Defaults to "Named Insured".
        **kwargs (Unpack[RequestParameters]): Additional keyword arguments to pass to the API request.

    Returns:
        Any: The result of processing the API response, typically the response data or None.
    """
    LOGGER.debug(f"Adding role '{role}' to '{contact_id}'")
    role_request_json: dict[
        Literal["contact_id", "role_name"], str | ROLETYPES | None
    ] = {"contact_id": contact_id, "role_name": role}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/add_contact_to_role",
        json=role_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def update_contact(
    contact: dict[str, str | list[dict[str, str]]], **kwargs: Unpack[RequestParameters]
) -> Any:
    """
    Update contact information with the provided data.

    This function sends a request to update contact information using the
    API client. It constructs a request payload with the contact data and
    sends it to the specified API endpoint.

    Parameters
    ----------
    contact : dict[str, str | list[dict[str, str]]]
        Dictionary containing contact information to be updated. The
        structure should include fields like name, email, phone, etc.
        Can also contain nested dictionaries for more complex contact
        structures.
    **kwargs : Unpack[RequestParameters]
        Additional keyword arguments that will be passed to the API
        client's request method. These typically include authentication
        tokens, headers, or other request-specific parameters.

    Returns
    -------
    Any
        The result of processing the API response. The exact type
        depends on the API client's process_result method implementation.

    Notes
    -----
    The function logs the contact information being updated at debug level
    before sending the request. The actual API endpoint used is
    /api/v2/contacts/update_contact.
    """
    LOGGER.debug(f"Updating contact information\n{contact}")
    update_request_json: dict[str, dict] = {"contact": contact}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/update_contact",
        json=update_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def get_contact(contact_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve contact information by contact ID.

    This function fetches contact details from the API using the provided contact ID.
    It constructs a request with the contact ID and sends it to the contacts endpoint.

    Parameters:
        contact_id (str): The unique identifier of the contact to retrieve
        **kwargs: Additional request parameters that will be passed to the API client

    Returns:
        Any: The result of processing the API response, typically contact data

    Raises:
        Any exceptions that may occur during the API request or response processing
    """
    LOGGER.debug(f"Retrieving contact id '{contact_id}'")
    contact_retrieve_json: dict[str, str] = {"contact_id": contact_id}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact",
        json=contact_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def find_contact_by_params(
    name: str,
    role_name: ROLETYPES | None = None,
    dob: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Find a contact by specified parameters.

    This function searches for a contact using the provided name and optional
    role name and date of birth. Additional request parameters can be passed
    through keyword arguments.

    Parameters:
        name: The name of the contact to search for
        role_name: Optional role name to filter contacts by
        dob: Optional date of birth to filter contacts by
        **kwargs: Additional request parameters to pass to the API client

    Returns:
        The result of processing the API request, typically the contact data
        or None if not found

    Raises:
        Any exceptions raised by the API client during request processing
    """
    LOGGER.debug(f"Finding contact '{name}'")
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

    return API_CLIENT.process_result(request_result)
