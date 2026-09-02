"""Tests for claim mapper helpers."""

import pytest

from britecore_sdk.mappers.claims import to_named_insured_payload
from britecore_sdk.models import BritecoreContact


@pytest.mark.unit
def test_named_insured_role_added_if_missing():
    """Mapper appends named insured role without removing existing values."""
    out = to_named_insured_payload(
        {
            "name": "Jane Doe",
            "roles": ["claimant"],
        }
    )

    assert "named_insured" in out["roles"]
    assert "claimant" in out["roles"]


@pytest.mark.unit
def test_named_insured_role_not_duplicated():
    """Mapper avoids duplicate named insured role entries."""
    out = to_named_insured_payload(
        {
            "name": "Jane Doe",
            "roles": ["named_insured"],
        }
    )

    assert out["roles"].count("named_insured") == 1


@pytest.mark.unit
def test_named_insured_payload_shape_uses_contact_fields():
    """Mapper keeps contact payload fields while adding role metadata."""
    out = to_named_insured_payload(
        {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane@example.com",
        }
    )

    assert out["first_name"] == "Jane"
    assert out["last_name"] == "Doe"
    assert out["email"] == "jane@example.com"
    assert "named_insured" in out["roles"]


@pytest.mark.unit
def test_named_insured_payload_accepts_contact_model():
    """Mapper supports BritecoreContact instances for claim payload shaping."""
    contact = BritecoreContact(
        name="Jane Doe",
        address={
            "address_line1": "123 Main St",
            "address_city": "Madison",
            "address_state": "WI",
            "address_zip": "53703",
        },
    )

    out = to_named_insured_payload(contact)

    assert out["name"] == "Jane Doe"
    assert "named_insured" in out["roles"]
