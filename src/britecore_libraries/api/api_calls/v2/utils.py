from logging import Logger

from typing import Unpack, Optional, Any

from britecore_libraries.api.api_calls import api_client, BritecoreAPIClient, RequestParameters
from britecore_libraries import logger

from urllib3 import BaseHTTPResponse, HTTPResponse

LOGGER: Logger = logger
API_CLIENT: BritecoreAPIClient = api_client

def get_available_function_names(**kwargs:Unpack[RequestParameters]) -> Any:
    """
    Get available functions
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Functions
    :rtype: Any
    """
    LOGGER.debug("Retrieving functions")
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/utils/get_available_function_names",
        **kwargs,
    )

    return API_CLIENT.process_result(request_result)

def rebuild_search_index(only_build: list, **kwargs) -> bool:
    """
    Rebuild BriteCore search indexes
    :param only_build:
    :type only_build: list
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Result
    :rtype: bool
    """
    LOGGER.debug("Rebuilding index")
    rebuild_index: dict[str,Any] = {"only_build": only_build}
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/utils/rebuild_search_index",
        json=rebuild_index,
        **kwargs,
    )
    return API_CLIENT.process_result(request_result)
