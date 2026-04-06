"""Phone number validation and normalization."""

import re
from re import Pattern

from britecore_libraries.constants import DEFAULT_PHONE_TYPE
from britecore_libraries.exceptions import BritecoreError
from britecore_libraries.maps.britecore_policy_name_map import load_regexes

# Lazy-loaded regex patterns
_COMPILED_REGEXES: dict[str, Pattern[str]] = {}


def _get_regexes() -> dict[str, Pattern[str]]:
    """
    Retrieve compiled regex patterns for parsing.

    This function returns a dictionary of pre-compiled regular expressions
    used for parsing various components of the input data. The regex patterns
    are loaded once and cached for subsequent calls to improve performance.

    Returns:
        dict[str, Pattern[str]]: A dictionary mapping regex pattern names to
        their compiled regular expression objects.
    """
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

    def __init__(self, phone_numbers: list[dict[str, str]]) -> None:
        """
        Initialize phone validator.

        Parameters:
            phone_numbers (list[dict[str,str]]): List of phone number dictionaries with 'phone' and 'type' keys
        """
        self.phone_numbers = phone_numbers

    def process(self) -> list[dict[str, str]]:
        """
        Process and validate phone numbers.

        Returns:
            list[dict[str, str]]: List of normalized phone number dictionaries
        """
        phone_number_list: list[dict[str, str]] = []

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

            # Raise if phone is present but invalid
            if not normalized:
                raise BritecoreError.InvalidPhoneNumber(
                    f"Invalid phone number: {phone_number}"
                )

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

        Parameters:
            phone (str): Phone number to check

        Returns:
            bool: True if phone should be skipped, False otherwise
        """
        if not phone:
            return True

        phone_stripped = phone.strip()

        # Skip obviously invalid values
        if phone_stripped in ("", "0", "-"):
            return True

        return False

    @staticmethod
    def normalize_phone(phone: str) -> str | None:
        """
        Normalize phone number to standard format: 1-###-###-####.

        Parameters:
            phone (str): Raw phone number string

        Returns:
            Optional[str]: Normalized phone number or None if invalid

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

        Parameters:
            phone (str): Phone number to validate

        Returns:
            bool: True if valid, False otherwise
        """
        if cls._is_invalid_phone(phone):
            return False

        normalized = cls.normalize_phone(phone)
        return normalized is not None
