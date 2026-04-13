"""BriteCore v2 Search API endpoint wrappers.

This module provides wrappers for adding and removing documents from the
BriteCore v2 search index.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


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
    return post(
        "/api/v2/search/add_to_index",
        build_payload(document=document, id=id, index_name=index_name),
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
    return post(
        "/api/v2/search/remove_from_index",
        build_payload(id=id, index_name=index_name),
        **kwargs,
    )


__all__ = [
    "add_to_index",
    "remove_from_index",
]
