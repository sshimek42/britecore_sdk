"""Shared TypedDict response shapes for BriteCore API wrappers.

These types describe the normalised payload returned by
``BritecoreAPIClient.process_result()``.  All wrappers in
``api/api_calls/v2/`` return ``Any``; callers who want IDE
autocomplete and static type-checking can narrow the return
type by casting to the appropriate TypedDict.

Example::

    from typing import cast
    from britecore_libraries.api.api_calls.v2 import policies
    from britecore_libraries.api.types import PolicyData

    result = cast(PolicyData, policies.retrieve_policy(policy_number="POL-001"))
    print(result["policy_number"])
"""
from typing import Any, NotRequired

from typing_extensions import TypedDict


class BritecoreResponse(TypedDict, total=False):
    """Top-level envelope returned by every BriteCore API call.

    The ``data`` key is the primary payload; ``message`` / ``messages``
    carry human-readable status text.
    """

    success: bool
    data: Any
    message: str
    messages: list[str]


# ---------------------------------------------------------------------------
# Common nested shapes
# ---------------------------------------------------------------------------


class AddressData(TypedDict, total=False):
    """Normalised address object as returned by the contacts / policy APIs."""

    address_id: str
    address_type: str
    street: str
    city: str
    state: str
    zip: str
    country: str


class PhoneData(TypedDict, total=False):
    """Normalised phone object."""

    phone_id: str
    phone_type: str
    phone_number: str


class EmailData(TypedDict, total=False):
    """Normalised email object."""

    email_id: str
    email_type: str
    email_address: str


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------


class ContactData(TypedDict, total=False):
    """Contact payload returned by the contacts API."""

    contact_id: str
    first_name: str
    last_name: str
    business_name: str
    phones: list[PhoneData]
    emails: list[EmailData]
    addresses: list[AddressData]


# ---------------------------------------------------------------------------
# Policy / Revision
# ---------------------------------------------------------------------------


class PolicyData(TypedDict, total=False):
    """Policy payload returned by the policies API."""

    policy_id: str
    policy_number: str
    revision_id: str
    status: str
    effective_date: str
    expiration_date: str
    contacts: list[ContactData]


class RevisionData(TypedDict, total=False):
    """Policy revision detail payload."""

    revision_id: str
    policy_id: str
    policy_number: str
    status: str
    effective_date: str
    expiration_date: str
    premium: NotRequired[float]


# ---------------------------------------------------------------------------
# Quote
# ---------------------------------------------------------------------------


class QuoteData(TypedDict, total=False):
    """Quote payload returned by the quotes API."""

    quote_id: str
    policy_number: str
    status: str
    premium: NotRequired[float]


# ---------------------------------------------------------------------------
# Invoice / Billing
# ---------------------------------------------------------------------------


class InvoiceData(TypedDict, total=False):
    """Invoice payload returned by the accounting / billing APIs."""

    invoice_id: str
    policy_id: str
    amount_due: float
    bill_date: str
    due_date: str
    status: str


__all__ = [
    "AddressData",
    "BritecoreResponse",
    "ContactData",
    "EmailData",
    "InvoiceData",
    "PhoneData",
    "PolicyData",
    "QuoteData",
    "RevisionData",
]

