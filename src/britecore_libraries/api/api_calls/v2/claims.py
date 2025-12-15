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
    Retrieve policy claim information
    :param claim_id: Claim number to search for
    :type claim_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Claim information
    :rtype: Any
    """
    LOGGER.debug("Getting claim information")
    claim_search: dict[str, str] = {"claim_id": claim_id}
    request_result: Optional[BaseHTTPResponse, HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/claims/get_claim", json=claim_search, **kwargs
    )
    return API_CLIENT.process_result(request_result)
