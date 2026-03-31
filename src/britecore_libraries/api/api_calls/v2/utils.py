"""BriteCore v2 Utils API endpoint wrappers.

Provides administrative and system-utility helpers that don't belong to a
specific business domain.
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


def get_available_function_names(**kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve available function names from the API.

    This function makes a request to the API endpoint to fetch the list of
    available function names that can be used with the system.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Additional keyword arguments to pass to the API request.
        These parameters are unpacked from a RequestParameters type.

    Returns
    -------
    Any
        The processed result from the API request, typically containing
        the list of available function names.

    Raises
    ------
    Any exceptions raised by the underlying API client or HTTP request
    mechanism are propagated as-is.

    Notes
    -----
    This function uses the global API_CLIENT instance to make the request
    and processes the result through the API client's process_result method.
    The request is made to the /api/v2/utils/get_available_function_names
    endpoint.
    """
    LOGGER.debug("Retrieving functions")
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/utils/get_available_function_names",
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)


def rebuild_search_index(only_build: list, **kwargs) -> bool:
    """
    Rebuilds the search index for specified build components.

    This function initiates a search index rebuild operation for the specified
    build components by making an API request to the backend service.

    Parameters:
        only_build: List of build identifiers to include in the rebuild process
        **kwargs: Additional keyword arguments to pass to the API client request

    Returns:
        Boolean indicating whether the rebuild operation was successful

    Raises:
        Any exceptions raised by the underlying API client or HTTP request handling
    """
    LOGGER.debug("Rebuilding index")
    rebuild_index: dict[str, Any] = {"only_build": only_build}
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/utils/rebuild_search_index",
        json=rebuild_index,
        **kwargs,
    )
    return API_CLIENT.process_result(request_result)
