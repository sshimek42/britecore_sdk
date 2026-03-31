"""BriteCore v2 Search API endpoint wrappers.

Provides:
    add_to_index       -- Add a document to a search index.
    remove_from_index  -- Remove a document from a search index.
"""
from logging import Logger
from typing import Any, Optional, Unpack, cast

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
    payload: Optional[dict[str, Any]] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a search request and normalize the response."""
    LOGGER.debug("Calling search endpoint %s", path)
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def add_to_index(
    document: Optional[dict] = None,
    id: Optional[str] = None,
    index_name: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Add a document to a search index.

    Parameters
    ----------
    document : dict, optional
        The document object to index.
    id : str, optional
        Unique identifier for the document in the index.
    index_name : str, optional
        Name of the search index to add the document to.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the document was indexed.
    """
    return _post(
        "/api/v2/search/add_to_index",
        _build_payload(document=document, id=id, index_name=index_name),
        **kwargs,
    )


def remove_from_index(
    id: Optional[str] = None,
    index_name: Optional[str] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Remove a document from a search index.

    Parameters
    ----------
    id : str, optional
        Unique identifier of the document to remove.
    index_name : str, optional
        Name of the search index to remove the document from.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the document was removed.
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
