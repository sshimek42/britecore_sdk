"""Email address validation and normalization."""

import logging
import re
from functools import lru_cache
from re import Pattern
from typing import Any

from britecore_libraries.constants import DEFAULT_EMAIL_TYPE
from britecore_libraries.exceptions import BritecoreError
from britecore_libraries.maps import get_common_regexes

LOGGER = logging.getLogger("britecore_libraries")


@lru_cache(maxsize=1)
def _get_regexes() -> dict[str | Any, Pattern[str] | Any]:
    """
    Retrieves compiled regular expressions used for parsing and validation.

    This function manages a global cache of compiled regular expressions to avoid
    recompiling them on each call. It initializes the cache if it hasn't been
    populated yet by calling the get_common_regexes() function.

    Returns:
        dict[str | Any, Pattern[str] | Any]: A dictionary containing compiled
        regular expressions keyed by their names or identifiers.
    """
    return get_common_regexes()


class EmailValidator:
    """
    Validates and normalizes email addresses.

    Provides functionality to process a list of email dictionaries, normalize
    email addresses, and validate their format. Supports setting default email
    types and filtering out invalid entries.
    """

    def __init__(self, emails: list[dict[str, str]]) -> None:
        """
        Initialize email validator.

        Parameters:
            emails (list[dict[str,str]]): List of email dictionaries with 'email' and 'type' keys
        """
        self.emails = emails

    def process(self) -> list[dict[str, str]]:
        """
        Process and validate email addresses.

        Returns:
            list[dict[str, str]]: List of normalized email dictionaries
        """
        email_list: list[dict[str, str]] = []

        for each_email in self.emails:
            email_address = each_email.get("email", "").lower()
            email_type = each_email.get("type", "")

            # Set default type if empty
            if email_type == "":
                email_type = DEFAULT_EMAIL_TYPE

            normalized = self.normalize_email(email_address)

            # Raise if email is present but invalid
            if not normalized:
                if email_address:
                    raise BritecoreError.InvalidEmailAddress(
                        f"Invalid email address: {email_address}"
                    )
                continue

            email_list.append(
                {
                    "email": normalized,
                    "type": email_type,
                }
            )

        return email_list

    @staticmethod
    def normalize_email(email: str) -> str:
        """
        Normalize and validate email address.

        Parameters:
            email (str): Raw email address

        Returns:
            str: Normalized email address or empty string if invalid

        Example:
            >>> EmailValidator.normalize_email("  User@Example.COM  ")
            "user@example.com"
            >>> EmailValidator.normalize_email("invalid-email")
            ""
        """
        regexes = _get_regexes()

        # Strip and lowercase
        email = email.strip().lower()

        # Validate format
        email_pattern = regexes.get("reg_email")
        if not isinstance(email_pattern, (str, Pattern)):
            return ""
        email_match = re.match(email_pattern, email)

        if not email_match:
            if email:
                LOGGER.debug("Invalid email address: %s", email)
            return ""

        return email_match.group(0)

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """
        Check if email address is valid.

        Parameters:
            email (str): Email address to validate

        Returns:
            bool: True if valid, False otherwise
        """
        normalized = cls.normalize_email(email)
        return normalized != ""
