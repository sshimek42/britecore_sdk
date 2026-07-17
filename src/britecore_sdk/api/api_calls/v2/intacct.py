"""BriteCore v2 Intacct API endpoint wrappers.

This module provides wrappers for Intacct export and posting workflows in the
BriteCore v2 integration surface.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


def get_intacct_vendor_info(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve Intacct vendor information."""
    return post("/api/v2/intacct/get_intacct_vendor_info", {}, **kwargs)


def get_unexported_claim_transactions_xml(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve unexported claim transactions in XML form."""
    return post("/api/v2/intacct/get_unexported_claim_transactions_xml", {}, **kwargs)


def get_unexported_return_premiums_xml(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve unexported return premiums in XML form."""
    return post("/api/v2/intacct/get_unexported_return_premiums_xml", {}, **kwargs)


def post_claim_transactions(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Post claim transactions to Intacct."""
    return post(
        "/api/v2/intacct/post_claim_transactions",
        build_payload(payload=payload),
        **kwargs,
    )


def post_return_premiums(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Post return premiums to Intacct."""
    return post(
        "/api/v2/intacct/post_return_premiums",
        build_payload(payload=payload),
        **kwargs,
    )


__all__ = [
    "get_intacct_vendor_info",
    "get_unexported_claim_transactions_xml",
    "get_unexported_return_premiums_xml",
    "post_claim_transactions",
    "post_return_premiums",
]
