"""Phone number validation and normalization."""

import logging
import re
from typing import Dict, List, Optional

import sclogging.sclogging_main as scl

from britecore_libraries.constants import DEFAULT_PHONE_TYPE
from britecore_libraries.maps.britecore_policy_name_map import load_regexes

_LOGGER: logging.Logger = scl.get_parent_logger()

# Lazy-loaded regex patterns
_COMPILED_REGEXES: Dict = {}


def _get_regexes() -> Dict:
    """Lazy load compiled regexes from maps."""
    global _COMPILED_REGEXES
    if not _COMPILED_REGEXES:
        _COMPILED_REGEXES, _name_groups = load_regexes()
    return _COMPILED_REGEXES


class PhoneValidator:
    """
    Phone number validation and normalization for BriteCore.

    Handles:
    - Phone number format normalization
    - Invalid phone number filtering
    - Phone type assignment
    """

    def __init__(self, phone_numbers: List[Dict[str, str]]) -> None:
        """
        Initialize phone validator.

        Args:
            phone_numbers: List of phone number dictionaries with 'phone' and 'type' keys
        """
        self.phone_numbers = phone_numbers

    def process(self) -> List[Dict[str, str]]:
        """
        Process and validate phone numbers.

        Returns:
            List of normalized phone number dictionaries
        """
        phone_number_list = []

        for each_phone in self.phone_numbers:
            phone_number = each_phone.get("phone", "")
            phone_type = each_phone.get("type", "")

            # Set default type if empty
            if phone_type == "":
                phone_type = DEFAULT_PHONE_TYPE

            # Skip invalid/empty phone numbers
            if self._is_invalid_phone(phone_number):
                continue

            normalized = self.normalize_phone(phone_number)

            # Only add if normalization succeeded
            if normalized:
                phone_number_list.append(
                    {
                        "phone": normalized,
                        "type": phone_type,
                    }
                )

        return phone_number_list

    @staticmethod
    def _is_invalid_phone(phone: str) -> bool:
        """
        Check if phone number should be skipped.

        Args:
            phone: Phone number to check

        Returns:
            True if phone should be skipped, False otherwise
        """
        if not phone:
            return True

        phone_stripped = phone.strip()

        # Skip obviously invalid values
        if phone_stripped in ("", "0", "-"):
            return True

        return False

    @staticmethod
    def normalize_phone(phone: str) -> Optional[str]:
        """
        Normalize phone number to standard format: 1-###-###-####.

        Args:
            phone: Raw phone number string

        Returns:
            Normalized phone number or None if invalid

        Example:
            >>> PhoneValidator.normalize_phone("(920) 555-1234")
            "1-920-555-1234"
            >>> PhoneValidator.normalize_phone("555-1234")
            None
        """
        regexes = _get_regexes()

        # Remove all non-numeric characters
        phone_pattern = regexes.get("reg_phone", r"[^0-9]")
        phone = re.sub(phone_pattern, "", phone)

        # Validate: must be exactly 10 digits and numeric
        if len(phone) != 10 or not phone.isnumeric():
            return None

        # Format: 1-###-###-####
        phone = f"1-{phone[:3]}-{phone[3:6]}-{phone[6:]}"

        return phone

    @classmethod
    def validate_phone(cls, phone: str) -> bool:
        """
        Check if phone number is valid.

        Args:
            phone: Phone number to validate

        Returns:
            True if valid, False otherwise
        """
        if cls._is_invalid_phone(phone):
            return False

        normalized = cls.normalize_phone(phone)
        return normalized is not None
