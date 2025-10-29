
"""Shared constants for BriteCore library."""

from typing import Dict

# Default types for contact information
DEFAULT_ADDRESS_TYPE: str = "Mailing/Billing"
DEFAULT_PHONE_TYPE: str = "Home"
DEFAULT_EMAIL_TYPE: str = "Home"

# City name replacements for known inconsistencies
COMMON_CITY_REPLACEMENT: Dict[str, str] = {
    "Depere": "De Pere"
}
