# ruff: noqa: E402

"""
BriteCore Libraries - Core utilities for BriteCore API integration.

This package provides:
- Domain models for contacts and policies
- Validators for data normalization
- API clients and authentication
- Custom exceptions
"""

from importlib.metadata import PackageNotFoundError, version

from britecore_libraries.base_logger import get_logger

logger = get_logger(
    __package__, level="INFO", log_to_file=True, log_file_level="INFO"
)

try:
    __version__ = version("britecore_libraries")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

# Constants
# API client helpers — exposed at package root for convenience
from britecore_libraries.api.api_calls import (
    get_api_client,
    get_async_api_client,
)
from britecore_libraries.constants import (
    COMMON_CITY_REPLACEMENT,
    DEFAULT_ADDRESS_TYPE,
    DEFAULT_EMAIL_TYPE,
    DEFAULT_PHONE_TYPE,
)

# Exceptions
from britecore_libraries.exceptions import BritecoreError
from britecore_libraries.maps import load_regexes

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
    fix_apostrophe_capitalization,
    fix_suffix_capitalization,
    normalize_business_name,
)

__all__ = [
    # Models
    "BritecoreContact",
    "BritecorePolicy",
    # Validators
    "AddressValidator",
    "EmailValidator",
    "NameValidator",
    "PhoneValidator",
    "fix_suffix_capitalization",
    "fix_apostrophe_capitalization",
    "normalize_business_name",
    # Exceptions
    "BritecoreError",
    # Constants
    "DEFAULT_ADDRESS_TYPE",
    "DEFAULT_EMAIL_TYPE",
    "DEFAULT_PHONE_TYPE",
    "COMMON_CITY_REPLACEMENT",
    "load_regexes",
    # API client helpers
    "get_api_client",
    "get_async_api_client",
    # Version
    "__version__",
    "logger",
]
