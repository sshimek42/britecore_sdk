"""
BriteCore Libraries - Core utilities for BriteCore API integration.

This package provides:
- Domain models for contacts and policies
- Validators for data normalization
- API clients and authentication
- Custom exceptions
"""

from sclogging import sclogging_main as scl

from britecore_libraries.constants import (
    COMMON_CITY_REPLACEMENT,
    DEFAULT_ADDRESS_TYPE,
    DEFAULT_EMAIL_TYPE,
    DEFAULT_PHONE_TYPE,
)
from britecore_libraries.exceptions import BritecoreError
from britecore_libraries.maps import load_regexes
from britecore_libraries.models import (
    BritecoreContact,
    BritecorePolicy,
)
from britecore_libraries.validators import (
    AddressValidator,
    EmailValidator,
    NameValidator,
    PhoneValidator,
    fix_apostrophe_capitalisation,
    fix_suffix_capitalisation,
    normalize_business_name,
)

logger = scl.get_parent_logger()

__version__ = "1.0.0"

# Constants

# Exceptions

# Core models

# Validators

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
    "load_regexes",
    # Version
    "__version__",
    "logger",
]
