"""BriteCore v2 Claims API endpoint wrappers.

This module provides the SDK wrapper for retrieving claim details from the
BriteCore v2 claims API.
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


def get_claim(claim_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve claim details by claim identifier.

    This wrapper sends ``claim_id`` to ``/api/v2/claims/get_claim`` and
    returns the normalized ``process_result(...)`` payload for the matching
    claim record. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Getting claim information")
    claim_search: dict[str, str] = {"claim_id": claim_id}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/claims/get_claim", json=claim_search, **kwargs
    )
    return API_CLIENT.process_result(request_result)
