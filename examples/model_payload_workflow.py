"""Local-only demo for new model payload helpers.

This script does not make API calls. It demonstrates model construction and
payload shaping through `to_dict()` and `britecore_sdk.data_layer` helpers.
"""

from __future__ import annotations

from pprint import pprint

from britecore_sdk.data_layer import (
    normalize_coverage_payload,
    normalize_driver_payload,
    normalize_line_definition_payload,
    normalize_payment_method_payload,
    normalize_vehicle_payload,
)
from britecore_sdk.models import (
    BritecoreCoverage,
    BritecoreDriver,
    BritecoreLineDefinition,
    BritecorePaymentMethod,
    BritecoreVehicle,
)


def run_model_examples() -> None:
    """Demonstrate model-level payload generation via to_dict()."""
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
    driver = BritecoreDriver(
        quote_id="quote-1",
        name="Jane Doe",
        date_of_birth="1990-05-01",
        license_state="WI",
        license_number="X1234567",
    )
    coverage = BritecoreCoverage(
        name="Liability", coverage_type="auto", limit_amount=50000
    )
    payment_method = BritecorePaymentMethod(
        contact_id="contact-1",
        method="ACH",
        account_name="Primary Account",
        name_on_account="Jane Doe",
        masked_number="****1234",
    )
    line_definition = BritecoreLineDefinition(
        location_id="state-wi",
        effective_date_id="eff-1",
        name="Personal Auto",
    )

    print("Model -> to_dict payloads")
    pprint(vehicle.to_dict())
    pprint(driver.to_dict())
    pprint(coverage.to_dict())
    pprint(payment_method.to_dict())
    pprint(line_definition.to_dict())


def run_data_layer_examples() -> None:
    """Demonstrate payload shaping through standalone data_layer helpers."""
    print("\nData-layer normalize_*_payload helpers")
    pprint(
        normalize_vehicle_payload(
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
    )
    pprint(
        normalize_driver_payload(
            quote_id="quote-1",
            name="Jane Doe",
            date_of_birth="1990-05-01",
            license_state="WI",
            license_number="X1234567",
        )
    )
    pprint(normalize_coverage_payload(name="Liability", coverage_type="auto"))
    pprint(
        normalize_payment_method_payload(
            contact_id="contact-1",
            method="ACH",
            account_name="Primary Account",
            name_on_account="Jane Doe",
            masked_number="****1234",
        )
    )
    pprint(
        normalize_line_definition_payload(
            location_id="state-wi",
            effective_date_id="eff-1",
            name="Personal Auto",
        )
    )


def main() -> int:
    """Run all local payload examples."""
    run_model_examples()
    run_data_layer_examples()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
