"""Claim payload mappers."""

from typing import Any

from britecore_sdk.models import BritecoreContact

NAMED_INSURED_ROLE = "named_insured"


def to_named_insured_payload(
    contact: BritecoreContact | dict[str, Any],
) -> dict[str, Any]:
    """Convert contact data to a claim-compatible named insured payload."""
    payload: dict[str, Any]
    if isinstance(contact, BritecoreContact):
        payload = contact.process_contact()
    else:
        payload = dict(contact)

    roles = list(payload.get("roles") or [])
    if NAMED_INSURED_ROLE not in roles:
        roles.append(NAMED_INSURED_ROLE)
    payload["roles"] = roles

    return payload
