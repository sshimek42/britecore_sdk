"""Shared constants for BriteCore library."""

# Default types for contact information
DEFAULT_ADDRESS_TYPE: str = "Mailing/Billing"
DEFAULT_PHONE_TYPE: str = "Home"
DEFAULT_EMAIL_TYPE: str = "Personal"

# City name replacements for known inconsistencies
COMMON_CITY_REPLACEMENT: dict[str, str] = {"Depere": "De Pere"}
