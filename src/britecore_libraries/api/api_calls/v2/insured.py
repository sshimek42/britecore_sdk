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


def get_property_information_and_photos(
    property_id: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """
    Retrieve a single property and return data needed to add item to policy
    :param property_id:Property ID
    :type: property_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Property data
    :rtype: Any
    """
    LOGGER.debug(
        f"Getting property information for property_id %f.yellow%{property_id}%f%"
    )
    property_json: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/insured/get_property_information_and_photos",
        json={"property_id": property_id},
        **kwargs,
    )
    property_json = API_CLIENT.process_result(property_json)

    return property_json
