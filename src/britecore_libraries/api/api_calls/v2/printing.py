"""BriteCore v1 Printing API endpoint wrappers.

Provides:
    getattachment       -- Retrieve a print attachment by descriptor.
    gettobeprinted      -- Retrieve items queued to be printed.
    markasprinted       -- Mark queued items as printed.
    sendprinthawk       -- Send a document to PrintHawk.
    sendprinthawkemail  -- Send a PrintHawk email notification.
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
    """Send a printing request and normalize the response."""
    LOGGER.debug("Calling printing endpoint %s", path)
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def getattachment(
    json_dict: Optional[dict] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve a print attachment.

    Parameters
    ----------
    json_dict : dict, optional
        Dictionary containing attachment descriptor fields.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the attachment data.
    """
    return _post(
        "/api/v1/printing/getAttachment",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def gettobeprinted(
    json_dict: Optional[dict] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve the list of items queued to be printed.

    Parameters
    ----------
    json_dict : dict, optional
        Dictionary containing filter or query fields.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing items pending print.
    """
    return _post(
        "/api/v1/printing/getToBePrinted",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def markasprinted(
    json_dict: Optional[dict] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Mark queued print items as printed.

    Parameters
    ----------
    json_dict : dict, optional
        Dictionary identifying the items to mark as printed.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the update.
    """
    return _post(
        "/api/v1/printing/markAsPrinted",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def sendprinthawk(
    json_dict: Optional[dict] = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a document to the PrintHawk service.

    Parameters
    ----------
    json_dict : dict, optional
        Dictionary containing the PrintHawk document descriptor.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response from PrintHawk.
    """
    return _post(
        "/api/v1/printing/sendPrintHawk",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def sendprinthawkemail(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a PrintHawk email notification.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response confirming the email was sent.
    """
    return _post("/api/v1/printing/sendPrintHawkEmail", {}, **kwargs)


__all__ = [
    "getattachment",
    "gettobeprinted",
    "markasprinted",
    "sendprinthawk",
    "sendprinthawkemail",
]
