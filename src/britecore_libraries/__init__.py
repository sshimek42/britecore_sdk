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

from britecore_libraries.base_logger import get_logger

logger = get_logger(__package__, level="INFO", log_to_file=True, log_file_level="INFO")

try:
    __version__ = version("britecore_libraries")
except PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

if TYPE_CHECKING:
    from britecore_libraries.api.api_calls import get_api_client, get_async_api_client
    from britecore_libraries.constants import (
        COMMON_CITY_REPLACEMENT,
        DEFAULT_ADDRESS_TYPE,
        DEFAULT_EMAIL_TYPE,
        DEFAULT_PHONE_TYPE,
    )
    from britecore_libraries.exceptions import BritecoreError
    from britecore_libraries.maps import get_common_regexes, load_regexes
    from britecore_libraries.models import BritecoreContact, BritecorePolicy
    from britecore_libraries.validators import (
        AddressValidator,
        EmailValidator,
        NameValidator,
        PhoneValidator,
        fix_apostrophe_capitalization,
        fix_suffix_capitalization,
        normalize_business_name,
    )


_EXPORT_MAP: dict[str, tuple[str, str]] = {
    "get_api_client": ("britecore_libraries.api.api_calls", "get_api_client"),
    "get_async_api_client": (
        "britecore_libraries.api.api_calls",
        "get_async_api_client",
    ),
    "COMMON_CITY_REPLACEMENT": (
        "britecore_libraries.constants",
        "COMMON_CITY_REPLACEMENT",
    ),
    "DEFAULT_ADDRESS_TYPE": ("britecore_libraries.constants", "DEFAULT_ADDRESS_TYPE"),
    "DEFAULT_EMAIL_TYPE": ("britecore_libraries.constants", "DEFAULT_EMAIL_TYPE"),
    "DEFAULT_PHONE_TYPE": ("britecore_libraries.constants", "DEFAULT_PHONE_TYPE"),
    "BritecoreError": ("britecore_libraries.exceptions", "BritecoreError"),
    "load_regexes": ("britecore_libraries.maps", "load_regexes"),
    "get_common_regexes": ("britecore_libraries.maps", "get_common_regexes"),
    "BritecoreContact": ("britecore_libraries.models", "BritecoreContact"),
    "BritecorePolicy": ("britecore_libraries.models", "BritecorePolicy"),
    "AddressValidator": ("britecore_libraries.validators", "AddressValidator"),
    "EmailValidator": ("britecore_libraries.validators", "EmailValidator"),
    "NameValidator": ("britecore_libraries.validators", "NameValidator"),
    "PhoneValidator": ("britecore_libraries.validators", "PhoneValidator"),
    "fix_suffix_capitalization": (
        "britecore_libraries.validators",
        "fix_suffix_capitalization",
    ),
    "fix_apostrophe_capitalization": (
        "britecore_libraries.validators",
        "fix_apostrophe_capitalization",
    ),
    "normalize_business_name": (
        "britecore_libraries.validators",
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
        from britecore_libraries.utils import check_site_configs

        settings_path = Path(__file__).resolve().parent / "config" / "settings.toml"
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
    # Version
    "__version__",
    "logger",
]
