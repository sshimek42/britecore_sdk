"""Name validation and normalization utilities."""

import re
from typing import Pattern

from britecore_libraries.maps.britecore_policy_name_map import load_regexes

# Lazy-loaded from maps if needed
_BUSINESS_NAME_REGEX: Pattern | None = None
_COMPILED_REGEXES: dict[str, Pattern[str]] = {}


def _get_regexes() -> dict[str, Pattern[str]]:
    """Lazy load compiled regexes from maps."""
    global _COMPILED_REGEXES
    if not _COMPILED_REGEXES:
        _COMPILED_REGEXES, _name_groups = load_regexes()
    return _COMPILED_REGEXES


def _get_business_name_regex() -> Pattern:
    """Lazy load business name regex from maps."""
    global _BUSINESS_NAME_REGEX
    _get_regexes()
    _BUSINESS_NAME_REGEX = _COMPILED_REGEXES.get("reg_business_name")
    return _BUSINESS_NAME_REGEX


class NameValidator:
    """Utilities for validating and normalizing contact names."""

    @staticmethod
    def normalize_business_name(name: str) -> str:
        """
        Normalize business suffix capitalization (LLC, LLP, DBA, etc.).

        Args:
            name: Contact name to normalize

        Returns:
            Name with standardized business suffix capitalization

        Example:
            >>> NameValidator.normalize_business_name("ABC Company llc")
            "ABC Company LLC"
        """
        regex = _get_business_name_regex()
        matches = re.findall(regex, name)

        for match in matches:
            normalized = match.upper().strip().replace(" ", "")
            name = name.replace(match, normalized)

        return name

    @staticmethod
    def normalize_apostrophe(name: str) -> str:
        """
        Fix capitalization after apostrophes (Karen'S -> Karen's).

        Args:
            name: Name to normalize

        Returns:
            Name with proper apostrophe capitalization
        """
        # This would need the regex from compiled_regexes
        # For now, simple implementation
        return re.sub(r"'([A-Z])", lambda m: f"'{m.group(1).lower()}", name)

    @staticmethod
    def normalize_suffix(suffix: str) -> str:
        """
        Normalize name suffixes (Jr, Sr, III, IV, etc.).

        Args:
            suffix: Suffix to normalize

        Returns:
            Properly capitalized suffix
        """
        suffix_lower = suffix.lower()

        if suffix_lower == "iv":
            return suffix.upper()

        # Check for repeated letters (III, II)
        char_counts = {}
        for char in suffix_lower:
            char_counts[char] = char_counts.get(char, 0) + 1

        # If any character repeats more than 2 times, uppercase entire suffix
        if any(count > 2 for count in char_counts.values()):
            return suffix.upper()

        return suffix
