"""BriteCore v2 Quotes API endpoint wrappers.

Provides:
    create_full_quote  -- Create a new full quote from a JSON payload.
    get_quote          -- Retrieve an existing quote by ID.
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


def create_full_quote(
    quote_json: dict[str, Any], **kwargs: Unpack[RequestParameters]
) -> tuple[dict[str, Any] | None, str | None]:
    """
    Create a full quote from the provided quote JSON data.

    This function sends a request to create a full quote using the API client
    and processes the response to extract relevant information including
    the quote ID.

    Parameters
    ----------
    quote_json : dict[str, Any]
        Dictionary containing the quote data to be processed
    **kwargs : Unpack[RequestParameters]
        Additional keyword arguments to be passed to the API request

    Returns
    -------
    tuple[dict[str, Any] | None, str | None]
        A tuple containing:
        - The processed quote information as a dictionary, or None if
          processing fails
        - The quote ID as a string, or None if no ID is available
    """
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/quotes/create_full_quote", json=quote_json, **kwargs
    )

    json_info: Any = API_CLIENT.process_result(request_result)

    if not json_info:
        return None, None

    return json_info, json_info["id"]


def get_quote(id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve a quote by its unique identifier.

    This function fetches a quote from the API using the provided quote ID. It constructs
    a request with the necessary parameters and processes the response to return the quote data.

    Parameters:
        id (str): The unique identifier of the quote to retrieve
        **kwargs (Unpack[RequestParameters]): Additional keyword arguments to pass to the
            underlying API request, such as headers, timeout settings, or authentication
            parameters

    Returns:
        Any: The quote data returned by the API, typically a dictionary or similar
            data structure containing the quote information

    Note:
        This function uses a global API client and logger, which must be properly
        configured before calling this function. The function will log debug information
        about the quote retrieval process.
    """
    quote_json: dict[str, str] = {"id": id}

    LOGGER.debug("Getting quote")

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/quotes/get_quote", json=quote_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)
