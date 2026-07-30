"""BriteCore v2 Insured API endpoint wrappers.

This module provides the SDK wrapper for retrieving property information and
associated photos from the BriteCore v2 insured API.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.api.api_calls.v2._common import build_payload

API_CLIENT: BritecoreAPIClient = api_client


def get_property_information_and_photos(
    property_id: str, **kwargs: Unpack[RequestParameters]
) -> Any:
    """Retrieve property information and associated photos.

    POST /api/v2/insured/get_property_information_and_photos
    """
    request_json = build_payload(property_id=property_id)
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/get_property_information_and_photos",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/get_property_information_and_photos",
    )


def new_claim_information(
    property_id: str,
    policy_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve claim starter information for a property/policy pair."""
    request_json = build_payload(property_id=property_id, policy_id=policy_id)
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/new_claim_information",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/new_claim_information",
    )


def set_photo_as_insurred_preferred(
    file_id: str,
    reference_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Mark an uploaded photo as the preferred insured photo."""
    request_json = build_payload(file_id=file_id, reference_id=reference_id)
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/set_photo_as_insurred_preferred",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/set_photo_as_insurred_preferred",
    )


def update_claim(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update claim details for an insured workflow."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/update_claim",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/update_claim",
    )


def get_primary_carrier(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the primary carrier metadata."""
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/get_primary_carrier",
        json={},
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/get_primary_carrier",
    )


def retrieve_contact_information(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve insured contact information."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/retrieve_contact_information",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/retrieve_contact_information",
    )


def change_billing_schedule(
    policy_id: str,
    billing_schedule_id: str,
    policy_term_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Change an insured's billing schedule selection."""
    request_json = build_payload(
        policy_id=policy_id,
        billing_schedule_id=billing_schedule_id,
        policy_term_id=policy_term_id,
    )
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/change_billing_schedule",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/change_billing_schedule",
    )


def set_file_metadata(
    file_id: str,
    metadata: dict[str, Any],
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update metadata for an insured file record."""
    request_json = build_payload(file_id=file_id, metadata=metadata)
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/set_file_metadata",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/set_file_metadata",
    )


def update_contact_information(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update insured contact information."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/update_contact_information",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/update_contact_information",
    )


def set_photo_caption(
    file_id: str,
    caption: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Set or update a caption for an insured photo."""
    request_json = build_payload(file_id=file_id, caption=caption)
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/set_photo_caption",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/set_photo_caption",
    )


def get_complete_contact_information(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve complete insured contact details."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/get_complete_contact_information",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/get_complete_contact_information",
    )


def upload_property_or_claim_photo(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a property or claim photo."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/upload_property_or_claim_photo",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/upload_property_or_claim_photo",
    )


def get_agent_and_agencies_from_contact(
    contact_id: str,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve agent and agency records for a contact."""
    request_json = build_payload(contact_id=contact_id)
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/get_agent_and_agencies_from_contact",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/get_agent_and_agencies_from_contact",
    )


def submit_claim(claim_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Submit a claim for processing."""
    request_json = build_payload(claim_id=claim_id)
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/submit_claim",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/submit_claim",
    )


def is_email_available(
    email: str,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Check whether an email address is available for use."""
    request_json = build_payload(email=email, contact_id=contact_id)
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/is_email_available",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/is_email_available",
    )


def update_contact_email_notices_flag(
    contact_id: str,
    enabled: bool,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Update the insured contact email-notices preference flag."""
    request_json = build_payload(contact_id=contact_id, enabled=enabled)
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/update_contact_email_notices_flag",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/update_contact_email_notices_flag",
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

# --- Autogenerated spec wrappers ---


def find_similar_contact(
    contact_ids_to_check: list[str] | None = None,
    ssn_only_check: bool | None = None,
    contact_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Find Similar Contact.

    POST /api/v2/insured/find_similar_contact
    """
    request_json: dict[str, Any] = {
        "contact_ids_to_check": contact_ids_to_check,
        "ssn_only_check": ssn_only_check,
        "contact_id": contact_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/find_similar_contact",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/insured/find_similar_contact"
    )


def get_contacts_with_insured_portal_user_role(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Get Contacts With Insured Portal User Role.

    POST /api/v2/insured/get_contacts_with_insured_portal_user_role
    """
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/insured/get_contacts_with_insured_portal_user_role",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/insured/get_contacts_with_insured_portal_user_role",
    )


__all__.extend(
    [
        "find_similar_contact",
        "get_contacts_with_insured_portal_user_role",
    ]
)
