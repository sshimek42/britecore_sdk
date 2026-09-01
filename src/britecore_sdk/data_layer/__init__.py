"""Standalone data-model and normalization layer.

Use this module in small scripts when you only need payload shaping and
validation, without importing API wrapper modules.
"""

from britecore_sdk.data_layer.normalization import (
    normalize_address,
    normalize_contact_payload,
    normalize_emails,
    normalize_name,
    normalize_phones,
    normalize_policy_payload,
    normalize_quote_payload,
)
from britecore_sdk.models import BritecoreContact, BritecorePolicy, BritecoreQuote
from britecore_sdk.validators import (
    AddressValidator,
    EmailValidator,
    NameValidator,
    PhoneValidator,
    fix_apostrophe_capitalization,
    fix_suffix_capitalization,
    normalize_business_name,
)

__all__ = [
    "AddressValidator",
    "BritecoreContact",
    "BritecorePolicy",
    "BritecoreQuote",
    "EmailValidator",
    "NameValidator",
    "PhoneValidator",
    "fix_apostrophe_capitalization",
    "fix_suffix_capitalization",
    "normalize_address",
    "normalize_business_name",
    "normalize_contact_payload",
    "normalize_emails",
    "normalize_name",
    "normalize_policy_payload",
    "normalize_phones",
    "normalize_quote_payload",
]
