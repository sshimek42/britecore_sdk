"""BriteCore v2 Uploads API endpoint wrappers.

Provides:
    attach_file_to_policy  -- Attach an uploaded file to a policy.
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
    """Send an uploads request and normalize the response."""
    LOGGER.debug("Calling uploads endpoint %s", path)
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def attach_file_to_policy(
    payload: Optional[dict] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Attach an uploaded file to a policy.

    Parameters
    ----------
    payload : dict, optional
        Object containing the file attachment details (e.g. file ID, policy ID,
        document type, and any additional metadata).
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the attachment.
    """
    return _post(
        "/api/v2/uploads/attach_file_to_policy",
        _build_payload(payload=payload),
        **kwargs,
    )


__all__ = [
    "attach_file_to_policy",
]
