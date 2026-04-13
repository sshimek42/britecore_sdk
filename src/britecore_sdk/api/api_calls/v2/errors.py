"""BriteCore v2 Errors API endpoint wrappers.

This module exposes the SDK wrapper for retrieving internal error records from
the BriteCore v2 errors API.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


def get_internal_error(
    internal_error_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve an internal error record by identifier.

    This wrapper sends ``internal_error_id`` to
    ``/api/v2/errors/get_internal_error`` and returns the normalized
    ``process_result(...)`` payload for the matching error record.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post(
        "/api/v2/errors/get_internal_error",
        build_payload(internal_error_id=internal_error_id),
        **kwargs,
    )


__all__ = [
    "get_internal_error",
]
