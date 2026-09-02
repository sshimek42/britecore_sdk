"""Lightweight data shaping helpers for one-off scripts.

This module intentionally avoids API transport/client imports so callers can use
normalization logic without touching request/auth layers.
"""

import datetime as dt
from typing import Literal

from britecore_sdk.models import (
    BritecoreContact,
    BritecoreCoverage,
    BritecoreDriver,
    BritecoreLineDefinition,
    BritecorePaymentMethod,
    BritecoreQuote,
    BritecoreVehicle,
)
from britecore_sdk.validators import (
    AddressValidator,
    EmailValidator,
    NameValidator,
    PhoneValidator,
)


def normalize_name(name: str) -> str:
    """Normalize a business/person name using SDK name rules."""
    return NameValidator.normalize_business_name(name)


def normalize_address(address: dict[str, str]) -> list[dict[str, str]]:
    """Validate and normalize one address payload."""
    return AddressValidator(address).process()


def normalize_phones(
    phone_numbers: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Validate and normalize phone entries."""
    return PhoneValidator(phone_numbers or []).process()


def normalize_emails(
    emails: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    """Validate and normalize email entries."""
    return EmailValidator(emails or []).process()


def normalize_contact_payload(
    *,
    name: str,
    address: dict[str, str],
    policy_number: str | None = None,
    phone_numbers: list[dict[str, str]] | None = None,
    emails: list[dict[str, str]] | None = None,
    contact_id: str | None = None,
    contact_type: Literal["individual", "organization"] = "individual",
) -> dict:
    """Build a BriteCore-ready contact payload with validation/normalization applied."""
    return BritecoreContact(
        name=name,
        address=address,
        policy_number=policy_number,
        phone_number=phone_numbers,
        email=emails,
        contact_id=contact_id,
        contact_type=contact_type,
    ).process_contact()


def normalize_named_insured_payload(
    *,
    contact: BritecoreContact | dict,
    role: str = "Named Insured",
    is_primary: bool | None = None,
) -> dict:
    """Map a contact object/dict to a named-insured payload shape."""
    contact_payload = (
        contact.process_contact()
        if isinstance(contact, BritecoreContact)
        else dict(contact)
    )
    named_insured = dict(contact_payload)

    # create_named_insured accepts an existing contact via contact_id.
    if "contact_id" not in named_insured and named_insured.get("id") is not None:
        named_insured["contact_id"] = named_insured["id"]

    named_insured["role"] = role
    if is_primary is not None:
        named_insured["is_primary"] = is_primary
    return named_insured


def _to_iso_date(value: dt.datetime | dt.date | str | None) -> str | None:
    """Normalize date-like values to YYYY-MM-DD strings for payloads."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, dt.datetime):
        return value.date().isoformat()
    return value.isoformat()


def _coerce_contact_payloads(
    contacts: list[BritecoreContact | dict] | None,
) -> list[dict]:
    """Accept contact model instances or raw dict payloads."""
    if not contacts:
        return []

    normalized_contacts: list[dict] = []
    for item in contacts:
        if isinstance(item, BritecoreContact):
            normalized_contacts.append(item.process_contact())
        else:
            normalized_contacts.append(dict(item))
    return normalized_contacts


def normalize_policy_payload(
    *,
    policy_number: str,
    contacts: list[BritecoreContact | dict] | None,
    effective_date: dt.datetime | dt.date | str,
    policy_type_id: str,
    inception_date: dt.datetime | dt.date | str | None = None,
    term_type: str = "1 Year",
    renewal_term_type: str = "1 Year",
    is_renewal: bool = True,
    as_agent: bool = False,
    manual_policy_number: bool = True,
    previous_inspection_date: dt.datetime | dt.date | str | None = None,
    next_inspection_date: dt.datetime | dt.date | str | None = None,
) -> dict:
    """Build a policy payload with script-friendly date/contact coercion."""
    return {
        "policy_number": policy_number,
        "contacts": _coerce_contact_payloads(contacts),
        "effective_date": _to_iso_date(effective_date),
        "policy_type_id": policy_type_id,
        "inception_date": _to_iso_date(inception_date),
        "term_type": term_type,
        "renewal_term_type": renewal_term_type,
        "is_renewal": is_renewal,
        "as_agent": as_agent,
        "manual_policy_number": manual_policy_number,
        "previous_inspection_date": _to_iso_date(previous_inspection_date),
        "next_inspection_date": _to_iso_date(next_inspection_date),
    }


def normalize_quote_payload(
    *,
    number: str,
    policy_type_id: str,
    agency_id: str,
    named_insureds: list[str],
    risks: list[str],
    underwriting_questions: list | None = None,
    description: str | None = "",
    number_origin: str = "manual",
    transaction_type: str = "renewal",
    term_type: str = "1 Year",
    inception_date: dt.datetime | dt.date | str | None = None,
    effective_date: dt.datetime | dt.date | str | None = None,
    next_inspection_date: dt.datetime | dt.date | str | None = None,
    previous_inspection_date: dt.datetime | dt.date | str | None = None,
) -> dict:
    """Build a quote payload using model defaults plus date coercion."""
    quote = BritecoreQuote(
        number=number,
        policy_type_id=policy_type_id,
        agency_id=agency_id,
        named_insureds=named_insureds,
        risks=risks,
        underwriting_questions=underwriting_questions or [],
        description=description,
        number_origin=number_origin,
        transaction_type=transaction_type,
        term_type=term_type,
        inception_date=_to_iso_date(inception_date) or dt.date.today().isoformat(),
        effective_date=_to_iso_date(effective_date) or dt.date.today().isoformat(),
        next_inspection_date=_to_iso_date(next_inspection_date),
        previous_inspection_date=_to_iso_date(previous_inspection_date),
    )
    return quote.to_dict()


def normalize_payment_method_payload(
    *,
    contact_id: str,
    method: str,
    account_name: str,
    name_on_account: str,
    masked_number: str,
    id: str | None = None,
    account_type: str | None = None,
    masked_routing: str | None = None,
    expire_date: str | None = None,
    address_line1: str | None = None,
    address_line2: str | None = None,
    address_city: str | None = None,
    address_state: str | None = None,
    address_zip: str | None = None,
    primary_account: bool = False,
    active: bool = True,
    metadata: dict | None = None,
) -> dict:
    """Build a payment-method payload using model defaults."""
    return BritecorePaymentMethod(
        id=id,
        contact_id=contact_id,
        method=method,
        account_type=account_type,
        account_name=account_name,
        name_on_account=name_on_account,
        masked_number=masked_number,
        masked_routing=masked_routing,
        expire_date=expire_date,
        address_line1=address_line1,
        address_line2=address_line2,
        address_city=address_city,
        address_state=address_state,
        address_zip=address_zip,
        primary_account=primary_account,
        active=active,
        metadata=metadata or {},
    ).to_dict()


def normalize_vehicle_payload(
    *,
    quote_id: str,
    vehicle_year: int,
    vehicle_make: str,
    vehicle_model: str,
    vehicle_type: str,
    vehicle_number: int,
    address_line1: str,
    address_city: str,
    address_state: str,
    address_zip: str,
    address_county: str,
    id: str | None = None,
    address_line2: str | None = None,
    cost_new: float | int | None = None,
    included_in_policy: bool = True,
    deleted: bool = False,
) -> dict:
    """Build a vehicle payload using model defaults."""
    return BritecoreVehicle(
        id=id,
        quote_id=quote_id,
        vehicle_year=vehicle_year,
        vehicle_make=vehicle_make,
        vehicle_model=vehicle_model,
        vehicle_type=vehicle_type,
        vehicle_number=vehicle_number,
        address_line1=address_line1,
        address_line2=address_line2,
        address_city=address_city,
        address_state=address_state,
        address_zip=address_zip,
        address_county=address_county,
        cost_new=cost_new,
        included_in_policy=included_in_policy,
        deleted=deleted,
    ).to_dict()


def normalize_coverage_payload(
    *,
    name: str,
    coverage_type: str,
    id: str | None = None,
    description: str | None = None,
    limit_amount: float | int | None = None,
    deductible_amount: float | int | None = None,
    annual_premium: float | int | None = None,
    sub_line_id: str | None = None,
    policy_type_item_id: str | None = None,
    system_tags: dict | None = None,
) -> dict:
    """Build a coverage payload using model defaults."""
    return BritecoreCoverage(
        id=id,
        name=name,
        description=description,
        coverage_type=coverage_type,
        limit_amount=limit_amount,
        deductible_amount=deductible_amount,
        annual_premium=annual_premium,
        sub_line_id=sub_line_id,
        policy_type_item_id=policy_type_item_id,
        system_tags=system_tags or {},
    ).to_dict()


def normalize_driver_payload(
    *,
    quote_id: str,
    name: str,
    date_of_birth: str,
    license_state: str,
    license_number: str,
    id: str | None = None,
    gender: str | None = None,
    license_class: str | None = None,
    marital_status: str | None = None,
    occupation: str | None = None,
    years_driving_experience: int | None = None,
) -> dict:
    """Build a driver payload using model defaults."""
    return BritecoreDriver(
        id=id,
        quote_id=quote_id,
        name=name,
        date_of_birth=date_of_birth,
        gender=gender,
        license_state=license_state,
        license_number=license_number,
        license_class=license_class,
        marital_status=marital_status,
        occupation=occupation,
        years_driving_experience=years_driving_experience,
    ).to_dict()


def normalize_line_definition_payload(
    *,
    location_id: str,
    effective_date_id: str,
    name: str,
    policy_types: list[str] | None = None,
    id: str | None = None,
    description: str | None = None,
    line: dict | None = None,
    system_tags: dict | None = None,
) -> dict:
    """Build a line-definition payload using model defaults."""
    return BritecoreLineDefinition(
        id=id,
        location_id=location_id,
        effective_date_id=effective_date_id,
        name=name,
        description=description,
        policy_types=policy_types or [],
        line=line,
        system_tags=system_tags or {},
    ).to_dict()
