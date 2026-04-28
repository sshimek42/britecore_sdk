"""Smoke / structural tests for britecore_sdk.api.types.

TypedDict classes have no runtime behaviour to test, so this module
verifies:
  1. Every name listed in __all__ is importable from the module.
  2. Each TypedDict can be instantiated with representative data and
     the fields survive a round-trip through dict().
  3. The BritecoreResponse envelope accepts the canonical response shape.
"""

from britecore_sdk.api.types import (
    AddressData,
    BritecoreResponse,
    ContactData,
    EmailData,
    InvoiceData,
    PhoneData,
    PolicyData,
    QuoteData,
    RevisionData,
    __all__,
)

# ---------------------------------------------------------------------------
# __all__ completeness
# ---------------------------------------------------------------------------


EXPECTED_EXPORTS = {
    "AddressData",
    "BritecoreResponse",
    "ContactData",
    "EmailData",
    "InvoiceData",
    "PhoneData",
    "PolicyData",
    "QuoteData",
    "RevisionData",
}


def test_all_exports_match_expected():
    assert set(__all__) == EXPECTED_EXPORTS


def test_all_names_importable():
    import britecore_sdk.api.types as t

    for name in EXPECTED_EXPORTS:
        assert hasattr(t, name), f"{name!r} not found in britecore_sdk.api.types"


# ---------------------------------------------------------------------------
# BritecoreResponse
# ---------------------------------------------------------------------------


def test_britecore_response_full():
    resp: BritecoreResponse = {
        "success": True,
        "data": {"id": "abc"},
        "message": "OK",
        "messages": ["all good"],
    }
    assert resp["success"] is True
    assert resp["data"]["id"] == "abc"
    assert resp["message"] == "OK"
    assert resp["messages"] == ["all good"]


def test_britecore_response_minimal():
    resp: BritecoreResponse = {"success": False}
    assert resp["success"] is False


# ---------------------------------------------------------------------------
# Primitive nested shapes
# ---------------------------------------------------------------------------


def test_address_data_fields():
    addr: AddressData = {
        "address_id": "ADDR-1",
        "address_type": "physical",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "zip": "90210",
        "country": "US",
    }
    assert addr["zip"] == "90210"


def test_phone_data_fields():
    phone: PhoneData = {
        "phone_id": "PH-1",
        "phone_type": "mobile",
        "phone_number": "555-1234",
    }
    assert phone["phone_number"] == "555-1234"


def test_email_data_fields():
    email: EmailData = {
        "email_id": "EM-1",
        "email_type": "work",
        "email_address": "user@example.com",
    }
    assert email["email_address"] == "user@example.com"


# ---------------------------------------------------------------------------
# Domain shapes
# ---------------------------------------------------------------------------


def test_contact_data_with_nested_collections():
    contact: ContactData = {
        "contact_id": "C-1",
        "first_name": "Jane",
        "last_name": "Doe",
        "business_name": "ACME",
        "phones": [
            {"phone_id": "PH-1", "phone_type": "home", "phone_number": "555-0000"}
        ],
        "emails": [
            {"email_id": "EM-1", "email_type": "personal", "email_address": "j@e.com"}
        ],
        "addresses": [
            {
                "address_id": "A-1",
                "street": "1 Way",
                "city": "Town",
                "state": "TX",
                "zip": "77001",
            }
        ],
    }
    assert contact["contact_id"] == "C-1"
    assert contact["phones"][0]["phone_number"] == "555-0000"


def test_policy_data_fields():
    policy: PolicyData = {
        "policy_id": "POL-1",
        "policy_number": "P-100",
        "revision_id": "REV-1",
        "status": "active",
        "effective_date": "2026-01-01",
        "expiration_date": "2027-01-01",
        "contacts": [],
    }
    assert policy["policy_number"] == "P-100"


def test_revision_data_optional_premium():
    rev: RevisionData = {
        "revision_id": "REV-2",
        "policy_id": "POL-2",
        "policy_number": "P-200",
        "status": "active",
        "effective_date": "2026-01-01",
        "expiration_date": "2027-01-01",
        "premium": 1234.56,
    }
    assert rev["premium"] == 1234.56


def test_revision_data_without_premium():
    rev: RevisionData = {
        "revision_id": "REV-3",
        "policy_number": "P-300",
        "status": "quoted",
    }
    assert "premium" not in rev


def test_quote_data_fields():
    quote: QuoteData = {
        "quote_id": "Q-1",
        "policy_number": "P-Q1",
        "status": "pending",
        "premium": 500.00,
    }
    assert quote["premium"] == 500.00


def test_invoice_data_fields():
    invoice: InvoiceData = {
        "invoice_id": "INV-1",
        "policy_id": "POL-1",
        "amount_due": 250.75,
        "bill_date": "2026-04-01",
        "due_date": "2026-04-15",
        "status": "unpaid",
    }
    assert invoice["amount_due"] == 250.75
