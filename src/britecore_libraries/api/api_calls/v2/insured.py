"""BriteCore v2 Insured API endpoint wrappers.

This module provides the SDK wrapper for retrieving property information and
associated photos from the BriteCore v2 insured API.
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
    """Retrieve property information and associated photos.

    This wrapper sends ``property_id`` to
    ``/api/v2/insured/get_property_information_and_photos`` and returns the
    normalized ``process_result(...)`` payload for the matching property.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Getting property information for property_id '%s'", property_id)
    property_json: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/insured/get_property_information_and_photos",
        json={"property_id": property_id},
        **kwargs,
    )
    property_json = API_CLIENT.process_result(property_json)

    return property_json
