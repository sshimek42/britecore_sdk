"""BriteCore v2 Claims API endpoint wrappers.

This module provides the SDK wrapper for retrieving claim details from the
BriteCore v2 claims API.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.api.api_calls.v2._common import build_payload
from britecore_sdk.api.api_calls.v2._common import post as common_post

API_CLIENT: BritecoreAPIClient = api_client


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return common_post(path, payload, client=API_CLIENT, **kwargs)


def get_claim(claim_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve claim details by claim identifier.

    This wrapper sends ``claim_id`` to ``/api/v2/claims/get_claim`` and
    returns the normalized ``process_result(...)`` payload for the matching
    claim record. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/claims/get_claim",
        build_payload(claim_id=claim_id),
        **kwargs,
    )


def export_claim_payments(
    claim_ids: list[str] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Export claim payments for one or more claim identifiers."""
    return _post(
        "/api/v2/claims/export_claim_payments",
        build_payload(claim_ids=claim_ids),
        **kwargs,
    )


def get_all_catastrophes(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve all catastrophe records available to the claims domain."""
    return _post("/api/v2/claims/get_all_catastrophes", **kwargs)


def get_all_perils(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve all peril records available to the claims domain."""
    return _post("/api/v2/claims/get_all_perils", **kwargs)


def get_claim_contacts(
    claim_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve contacts associated with a claim."""
    return _post(
        "/api/v2/claims/get_claim_contacts",
        build_payload(claim_id=claim_id),
        **kwargs,
    )


def get_claim_payments(
    claim_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve payment records associated with a claim."""
    return _post(
        "/api/v2/claims/get_claim_payments",
        build_payload(claim_id=claim_id),
        **kwargs,
    )


def update_claim(
    claim_id: str | None = None,
    claim: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update claim fields for the provided claim identifier."""
    return _post(
        "/api/v2/claims/update_claim",
        build_payload(claim_id=claim_id, claim=claim),
        **kwargs,
    )


__all__ = [
    "export_claim_payments",
    "get_all_catastrophes",
    "get_all_perils",
    "get_claim",
    "get_claim_contacts",
    "get_claim_payments",
    "update_claim",
]
