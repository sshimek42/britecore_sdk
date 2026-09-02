"""Unit tests for the standalone data_layer helpers."""

import datetime as dt

import pytest

from britecore_sdk.data_layer import (
    normalize_contact_payload,
    normalize_coverage_payload,
    normalize_driver_payload,
    normalize_emails,
    normalize_line_definition_payload,
    normalize_name,
    normalize_named_insured_payload,
    normalize_payment_method_payload,
    normalize_phones,
    normalize_policy_payload,
    normalize_quote_payload,
    normalize_vehicle_payload,
)
from britecore_sdk.models import BritecoreContact


@pytest.mark.unit
def test_normalize_name_helper():
    """normalize_name applies business suffix normalization."""
    assert normalize_name("acme llc") == "acme LLC"


@pytest.mark.unit
def test_normalize_phones_helper():
    """normalize_phones returns BriteCore-formatted phone values."""
    result = normalize_phones([{"phone": "(920) 555-1234", "type": "mobile"}])
    assert result == [{"phone": "1-920-555-1234", "type": "Cell"}]


@pytest.mark.unit
def test_normalize_emails_helper():
    """normalize_emails lowercases and preserves normalized type values."""
    result = normalize_emails([{"email": "TEAM@ACME.COM", "type": "work"}])
    assert result == [{"email": "team@acme.com", "type": "Work"}]


@pytest.mark.unit
def test_normalize_contact_payload_helper():
    """normalize_contact_payload builds a BriteCore-ready contact dict."""
    payload = normalize_contact_payload(
        name="acme llc",
        address={
            "address_line1": "123 Main St",
            "address_city": "Madison",
            "address_state": "WI",
            "address_zip": "53703",
        },
        phone_numbers=[{"phone": "(920) 555-1234", "type": "mobile"}],
        emails=[{"email": "TEAM@ACME.COM", "type": "work"}],
    )

    assert payload["name"] == "acme LLC"
    assert payload["phones"] == [{"phone": "1-920-555-1234", "type": "Cell"}]
    assert payload["emails"] == [{"email": "team@acme.com", "type": "Work"}]


@pytest.mark.unit
def test_normalize_policy_payload_helper():
    """normalize_policy_payload coerces dates and accepts contact dict payloads."""
    payload = normalize_policy_payload(
        policy_number="POL001",
        contacts=[{"contact_id": "c-1", "name": "Acme"}],
        effective_date=dt.date(2026, 1, 2),
        policy_type_id="pt-123",
    )

    assert payload["policy_number"] == "POL001"
    assert payload["effective_date"] == "2026-01-02"
    assert payload["policy_type_id"] == "pt-123"
    assert payload["contacts"][0]["contact_id"] == "c-1"


@pytest.mark.unit
def test_normalize_quote_payload_helper():
    """normalize_quote_payload returns model-shaped quote payload with date coercion."""
    payload = normalize_quote_payload(
        number="Q-001",
        policy_type_id="pt-123",
        agency_id="agency-1",
        named_insureds=["ni-1"],
        risks=["risk-1"],
        inception_date=dt.date(2026, 1, 5),
        effective_date=dt.date(2026, 1, 7),
    )

    assert payload["number"] == "Q-001"
    assert payload["policy_type_id"] == "pt-123"
    assert payload["inception_date"] == "2026-01-05"
    assert payload["effective_date"] == "2026-01-07"


@pytest.mark.unit
def test_normalize_named_insured_payload_from_contact_model():
    """normalize_named_insured_payload maps contact models and injects role metadata."""
    contact = BritecoreContact(
        name="acme llc",
        address={
            "address_line1": "123 Main St",
            "address_city": "Madison",
            "address_state": "WI",
            "address_zip": "53703",
        },
    )

    payload = normalize_named_insured_payload(contact=contact, is_primary=True)

    assert payload["name"] == "acme LLC"
    assert payload["type"] == "individual"
    assert payload["role"] == "Named Insured"
    assert payload["is_primary"] is True


@pytest.mark.unit
def test_normalize_named_insured_payload_with_dict_shape_fixes():
    """normalize_named_insured_payload maps id->contact_id for existing contacts."""
    payload = normalize_named_insured_payload(
        contact={"id": "contact-1", "name": "Jane Doe", "type": "individual"}
    )

    assert payload["contact_id"] == "contact-1"
    assert payload["role"] == "Named Insured"


@pytest.mark.unit
def test_normalize_payment_method_payload_helper():
    """normalize_payment_method_payload produces model-shaped payloads."""
    payload = normalize_payment_method_payload(
        contact_id="contact-1",
        method="ACH",
        account_name="Primary Account",
        name_on_account="Jane Doe",
        masked_number="****1234",
    )

    assert payload["contact_id"] == "contact-1"
    assert payload["method"] == "ACH"
    assert payload["active"] is True


@pytest.mark.unit
def test_normalize_vehicle_payload_helper():
    """normalize_vehicle_payload returns expected vehicle payload fields."""
    payload = normalize_vehicle_payload(
        quote_id="quote-1",
        vehicle_year=2025,
        vehicle_make="Ford",
        vehicle_model="F-150",
        vehicle_type="Truck",
        vehicle_number=1,
        address_line1="123 Main St",
        address_city="Madison",
        address_state="WI",
        address_zip="53703",
        address_county="Dane",
    )

    assert payload["quote_id"] == "quote-1"
    assert payload["vehicle_year"] == 2025
    assert payload["included_in_policy"] is True


@pytest.mark.unit
def test_normalize_coverage_payload_helper():
    """normalize_coverage_payload keeps coverage values and tags."""
    payload = normalize_coverage_payload(
        name="Liability",
        coverage_type="auto",
        limit_amount=100000,
        system_tags={"source": "sdk"},
    )

    assert payload["name"] == "Liability"
    assert payload["coverage_type"] == "auto"
    assert payload["system_tags"] == {"source": "sdk"}


@pytest.mark.unit
def test_normalize_driver_payload_helper():
    """normalize_driver_payload builds driver payload and filters null fields."""
    payload = normalize_driver_payload(
        quote_id="quote-1",
        name="Jane Doe",
        date_of_birth="1990-05-01",
        license_state="WI",
        license_number="X1234567",
    )

    assert payload["name"] == "Jane Doe"
    assert payload["license_state"] == "WI"
    assert "occupation" not in payload


@pytest.mark.unit
def test_normalize_line_definition_payload_helper():
    """normalize_line_definition_payload builds line payload defaults."""
    payload = normalize_line_definition_payload(
        location_id="state-wi",
        effective_date_id="eff-1",
        name="Personal Auto",
    )

    assert payload["location_id"] == "state-wi"
    assert payload["effective_date_id"] == "eff-1"
    assert payload["name"] == "Personal Auto"
