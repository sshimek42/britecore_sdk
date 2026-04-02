"""BriteCore v2 Claims API endpoint wrappers.

Provides:
    get_claim  -- Retrieve detailed claim information by claim ID.
"""

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


def get_claim(claim_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve claim information by claim ID.

    This function fetches detailed information about a specific claim using the
    provided claim ID. It constructs a search query and sends a request to the
    API endpoint to retrieve the claim data.

    Parameters:
        claim_id (str): The unique identifier of the claim to retrieve
        **kwargs (Unpack[RequestParameters]): Additional request parameters
            that will be passed to the API client

    Returns:
        Any: The processed claim information returned by the API

    Raises:
        Any exceptions raised by the underlying API client or request processing mechanisms

    Note:
        This function uses a debug logger to trace execution and relies on
            API_CLIENT for actual request handling and result processing
    """
    LOGGER.debug("Getting claim information")
    claim_search: dict[str, str] = {"claim_id": claim_id}
    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/claims/get_claim", json=claim_search, **kwargs
    )
    return API_CLIENT.process_result(request_result)
