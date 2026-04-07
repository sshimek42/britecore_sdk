"""BriteCore v1 Printing API endpoint wrappers."""

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
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def getattachment(
    json_dict: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return _post(
        "/api/v1/printing/getAttachment",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def gettobeprinted(
    json_dict: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return _post(
        "/api/v1/printing/getToBePrinted",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def markasprinted(
    json_dict: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return _post(
        "/api/v1/printing/markAsPrinted",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def sendprinthawk(
    json_dict: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return _post(
        "/api/v1/printing/sendPrintHawk",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def sendprinthawkemail(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return _post("/api/v1/printing/sendPrintHawkEmail", {}, **kwargs)


# Backwards-compatible helper names from prior v1 module.
def get_to_be_printed(
    from_date: str,
    to_date: str,
    ignore_state: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return gettobeprinted(
        json_dict={"from_date": from_date, "to_date": to_date, "ignore_state": ignore_state},
        **kwargs,
    )


def mark_as_printed(file_ids: list[str], **kwargs: Unpack[RequestParameters]) -> Any:
    return markasprinted(json_dict={"file_ids": file_ids}, **kwargs)


__all__ = [
    "get_to_be_printed",
    "getattachment",
    "gettobeprinted",
    "mark_as_printed",
    "markasprinted",
    "sendprinthawk",
    "sendprinthawkemail",
]
