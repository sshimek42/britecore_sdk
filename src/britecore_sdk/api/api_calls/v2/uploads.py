"""BriteCore v2 Uploads API endpoint wrappers.

This module provides the SDK wrapper for associating uploaded files with policy
records through the BriteCore v2 uploads API.
"""

from logging import Logger
from typing import Any, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk import logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send an uploads request and normalize the response."""
    LOGGER.debug("Calling uploads endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def attach_file_to_policy(
    payload: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Attach an uploaded file to a policy record.

    This wrapper sends ``payload`` to ``/api/v2/uploads/attach_file_to_policy``
    and returns the normalized ``process_result(...)`` payload for the
    attachment request. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post(
        "/api/v2/uploads/attach_file_to_policy",
        build_payload(payload=payload),
        **kwargs,
    )


__all__ = [
    "attach_file_to_policy",
]
