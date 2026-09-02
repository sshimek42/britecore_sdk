"""Tests for model-instance payload coercion in selected v2 wrappers."""

from __future__ import annotations

from unittest.mock import Mock, patch

import pytest

from britecore_sdk.models import BritecoreCoverage, BritecoreDriver, BritecoreVehicle


def _mock_api_client() -> Mock:
    client = Mock()
    client.do_request.return_value = {"raw": True}
    client.process_result.return_value = {"ok": True}
    return client


class _ModelLikePayload:
    """Simple test double with a to_dict API used by wrapper coercion."""

    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def to_dict(self) -> dict[str, object]:
        return dict(self._payload)


@pytest.mark.unit
def test_create_vehicle_accepts_model_instance() -> None:
    """vehicles.create_vehicle should serialize BritecoreVehicle inputs."""
    from britecore_sdk.api.api_calls.v2 import vehicles

    vehicle = BritecoreVehicle(
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

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.vehicles.API_CLIENT", mock_client):
        result = vehicles.create_vehicle(vehicle=vehicle)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/vehicles/create_vehicle",
        json={"vehicle": vehicle.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_update_driver_accepts_model_instance() -> None:
    """drivers.update_driver should serialize BritecoreDriver inputs."""
    from britecore_sdk.api.api_calls.v2 import drivers

    driver = BritecoreDriver(
        quote_id="quote-1",
        name="Jane Doe",
        date_of_birth="1990-05-01",
        license_state="WI",
        license_number="X1234567",
    )

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.drivers.API_CLIENT", mock_client):
        result = drivers.update_driver(driver=driver)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/drivers/update_driver",
        json={"driver": driver.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_add_coverages_accepts_model_list() -> None:
    """coverages.add_coverages should serialize lists of BritecoreCoverage inputs."""
    from britecore_sdk.api.api_calls.v2 import coverages

    liability = BritecoreCoverage(
        name="Liability", coverage_type="auto", limit_amount=50000
    )
    collision = BritecoreCoverage(name="Collision", coverage_type="auto")

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.coverages.API_CLIENT", mock_client):
        result = coverages.add_coverages(coverages=[liability, collision])

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/coverages/add_coverages",
        json={"coverages": [liability.to_dict(), collision.to_dict()]},
        method="POST",
    )


@pytest.mark.unit
def test_create_claim_vehicle_accepts_model_instance() -> None:
    """claim_vehicles.create_claim_vehicle should serialize BritecoreVehicle inputs."""
    from britecore_sdk.api.api_calls.v2 import claim_vehicles

    claim_vehicle = BritecoreVehicle(
        quote_id="quote-claim-1",
        vehicle_year=2020,
        vehicle_make="Toyota",
        vehicle_model="Camry",
        vehicle_type="Passenger",
        vehicle_number=2,
        address_line1="123 Main St",
        address_city="Madison",
        address_state="WI",
        address_zip="53703",
        address_county="Dane",
    )

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.claim_vehicles.API_CLIENT", mock_client):
        result = claim_vehicles.create_claim_vehicle(claim_vehicle=claim_vehicle)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/claim_vehicles/create_claim_vehicle",
        json={"claim_vehicle": claim_vehicle.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_update_claim_vehicle_accepts_model_instance() -> None:
    """claim_vehicles.update_claim_vehicle should serialize BritecoreVehicle inputs."""
    from britecore_sdk.api.api_calls.v2 import claim_vehicles

    claim_vehicle = BritecoreVehicle(
        quote_id="quote-claim-1",
        vehicle_year=2021,
        vehicle_make="Subaru",
        vehicle_model="Outback",
        vehicle_type="Wagon",
        vehicle_number=3,
        address_line1="456 Lake Rd",
        address_city="Madison",
        address_state="WI",
        address_zip="53705",
        address_county="Dane",
    )

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.claim_vehicles.API_CLIENT", mock_client):
        result = claim_vehicles.update_claim_vehicle(claim_vehicle=claim_vehicle)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/claim_vehicles/update_claim_vehicle",
        json={"claim_vehicle": claim_vehicle.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_create_claim_property_accepts_model_like_payload() -> None:
    """claim_properties.create_claim_property should serialize to_dict payloads."""
    from britecore_sdk.api.api_calls.v2 import claim_properties

    claim_property = _ModelLikePayload(
        {
            "claim_id": "claim-1",
            "address_line1": "123 Main St",
            "property_type": "residential",
        }
    )

    mock_client = _mock_api_client()
    with patch(
        "britecore_sdk.api.api_calls.v2.claim_properties.API_CLIENT", mock_client
    ):
        result = claim_properties.create_claim_property(claim_property=claim_property)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/claim_properties/create_claim_property",
        json={"claim_property": claim_property.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_update_injury_accepts_model_like_payload() -> None:
    """claim_injuries.update_injury should serialize to_dict payloads."""
    from britecore_sdk.api.api_calls.v2 import claim_injuries

    injury = _ModelLikePayload(
        {
            "claim_id": "claim-1",
            "injury_type": "minor",
            "description": "Soft tissue",
        }
    )

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.claim_injuries.API_CLIENT", mock_client):
        result = claim_injuries.update_injury(injury=injury)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/claim_injuries/update_injury",
        json={"injury": injury.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_create_claim_contact_accepts_model_like_payload() -> None:
    """claim_contacts.create_claim_contact should serialize to_dict payloads."""
    from britecore_sdk.api.api_calls.v2 import claim_contacts

    claim_contact = _ModelLikePayload(
        {
            "claim_id": "claim-1",
            "contact_id": "contact-1",
            "role": "Claimant",
        }
    )

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.claim_contacts.API_CLIENT", mock_client):
        result = claim_contacts.create_claim_contact(claim_contact=claim_contact)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/claim_contacts/create_claim_contact",
        json={"claim_contact": claim_contact.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_update_claim_contact_accepts_model_like_payload() -> None:
    """claim_contacts.update_claim_contact should serialize to_dict payloads."""
    from britecore_sdk.api.api_calls.v2 import claim_contacts

    claim_contact = _ModelLikePayload(
        {
            "id": "claim-contact-1",
            "claim_id": "claim-1",
            "role": "Witness",
        }
    )

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.claim_contacts.API_CLIENT", mock_client):
        result = claim_contacts.update_claim_contact(claim_contact=claim_contact)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/claim_contacts/update_claim_contact",
        json={"claim_contact": claim_contact.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_create_named_insured_accepts_model_like_payload() -> None:
    """named_insureds.create_named_insured should serialize to_dict payloads."""
    from britecore_sdk.api.api_calls.v2 import named_insureds

    named_insured = _ModelLikePayload(
        {
            "contact_id": "contact-1",
            "role": "Named Insured",
        }
    )

    mock_client = _mock_api_client()
    with patch("britecore_sdk.api.api_calls.v2.named_insureds.API_CLIENT", mock_client):
        result = named_insureds.create_named_insured(named_insured=named_insured)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/named_insureds/create_named_insured",
        json={"named_insured": named_insured.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_update_catastrophe_accepts_model_like_payload() -> None:
    """claim_catastrophes.update_catastrophe should serialize to_dict payloads."""
    from britecore_sdk.api.api_calls.v2 import claim_catastrophes

    catastrophe = _ModelLikePayload(
        {
            "id": "cat-1",
            "name": "Severe Storm",
        }
    )

    mock_client = _mock_api_client()
    with patch(
        "britecore_sdk.api.api_calls.v2.claim_catastrophes.API_CLIENT", mock_client
    ):
        result = claim_catastrophes.update_catastrophe(catastrophe=catastrophe)

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/claim_catastrophes/update_catastrophe",
        json={"catastrophe": catastrophe.to_dict()},
        method="POST",
    )


@pytest.mark.unit
def test_update_all_authority_limits_accepts_model_like_list() -> None:
    """authority_limits.update_all_authority_limits should serialize list payloads."""
    from britecore_sdk.api.api_calls.v2 import authority_limits

    first = _ModelLikePayload({"id": "al-1", "max_amount": 10000})
    second = _ModelLikePayload({"id": "al-2", "max_amount": 25000})

    mock_client = _mock_api_client()
    with patch(
        "britecore_sdk.api.api_calls.v2.authority_limits.API_CLIENT", mock_client
    ):
        result = authority_limits.update_all_authority_limits(
            authority_limits=[first, second]
        )

    assert result == {"ok": True}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/authority_limits/update_all_authority_limits",
        json={"authority_limits": [first.to_dict(), second.to_dict()]},
        method="POST",
    )


@pytest.mark.unit
def test_edit_attachment_accepts_model_like_payload() -> None:
    """attachments.edit_attachment should serialize to_dict payloads."""
    from britecore_sdk.api.api_calls.v2 import attachments

    attachment = _ModelLikePayload({"id": "file-1", "caption": "Front view"})

    with patch("britecore_sdk.api.api_calls.v2.attachments.post") as mock_post:
        mock_post.return_value = {"ok": True}
        result = attachments.edit_attachment(attachment=attachment)

    assert result == {"ok": True}
    mock_post.assert_called_once_with(
        "/api/v2/attachments/edit_attachment",
        {"attachment": attachment.to_dict()},
    )
