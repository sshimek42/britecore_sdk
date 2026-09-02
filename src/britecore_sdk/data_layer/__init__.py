"""Standalone data-model and normalization layer.

Use this module in small scripts when you only need payload shaping and
validation, without importing API wrapper modules.
"""

from britecore_sdk.data_layer.normalization import (
    normalize_address,
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
from britecore_sdk.models import (
    BritecoreContact,
    BritecoreCoverage,
    BritecoreDriver,
    BritecoreLineDefinition,
    BritecorePaymentMethod,
    BritecorePolicy,
    BritecoreQuote,
    BritecoreVehicle,
)
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
    "BritecoreCoverage",
    "BritecoreDriver",
    "BritecoreLineDefinition",
    "BritecorePaymentMethod",
    "BritecorePolicy",
    "BritecoreQuote",
    "BritecoreVehicle",
    "EmailValidator",
    "NameValidator",
    "PhoneValidator",
    "fix_apostrophe_capitalization",
    "fix_suffix_capitalization",
    "normalize_address",
    "normalize_business_name",
    "normalize_coverage_payload",
    "normalize_contact_payload",
    "normalize_driver_payload",
    "normalize_emails",
    "normalize_line_definition_payload",
    "normalize_name",
    "normalize_named_insured_payload",
    "normalize_payment_method_payload",
    "normalize_policy_payload",
    "normalize_phones",
    "normalize_quote_payload",
    "normalize_vehicle_payload",
]
