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
from britecore_libraries.models.contact import ROLETYPES

LOGGER: Logger = logger
API_CLIENT: BritecoreAPIClient = api_client


def retrieve_contact_list(
    search_str: str,
    search_filter: Optional[ROLETYPES] = "Named Insured",
    current_page: Optional[str] = "1",
    page_size: Optional[str] = "10",
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieve a list of contacts based on search criteria.

    This function performs a contact search operation using the provided
    search string and optional filters. It constructs a request payload with
    the specified parameters and sends it to the API endpoint for contact
    retrieval.

    Parameters:
        search_str: The string to search for in contact records
        search_filter: The filter type to apply to the search (default: "Named Insured")
        current_page: The page number to retrieve (default: "1")
        page_size: The number of records per page (default: "10")
        **kwargs: Additional request parameters to pass to the API client

    Returns:
        A list of contact records matching the search criteria

    Raises:
        Any exceptions raised by the underlying API client or HTTP request
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
