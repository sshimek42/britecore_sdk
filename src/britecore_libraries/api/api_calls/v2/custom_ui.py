"""BriteCore v1 Custom UI API endpoint wrappers.

Provides:
    createurloverride    -- Create a URL override entry.
    deleteurloverride    -- Delete an existing URL override entry.
    retrieveurloverrides -- Retrieve all URL overrides.
    updateurloverride    -- Update an existing URL override entry.
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
    """Send a custom_ui request and normalize the response."""
    LOGGER.debug("Calling custom_ui endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def createurloverride(
    json_obj: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a new URL override entry.

    Parameters
    ----------
    json_obj : dict, optional
        Object containing the URL override configuration to create.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the created override.
    """
    return _post(
        "/api/v1/custom_ui/createURLOverride",
        _build_payload(json_obj=json_obj),
        **kwargs,
    )


def deleteurloverride(
    json_obj: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete an existing URL override entry.

    Parameters
    ----------
    json_obj : dict, optional
        Object containing identifying information for the override to delete.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming deletion.
    """
    return _post(
        "/api/v1/custom_ui/deleteURLOverride",
        _build_payload(json_obj=json_obj),
        **kwargs,
    )


def retrieveurloverrides(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve all configured URL overrides.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the list of URL overrides.
    """
    return _post("/api/v1/custom_ui/retrieveURLOverrides", {}, **kwargs)


def updateurloverride(
    json_obj: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update an existing URL override entry.

    Parameters
    ----------
    json_obj : dict, optional
        Object containing updated URL override data.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the update.
    """
    return _post(
        "/api/v1/custom_ui/updateURLOverride",
        _build_payload(json_obj=json_obj),
        **kwargs,
    )


__all__ = [
    "createurloverride",
    "deleteurloverride",
    "retrieveurloverrides",
    "updateurloverride",
]
