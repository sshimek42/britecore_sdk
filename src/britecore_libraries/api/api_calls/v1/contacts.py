from json import loads
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


def retrieve_contact_list(
    search_str: str,
    search_filter: str = "Named Insured",
    current_page: Optional[str] = "1",
    page_size: Optional[str] = "10",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieve named insured contacts
    :param search_str: Name to search for
    :type search_str: str
    :param search_filter: Role to search for (Default: 'Named Insured')
    :type search_filter: str
    :param current_page: Starting Search Page (Default: '1')
    :type current_page: Optional[str]
    :param page_size: Search Page Size (Default: '10')
    :type page_size: Optional[str]
    :param kwargs: urllib3 keywords to pass for request
    :type kwargs: Optional[dict[str,Any]]
    :return: Search results
    :rtype: Any
    """
    contact_request_json: dict[str, str] = {
        "searchString": search_str,
        "filter": search_filter,
        "currentPage": current_page,
        "pageSize": page_size,
    }

    LOGGER.debug("Getting search results")

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v1/contacts/retrieveContactList",
        json=contact_request_json,
        **kwargs,
    )

    contact_json: Any = loads(request_result.data.decode("utf-8"))

    return contact_json["records"]
