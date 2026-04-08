"""BriteCore v2 Utils API endpoint wrappers.

Provides administrative and system-utility helpers that don't belong to a
specific business domain.
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


def get_available_function_names(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve available utility function names.

    This wrapper calls ``/api/v2/utils/get_available_function_names`` and
    returns the normalized ``process_result(...)`` payload containing available
    function names. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Retrieving functions")
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/utils/get_available_function_names",
        **kwargs,
    )

    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/utils/get_available_function_names"
    )


def rebuild_search_index(
    only_build: list,
    **kwargs: Unpack[RequestParameters],
) -> bool:
    """Rebuild all or part of the search index.

    This wrapper sends ``only_build`` to ``/api/v2/utils/rebuild_search_index``
    and returns the normalized ``process_result(...)`` payload for the rebuild
    request. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    LOGGER.debug("Rebuilding index")
    rebuild_index: dict[str, Any] = {"only_build": only_build}
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/utils/rebuild_search_index",
        json=rebuild_index,
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/utils/rebuild_search_index"
    )
