"""BriteCore v2 Search API endpoint wrappers.

This module provides wrappers for adding and removing documents from the
BriteCore v2 search index.
"""

from logging import Logger
from typing import Any, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def _build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a search request and normalize the response."""
    LOGGER.debug("Calling search endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def add_to_index(
    document: dict | None = None,
    id: str | None = None,
    index_name: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add a document to a search index.

    This wrapper sends ``document``, ``id``, and ``index_name`` to
    ``/api/v2/search/add_to_index`` and returns the normalized
    ``process_result(...)`` payload for the indexing request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/search/add_to_index",
        _build_payload(document=document, id=id, index_name=index_name),
        **kwargs,
    )


def remove_from_index(
    id: str | None = None,
    index_name: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove a document from a search index.

    This wrapper sends ``id`` and ``index_name`` to
    ``/api/v2/search/remove_from_index`` and returns the normalized
    ``process_result(...)`` payload for the removal request. ``**kwargs``
    accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/search/remove_from_index",
        _build_payload(id=id, index_name=index_name),
        **kwargs,
    )


__all__ = [
    "add_to_index",
    "remove_from_index",
]
