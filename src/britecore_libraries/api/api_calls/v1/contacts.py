from json import loads
from britecore_libraries.api.api_calls import api_client

API_CLIENT = api_client

def retrieve_contact_list(
    search_str: str, search_filter: str = "Named Insured", **kwargs
) -> dict:
    """Retrieve named insured contacts
    :param search_str: Name to search for
    :type search_str: str
    :param search_filter: Name to search for
    :type search_filter: str
    :return: Contacts
    :rtype: dict
    """
    contact_request_json = {
        "searchString": search_str,
        "filter": search_filter,
        "currentPage": 1,
        "pageSize": 10,
    }
    request_result = API_CLIENT.do_request(
        path="/api/v1/contacts/retrieveContactList",
        json=contact_request_json,
        **kwargs,
    )

    contact_json = loads(request_result.data.decode("utf-8"))

    return contact_json["records"]
