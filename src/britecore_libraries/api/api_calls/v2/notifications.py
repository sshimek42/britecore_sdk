"""BriteCore v2 Notifications API endpoint wrappers.

Provides:
    acknowledge  -- Acknowledge one or more notifications.
    current      -- Retrieve current (unacknowledged) notifications.
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


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a notifications request and normalize the response."""
    LOGGER.debug("Calling notifications endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def acknowledge(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Acknowledge pending notifications.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming acknowledgement.
    """
    return _post("/api/v2/notifications/acknowledge", {}, **kwargs)


def current(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the current (unacknowledged) notifications.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the current notifications.
    """
    return _post("/api/v2/notifications/current", {}, **kwargs)


__all__ = [
    "acknowledge",
    "current",
]
