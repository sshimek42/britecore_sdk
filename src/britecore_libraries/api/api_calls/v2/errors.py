"""BriteCore v2 Errors API endpoint wrappers.

Provides:
    get_internal_error  -- Retrieve details for an internal error by ID.
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
    """Send an errors request and normalize the response."""
    LOGGER.debug("Calling errors endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def get_internal_error(
    internal_error_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve details for an internal error record.

    Parameters
    ----------
    internal_error_id : str, optional
        UUID of the internal error to retrieve.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing internal error details.
    """
    return _post(
        "/api/v2/errors/get_internal_error",
        _build_payload(internal_error_id=internal_error_id),
        **kwargs,
    )


__all__ = [
    "get_internal_error",
]
