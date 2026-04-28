"""
BriteCore Libraries - Core utilities for BriteCore API integration.

This package provides:
- Domain models for contacts and policies
- Validators for data normalization
- API clients and authentication
- Custom exceptions
"""

import os
from importlib import import_module
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import TYPE_CHECKING, Any

from britecore_sdk.base_logger import configure_logging, get_logger

logger = get_logger(__package__)

try:
    __version__ = version("britecore_sdk")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

if TYPE_CHECKING:
    from britecore_sdk.api.api_calls import (
        get_api_client,
        get_async_api_client,
        use_api_client,
    )
    from britecore_sdk.constants import (
        COMMON_CITY_REPLACEMENT,
        DEFAULT_ADDRESS_TYPE,
        DEFAULT_EMAIL_TYPE,
        DEFAULT_PHONE_TYPE,
    )
    from britecore_sdk.exceptions import (
        AuthenticationError,
        BritecoreError,
        ConfigurationError,
        NotFoundError,
        RateLimitError,
        RequestTimeoutError,
        ServerError,
        ValidationError,
    )
    from britecore_sdk.maps import get_common_regexes, load_regexes
    from britecore_sdk.models import BritecoreContact, BritecorePolicy
    from britecore_sdk.validators import (
        AddressValidator,
        EmailValidator,
        NameValidator,
        PhoneValidator,
        fix_apostrophe_capitalization,
        fix_suffix_capitalization,
        normalize_business_name,
    )


_EXPORT_MAP: dict[str, tuple[str, str]] = {
    "get_api_client": ("britecore_sdk.api.api_calls", "get_api_client"),
    "get_async_api_client": (
        "britecore_sdk.api.api_calls",
        "get_async_api_client",
    ),
    "use_api_client": ("britecore_sdk.api.api_calls", "use_api_client"),
    "COMMON_CITY_REPLACEMENT": (
        "britecore_sdk.constants",
        "COMMON_CITY_REPLACEMENT",
    ),
    "DEFAULT_ADDRESS_TYPE": ("britecore_sdk.constants", "DEFAULT_ADDRESS_TYPE"),
    "DEFAULT_EMAIL_TYPE": ("britecore_sdk.constants", "DEFAULT_EMAIL_TYPE"),
    "DEFAULT_PHONE_TYPE": ("britecore_sdk.constants", "DEFAULT_PHONE_TYPE"),
    "BritecoreError": ("britecore_sdk.exceptions", "BritecoreError"),
    # Flat exception aliases
    "AuthenticationError": ("britecore_sdk.exceptions", "AuthenticationError"),
    "ConfigurationError": ("britecore_sdk.exceptions", "ConfigurationError"),
    "NotFoundError": ("britecore_sdk.exceptions", "NotFoundError"),
    "RateLimitError": ("britecore_sdk.exceptions", "RateLimitError"),
    "RequestTimeoutError": ("britecore_sdk.exceptions", "RequestTimeoutError"),
    "ServerError": ("britecore_sdk.exceptions", "ServerError"),
    "ValidationError": ("britecore_sdk.exceptions", "ValidationError"),
    "load_regexes": ("britecore_sdk.maps", "load_regexes"),
    "get_common_regexes": ("britecore_sdk.maps", "get_common_regexes"),
    "BritecoreContact": ("britecore_sdk.models", "BritecoreContact"),
    "BritecorePolicy": ("britecore_sdk.models", "BritecorePolicy"),
    "AddressValidator": ("britecore_sdk.validators", "AddressValidator"),
    "EmailValidator": ("britecore_sdk.validators", "EmailValidator"),
    "NameValidator": ("britecore_sdk.validators", "NameValidator"),
    "PhoneValidator": ("britecore_sdk.validators", "PhoneValidator"),
    "fix_suffix_capitalization": (
        "britecore_sdk.validators",
        "fix_suffix_capitalization",
    ),
    "fix_apostrophe_capitalization": (
        "britecore_sdk.validators",
        "fix_apostrophe_capitalization",
    ),
    "normalize_business_name": (
        "britecore_sdk.validators",
        "normalize_business_name",
    ),
}


def __getattr__(name: str) -> Any:
    """Lazily resolve convenience exports from their authored modules."""
    try:
        module_name, attribute_name = _EXPORT_MAP[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    value = getattr(import_module(module_name), attribute_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Return package attributes including lazily exported convenience names."""
    return sorted(set(globals()) | set(__all__))


if os.environ.get("BRITECORE_ENV") == "development":
    try:
        from britecore_sdk.utils import check_site_configs

        settings_path = Path(__file__).resolve().parent / "settings" / "settings.toml"
        check_site_configs.warn_if_secrets_in_settings(str(settings_path))
    except Exception:
        pass  # Do not block startup

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
    "AuthenticationError",
    "ConfigurationError",
    "NotFoundError",
    "RateLimitError",
    "RequestTimeoutError",
    "ServerError",
    "ValidationError",
    # Constants
    "DEFAULT_ADDRESS_TYPE",
    "DEFAULT_EMAIL_TYPE",
    "DEFAULT_PHONE_TYPE",
    "COMMON_CITY_REPLACEMENT",
    "load_regexes",
    "get_common_regexes",
    # API client helpers
    "get_api_client",
    "get_async_api_client",
    "use_api_client",
    # Version
    "__version__",
    "logger",
    "configure_logging",
]
