"""Tests for additional domain models."""

import pytest

from britecore_sdk.models import (
    BritecoreCoverage,
    BritecoreDriver,
    BritecoreLineDefinition,
    BritecorePaymentMethod,
    BritecoreVehicle,
)


@pytest.mark.unit
def test_payment_method_to_dict_filters_empty_optional_fields():
    """Payment method payload excludes empty optional metadata containers."""
    payment_method = BritecorePaymentMethod(
        contact_id="contact-1",
        method="ACH",
        account_name="Primary Account",
        name_on_account="Jane Doe",
        masked_number="****4321",
    )

    result = payment_method.to_dict()

    assert result["contact_id"] == "contact-1"
    assert result["method"] == "ACH"
    assert "metadata" not in result


@pytest.mark.unit
def test_vehicle_to_dict_includes_required_fields():
    """Vehicle payload includes expected required fields."""
    vehicle = BritecoreVehicle(
        quote_id="quote-1",
        vehicle_year=2024,
        vehicle_make="Honda",
        vehicle_model="Civic",
        vehicle_type="Passenger",
        vehicle_number=1,
        address_line1="123 Main St",
        address_city="Madison",
        address_state="WI",
        address_zip="53703",
        address_county="Dane",
    )

    result = vehicle.to_dict()

    assert result["quote_id"] == "quote-1"
    assert result["vehicle_year"] == 2024
    assert result["included_in_policy"] is True


@pytest.mark.unit
def test_coverage_to_dict_includes_system_tags_when_present():
    """Coverage payload preserves system tags when provided."""
    coverage = BritecoreCoverage(
        name="Dwelling",
        coverage_type="property",
        limit_amount=250000,
        system_tags={"source": "sdk"},
    )

    result = coverage.to_dict()

    assert result["name"] == "Dwelling"
    assert result["coverage_type"] == "property"
    assert result["system_tags"] == {"source": "sdk"}


@pytest.mark.unit
def test_driver_to_dict_filters_none_values():
    """Driver payload excludes optional null fields."""
    driver = BritecoreDriver(
        quote_id="quote-1",
        name="Jane Doe",
        date_of_birth="1990-05-01",
        license_state="WI",
        license_number="D1234567",
    )

    result = driver.to_dict()

    assert result["name"] == "Jane Doe"
    assert result["license_state"] == "WI"
    assert "occupation" not in result


@pytest.mark.unit
def test_line_definition_to_dict_filters_empty_lists():
    """Line definition payload excludes empty policy type lists until populated."""
    line_definition = BritecoreLineDefinition(
        location_id="state-wi",
        effective_date_id="eff-1",
        name="Personal Auto",
    )

    result = line_definition.to_dict()

    assert result["location_id"] == "state-wi"
    assert result["effective_date_id"] == "eff-1"
    assert "policy_types" not in result
