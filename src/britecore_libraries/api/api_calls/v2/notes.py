from json import loads

from urllib3 import Timeout

from britecore_libraries.api.api_calls import (api_client, 
                                            web_timeout_long)
from britecore_libraries import logger

LOGGER = logger

API_CLIENT = api_client

def retrieve_notes(policy_id: str) -> list:
    """
    Retrieve policy notes
    :param policy_id: Policy ID
    :type policy_id: str
    :return: Notes
    :rtype: list
    """
    LOGGER.debug("Getting notes")
    notes_search = {
        "id": policy_id,
        "pageSize": 1000,
        "page": 0,
        "ascending": False,
    }
    request_result = API_CLIENT.do_request(
        path="/api/v2/notes/retrieveNotes",
        json=notes_search,
        request_timeout=Timeout(web_timeout_long),
    )
    if not request_result:
        return []
    try:
        return loads(request_result.data.decode("utf-8"))["records"]
    except KeyError:
        return []


