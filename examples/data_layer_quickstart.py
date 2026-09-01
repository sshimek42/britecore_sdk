"""Minimal runnable example for the standalone data-layer helpers."""

import datetime as dt

from britecore_sdk.data_layer import (
    normalize_contact_payload,
    normalize_policy_payload,
    normalize_quote_payload,
)


def main() -> None:
    contact_payload = normalize_contact_payload(
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

    policy_payload = normalize_policy_payload(
        policy_number="POL001",
        contacts=[contact_payload],
        effective_date=dt.date(2026, 1, 2),
        policy_type_id="pt-123",
    )

    quote_payload = normalize_quote_payload(
        number="Q-001",
        policy_type_id="pt-123",
        agency_id="agency-1",
        named_insureds=["ni-1"],
        risks=["risk-1"],
    )

    print("contact", contact_payload)
    print("policy", policy_payload)
    print("quote", quote_payload)


if __name__ == "__main__":
    main()
