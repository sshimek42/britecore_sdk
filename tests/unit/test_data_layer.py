"""Unit tests for the standalone data_layer helpers."""

import datetime as dt

import pytest

from britecore_sdk.data_layer import (
    normalize_contact_payload,
    normalize_emails,
    normalize_name,
    normalize_phones,
    normalize_policy_payload,
    normalize_quote_payload,
)


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
