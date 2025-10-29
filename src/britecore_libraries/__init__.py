"""
BriteCore Libraries - Core utilities for BriteCore API integration.

This package provides:
- Domain models for contacts and policies
- Validators for data normalization
- API clients and authentication
- Custom exceptions
"""

__version__ = "1.0.0"

# Core models
from britecore_libraries.models import (
    BritecoreContact,
    BritecorePolicy,
    )

# Validators
from britecore_libraries.validators import (
    AddressValidator,
    EmailValidator,
    NameValidator,
    PhoneValidator,
    fix_suffix_capitalisation,
    fix_apostrophe_capitalisation,
    normalize_business_name
    )

# Exceptions
from britecore_libraries.exceptions import BritecoreError

# Constants
from britecore_libraries.constants import (
    DEFAULT_ADDRESS_TYPE,
    DEFAULT_EMAIL_TYPE,
    DEFAULT_PHONE_TYPE,
    COMMON_CITY_REPLACEMENT,
    )

from britecore_libraries.maps import name_groups, compiled_regexes


__all__ = [
    # Models
    "BritecoreContact",
    "BritecorePolicy",

    # Validators
    "AddressValidator",
    "EmailValidator",
    "NameValidator",
    "PhoneValidator",
    "fix_suffix_capitalisation",
    "fix_apostrophe_capitalisation",
    "normalize_business_name",

    # Exceptions
    "BritecoreError",

    # Constants
    "DEFAULT_ADDRESS_TYPE",
    "DEFAULT_EMAIL_TYPE",
    "DEFAULT_PHONE_TYPE",
    "COMMON_CITY_REPLACEMENT",

    "compiled_regexes",
    "name_groups",

    # Version
    "__version__",
    ]