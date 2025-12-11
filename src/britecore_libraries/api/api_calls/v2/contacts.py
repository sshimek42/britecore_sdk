from britecore_libraries import logger
from britecore_libraries.api.api_calls import api_client

LOGGER = logger

API_CLIENT = api_client


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
    LOGGER.debug("Creating contact")
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

    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/new_contact",
        json=contact_request_json,
    )

    contact_json = API_CLIENT.process_result(request_result)

    try:
        new_id = contact_json.get("contact_id", "Fail")
    except AttributeError:
        new_id = "Fail"

    if new_id == "Fail":
        LOGGER.error(f"Failed to add contact - {name}")
        return None, None

    LOGGER.debug(f"Added {name}")
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
    LOGGER.debug("Adding role")
    role_request_json = {"contact_id": contact_id, "role_name": role}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/add_contact_to_role",
        json=role_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def update_contact(contact: dict, **kwargs) -> dict:
    """Updates contact
    :param contact: Dictionary with changes
    :type contact: dict
    :return: Request result
    :rtype: dict
    """
    LOGGER.debug("Updating contact")
    update_request_json = {"contact": contact}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/update_contact",
        json=update_request_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


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
    LOGGER.debug("Retrieving contact")
    contact_retrieve_json = {"contact_id": contact_id}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/get_contact",
        json=contact_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def find_contact_by_params(name, **kwargs):
    LOGGER.debug("Retrieving contact")
    contact_retrieve_json = {"name": name}
    request_result = API_CLIENT.do_request(
        path="/api/v2/contacts/find_contact_by_params",
        json=contact_retrieve_json,
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)
