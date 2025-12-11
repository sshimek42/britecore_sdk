"""Email address validation and normalization."""

import re
from typing import Dict, List

from britecore_libraries.constants import DEFAULT_EMAIL_TYPE
from britecore_libraries.maps.britecore_policy_name_map import load_regexes
from britecore_libraries import logger

LOGGER = logger

# Lazy-loaded regex patterns
_COMPILED_REGEXES: Dict = {}


def _get_regexes() -> Dict:
    """Lazy load compiled regexes from maps."""
    global _COMPILED_REGEXES
    if not _COMPILED_REGEXES:
        _COMPILED_REGEXES, _name_groups = load_regexes()
    return _COMPILED_REGEXES


class EmailValidator:
    """
    Email address validation and normalization for BriteCore.

    Handles:
    - Email format validation
    - Email normalization (lowercase, trim)
    - Email type assignment
    """

    def __init__(self, emails: List[Dict[str, str]]) -> None:
        """
        Initialize email validator.

        Args:
            emails: List of email dictionaries with 'email' and 'type' keys
        """
        self.emails = emails

    def process(self) -> List[Dict[str, str]]:
        """
        Process and validate email addresses.

        Returns:
            List of normalized email dictionaries
        """
        email_list = []

        for each_email in self.emails:
            email_address = each_email.get("email", "").lower()
            email_type = each_email.get("type", "")

            # Set default type if empty
            if email_type == "":
                email_type = DEFAULT_EMAIL_TYPE

            normalized = self.normalize_email(email_address)

            # Only add if email is valid
            if normalized:
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

        Args:
            email: Raw email address

        Returns:
            Normalized email address or empty string if invalid

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
        email_match = re.match(email_pattern, email)

        if not email_match:
            if email:
                LOGGER.debug(f"Invalid email address: {email}")
            return ""

        return email_match.group(0)

    @classmethod
    def validate_email(cls, email: str) -> bool:
        """
        Check if email address is valid.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        normalized = cls.normalize_email(email)
        return normalized != ""
