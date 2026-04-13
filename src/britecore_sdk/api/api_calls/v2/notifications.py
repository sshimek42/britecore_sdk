"""BriteCore v2 Notifications API endpoint wrappers.

This module provides wrappers for acknowledging notifications and retrieving
the current unacknowledged notification list.
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


def post(
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
    """Acknowledge the caller's current notifications.

    This wrapper calls ``/api/v2/notifications/acknowledge`` and returns the
    normalized ``process_result(...)`` payload confirming acknowledgement.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post("/api/v2/notifications/acknowledge", {}, **kwargs)


def current(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the current unacknowledged notifications.

    This wrapper calls ``/api/v2/notifications/current`` and returns the
    normalized ``process_result(...)`` payload for the active notification set.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return post("/api/v2/notifications/current", {}, **kwargs)


__all__ = [
    "acknowledge",
    "current",
]
