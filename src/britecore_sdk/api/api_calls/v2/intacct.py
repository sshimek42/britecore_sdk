"""BriteCore v2 Intacct API endpoint wrappers.

This module provides wrappers for Intacct export and posting workflows in the
BriteCore v2 integration surface.
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


def _build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send an intacct request and normalize the response."""
    LOGGER.debug("Calling intacct endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def get_intacct_vendor_info(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Intacct vendor information.

    This wrapper calls ``/api/v2/intacct/get_intacct_vendor_info`` and returns
    the normalized ``process_result(...)`` payload for the configured Intacct
    vendor integration. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post("/api/v2/intacct/get_intacct_vendor_info", {}, **kwargs)


def get_unexported_claim_transactions_xml(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve unexported claim transactions in XML form.

    This wrapper calls ``/api/v2/intacct/get_unexported_claim_transactions_xml``
    and returns the normalized ``process_result(...)`` payload for claim
    transactions awaiting export. ``**kwargs`` accepts ``RequestParameters``
    overrides.
    """
    return _post("/api/v2/intacct/get_unexported_claim_transactions_xml", {}, **kwargs)


def get_unexported_return_premiums_xml(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve unexported return premiums in XML form.

    This wrapper calls ``/api/v2/intacct/get_unexported_return_premiums_xml``
    and returns the normalized ``process_result(...)`` payload for return
    premiums awaiting export. ``**kwargs`` accepts ``RequestParameters``
    overrides.
    """
    return _post("/api/v2/intacct/get_unexported_return_premiums_xml", {}, **kwargs)


def post_claim_transactions(
    payload: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Post claim transactions to Intacct.

    This wrapper sends ``payload`` to ``/api/v2/intacct/post_claim_transactions``
    and returns the normalized ``process_result(...)`` payload for the posting
    operation. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/intacct/post_claim_transactions",
        _build_payload(payload=payload),
        **kwargs,
    )


def post_return_premiums(
    payload: dict | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Post return premiums to Intacct.

    This wrapper sends ``payload`` to ``/api/v2/intacct/post_return_premiums``
    and returns the normalized ``process_result(...)`` payload for the posting
    operation. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/intacct/post_return_premiums",
        _build_payload(payload=payload),
        **kwargs,
    )


__all__ = [
    "get_intacct_vendor_info",
    "get_unexported_claim_transactions_xml",
    "get_unexported_return_premiums_xml",
    "post_claim_transactions",
    "post_return_premiums",
]
