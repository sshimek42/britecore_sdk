from logging import Logger
from typing import Any, Optional, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def new_contact(
    name: str,
    address: list[dict[str, str]],
    phone: Optional[list[Optional[dict[str, str]]]] = None,
    email: Optional[list[Optional[dict[str, str]]]] = None,
    contact_type: Optional[str] = "individual",
    **kwargs: Unpack[RequestParameters],
) -> tuple[str | None, str | None]:
    """Creates a new contact
    :param name: Contact name
    :type name: str
    :param address: List of dictionaries with contact's addresses
    :type address: list[dict[str,str]]
    :param phone: List of dictionaries with contact's phone numbers
    :type phone: Optional[list[Optional[dict[str, str]]]]
    :param email: List of dictionaries with contact's e-mails
    :type email: Optional[list[Optional[dict[str, str]]]]
    :param contact_type: Contact type (Defaults to "individual")
    :type contact_type: Optional[str]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Request result and new Contact ID
    :rtype: tuple[str | None, str | None]
    """
    LOGGER.debug(f"Creating contact %f.yellow%{name}%f%")
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

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/contacts/new_contact", json=contact_request_json, **kwargs
    )

    contact_json: Any = API_CLIENT.process_result(request_result)

    try:
        new_id: str = contact_json.get("contact_id", "Fail")
    except AttributeError:
        new_id: str = "Fail"

    if new_id == "Fail":
        LOGGER.error(f"Failed to add contact - %f.yellow%{name}%f%")
        return None, None

    LOGGER.debug(f"Added %f.yellow%{name}%f%")
    return contact_json, new_id


def add_contact_to_role(
    contact_id: str,
    role: Optional[str] = "Named Insured",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Adds role to existing contact
    :param contact_id: Contact ID
    :type contact_id: str
    :param role: Requested role (Defaults to "Named Insured")
    :type role: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Results of request
    :rtype: Any
    """
    LOGGER.debug(
        f"Adding role %f.yellow%{role}%f% to %f.yellow%{contact_id}%f%")
    role_request_json: dict[str, str] = {
        "contact_id": contact_id, "role_name": role}
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/contacts/add_contact_to_role",
        json=role_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def update_contact(
    contact: dict[str, str | list[dict[str, str]]], **kwargs: Unpack[RequestParameters]
) -> Any:
    """Updates contact
    :param contact: Dictionary with changes
    :type contact: dict[str, str | list[dict[str, str]]]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Request result
    :rtype: Any
    """
    LOGGER.debug(f"Updating contact information\n%f.yellow%{contact}%f%")
    update_request_json: dict[str, dict] = {"contact": contact}
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/contacts/update_contact",
        json=update_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def get_contact(contact_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Gets contact info
    :param contact_id: Contact ID to lookup
    :type contact_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Contact info
    :rtype: Any
    """
    LOGGER.debug(f"Retrieving contact id %f.yellow%{contact_id}%f%")
    contact_retrieve_json: dict[str, str] = {"contact_id": contact_id}
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact",
        json=contact_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def find_contact_by_params(
    name: str,
    role_name: Optional[str] = None,
    dob: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Find contact from provided parameters
    :param name: Name to search for
    :type: str
    :param role_name: Assigned role
    :type role_name: Optional[str]
    :param dob: Date of birth (yyyy-mm-dd)
    :type dob: Optional[str]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Search results
    :rtype: Any
    """
    LOGGER.debug(f"Finding contact %f.yellow%{name}%f%")
    contact_retrieve_json: dict[str, str | None] = {
        "name": name,
        "role_name": role_name,
        "dob": dob,
    }
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/contacts/find_contact_by_params",
        json=contact_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)
