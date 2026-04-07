"""BriteCore v1 Payments API endpoint wrappers."""

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


def makemanualpolicypayment(
    json_dict: dict[str, Any],
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return _post(
        "/api/v1/payments/makeManualPolicyPayment",
        _build_payload(json_dict=json_dict),
        **kwargs,
    )


def make_manual_policy_payment(
    json_dict: dict[str, Any],
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return makemanualpolicypayment(json_dict=json_dict, **kwargs)


__all__ = ["make_manual_policy_payment", "makemanualpolicypayment"]
