"""Lightweight data shaping helpers for one-off scripts.

This module intentionally avoids API transport/client imports so callers can use
normalization logic without touching request/auth layers.
"""

import datetime as dt
from typing import Literal

from britecore_sdk.models import BritecoreContact, BritecoreQuote
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
