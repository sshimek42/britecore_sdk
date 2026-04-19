"""BriteCore v2 Insured API endpoint wrappers.

This module provides the SDK wrapper for retrieving property information and
associated photos from the BriteCore v2 insured API.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import BritecoreAPIClient, RequestParameters, api_client
from britecore_sdk.api.api_calls.v2._common import build_payload, post as common_post

API_CLIENT: BritecoreAPIClient = api_client


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return common_post(path, payload, client=API_CLIENT, **kwargs)


def get_property_information_and_photos(
    property_id: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve property information and associated photos.

    This wrapper sends ``property_id`` to
    ``/api/v2/insured/get_property_information_and_photos`` and returns the
    normalized ``process_result(...)`` payload for the matching property.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/insured/get_property_information_and_photos",
        build_payload(property_id=property_id),
        include_endpoint=True,
        **kwargs,
    )


def new_claim_information(
    property_id: str,
    policy_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve claim starter information for a property/policy pair."""
    return _post(
        "/api/v2/insured/new_claim_information",
        build_payload(property_id=property_id, policy_id=policy_id),
        include_endpoint=True,
        **kwargs,
    )


def set_photo_as_insurred_preferred(
    file_id: str,
    reference_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Mark an uploaded photo as the preferred insured photo."""
    return _post(
        "/api/v2/insured/set_photo_as_insurred_preferred",
        build_payload(file_id=file_id, reference_id=reference_id),
        include_endpoint=True,
        **kwargs,
    )


def update_claim(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update claim details for an insured workflow."""
    return _post(
        "/api/v2/insured/update_claim",
        payload,
        include_endpoint=True,
        **kwargs,
    )


def get_primary_carrier(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the primary carrier metadata."""
    return _post(
        "/api/v2/insured/get_primary_carrier", include_endpoint=True, **kwargs
    )


def retrieve_contact_information(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve insured contact information."""
    return _post(
        "/api/v2/insured/retrieve_contact_information",
        payload,
        include_endpoint=True,
        **kwargs,
    )


def change_billing_schedule(
    policy_id: str,
    billing_schedule_id: str,
    policy_term_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Change an insured's billing schedule selection."""
    return _post(
        "/api/v2/insured/change_billing_schedule",
        build_payload(
            policy_id=policy_id,
            billing_schedule_id=billing_schedule_id,
            policy_term_id=policy_term_id,
        ),
        include_endpoint=True,
        **kwargs,
    )


def set_file_metadata(
    file_id: str,
    metadata: dict[str, Any],
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update metadata for an insured file record."""
    return _post(
        "/api/v2/insured/set_file_metadata",
        build_payload(file_id=file_id, metadata=metadata),
        include_endpoint=True,
        **kwargs,
    )


def update_contact_information(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update insured contact information."""
    return _post(
        "/api/v2/insured/update_contact_information",
        payload,
        include_endpoint=True,
        **kwargs,
    )


def set_photo_caption(
    file_id: str,
    caption: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set or update a caption for an insured photo."""
    return _post(
        "/api/v2/insured/set_photo_caption",
        build_payload(file_id=file_id, caption=caption),
        include_endpoint=True,
        **kwargs,
    )


def get_complete_contact_information(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve complete insured contact details."""
    return _post(
        "/api/v2/insured/get_complete_contact_information",
        payload,
        include_endpoint=True,
        **kwargs,
    )


def upload_property_or_claim_photo(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a property or claim photo."""
    return _post(
        "/api/v2/insured/upload_property_or_claim_photo",
        payload,
        include_endpoint=True,
        **kwargs,
    )


def get_agent_and_agencies_from_contact(
    contact_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve agent and agency records for a contact."""
    return _post(
        "/api/v2/insured/get_agent_and_agencies_from_contact",
        build_payload(contact_id=contact_id),
        include_endpoint=True,
        **kwargs,
    )


def submit_claim(claim_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Submit a claim for processing."""
    return _post(
        "/api/v2/insured/submit_claim",
        build_payload(claim_id=claim_id),
        include_endpoint=True,
        **kwargs,
    )


def is_email_available(
    email: str,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check whether an email address is available for use."""
    return _post(
        "/api/v2/insured/is_email_available",
        build_payload(email=email, contact_id=contact_id),
        include_endpoint=True,
        **kwargs,
    )


def update_contact_email_notices_flag(
    contact_id: str,
    enabled: bool,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update the insured contact email-notices preference flag."""
    return _post(
        "/api/v2/insured/update_contact_email_notices_flag",
        build_payload(contact_id=contact_id, enabled=enabled),
        include_endpoint=True,
        **kwargs,
    )


__all__ = [
    "change_billing_schedule",
    "get_agent_and_agencies_from_contact",
    "get_complete_contact_information",
    "get_primary_carrier",
    "get_property_information_and_photos",
    "is_email_available",
    "new_claim_information",
    "retrieve_contact_information",
    "set_file_metadata",
    "set_photo_as_insurred_preferred",
    "set_photo_caption",
    "submit_claim",
    "update_claim",
    "update_contact_email_notices_flag",
    "update_contact_information",
    "upload_property_or_claim_photo",
]
