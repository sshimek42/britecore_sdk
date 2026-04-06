"""BriteCore v2 Insured API endpoint wrappers.

Provides:
    get_property_information_and_photos -- Retrieve comprehensive property
                                           details and associated photos.
"""

from logging import Logger
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger
API_CLIENT: BritecoreAPIClient = api_client


def get_property_information_and_photos(
    property_id: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """
    Retrieve comprehensive property information and associated photos using the specified property ID.

    This function makes a request to the API endpoint to fetch detailed information about a property
    including photos. It handles the API communication and result processing.

    Parameters:
        property_id (str): Unique identifier for the property to retrieve information for
        **kwargs: Additional keyword arguments to pass to the underlying HTTP request

    Returns:
        Any: The processed API response containing property information and photos

    Raises:
        Any exceptions raised by the underlying API client or HTTP request handling

    Note:
        The function uses a global API client instance to make the request and processes the
        result before returning it to the caller
    """
    LOGGER.debug(f"Getting property information for property_id '{property_id}'")
    property_json: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/insured/get_property_information_and_photos",
        json={"property_id": property_id},
        **kwargs,
    )
    property_json = API_CLIENT.process_result(property_json)

    return property_json
