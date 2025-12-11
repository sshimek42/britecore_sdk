"""Address validation and normalization."""

import re
from ast import literal_eval
from typing import Dict, List, Literal

from britecore_libraries.constants import COMMON_CITY_REPLACEMENT, DEFAULT_ADDRESS_TYPE
from britecore_libraries.exceptions import BritecoreError
from britecore_libraries.maps.britecore_policy_name_map import load_regexes
from britecore_libraries.utils.zip_code_lookup import zip_codes
from britecore_libraries import logger

LOGGER = logger

# Reference to zip code data
ZIP_CODE_DF = zip_codes

# Lazy-loaded regex patterns
_COMPILED_REGEXES: Dict = {}


def _get_regexes() -> Dict:
    """Lazy load compiled regexes from maps."""
    global _COMPILED_REGEXES
    if not _COMPILED_REGEXES:
        _COMPILED_REGEXES, _name_groups = load_regexes()
    return _COMPILED_REGEXES


class AddressValidator:
    """
    Address validation and normalization for BriteCore.

    Handles:
    - Address line normalization
    - City/state/zip validation and correction
    - County lookup
    - Street name standardization
    """

    def __init__(self, full_address: Dict[str, str]) -> None:
        """
        Initialize address validator.

        Args:
            full_address: Dictionary containing address components
        """
        self.full_address = full_address
        _get_regexes()

    def process(self) -> List[Dict]:
        """
        Process and validate address.

        Returns:
            List containing single normalized address dictionary

        Raises:
            BritecoreError.InvalidAddress: If address validation fails
        """
        full_address = self.full_address

        if not full_address:
            raise BritecoreError.InvalidAddress("Missing Address")

        if isinstance(self.full_address, str):
            full_address = literal_eval(str(self.full_address)[1:-2])

        # Extract components
        zip_code = full_address.get("address_zip", "").strip()
        address1 = full_address.get("address_line1", "").strip()
        address2 = full_address.get("address_line2", "").strip()
        state = full_address.get("address_state", "").upper()
        county = full_address.get("address_county", "").strip().title()
        city = full_address.get("address_city", "").title().strip()
        property_name = full_address.get("property", "").title().strip()

        # Validate address lines
        if address1 == "" and address2 != "":
            address1 = address2
            address2 = ""
        elif address1 == "":
            raise BritecoreError.InvalidAddress("Missing Address")

        # Lookup missing zip code
        if zip_code == "":
            try:
                zip_code = ZIP_CODE_DF.loc[
                    (
                        (state == ZIP_CODE_DF["admin code1"])
                        & (city == ZIP_CODE_DF["place name"])
                    )
                ]["postal code"].values[0]
                LOGGER.debug(
                    f"Zip code missing - using {zip_code} for city of {city} "
                    f"and state of {state}"
                )
            except IndexError:
                raise BritecoreError.InvalidAddress("Missing Zip Code")

        # Validate and normalize zip code
        zip_code = self.normalize_zipcode(zip_code)

        fixed_address = [
            {
                "address_line1": self.normalize_address_line(address1),
                "address_line2": self.normalize_address_line(address2),
                "address_state": self.validate_state(state, zip_code),
                "address_country": "USA",
                "address_zip": zip_code,
                "type": full_address.get("type", DEFAULT_ADDRESS_TYPE),
                "address_county": self.validate_county(county, zip_code[:5]),
                "address_city": self.validate_city(city, zip_code),
                "property": property_name,
            }
        ]

        LOGGER.debug(f"Created address {fixed_address}")
        return fixed_address

    @classmethod
    def validate_county(cls, county: str, zipcode: str) -> str:
        """Validate and correct county based on zip code."""
        tmp_zipcode = zipcode[:5]
        county_lookup = ZIP_CODE_DF
        county_lookup = county_lookup.loc[county_lookup["postal code"] == tmp_zipcode]

        try:
            county_lookup_value = county_lookup["admin name2"].values[0]
        except IndexError:
            county_lookup_value = ""

        county = COMMON_CITY_REPLACEMENT.get(county, county)

        if county == "" and county_lookup_value != "":
            county = county_lookup_value

        if county_lookup_value.lower() != county.lower() and county != "":
            LOGGER.debug(
                f"County '{county}' not found in zip code '{zipcode}' - "
                f"zip code matches '{county_lookup_value}'"
            )

        return county

    @classmethod
    def validate_city(cls, city: str, zipcode: str) -> str:
        """Validate and correct city based on zip code."""
        city = re.sub(_COMPILED_REGEXES.get("reg_city_state", r""), "", city)

        tmp_zipcode = zipcode[:5]

        city_lookup = ZIP_CODE_DF
        city_lookup = city_lookup.loc[city_lookup["postal code"] == tmp_zipcode]

        try:
            city_lookup_value = city_lookup["place name"].values[0]
        except IndexError:
            city_lookup_value = ""

        city = COMMON_CITY_REPLACEMENT.get(city, city)

        # Normalize common abbreviations
        if city.startswith("St "):
            city = city.replace("St ", "Saint ", 1)
        if city.startswith("Mt "):
            city = city.replace("Mt ", "Mount ", 1)

        if city == "" and city_lookup_value != "":
            city = city_lookup_value

        if city_lookup_value.lower() != city.lower() and city != "":
            LOGGER.debug(
                f"City %f.yellow%'{city}%f%' not found in zip code %f.yellow%'{zipcode}'%f% - "
                f"zip code matches %f.yellow%'{city_lookup_value}'%f% - no changes made"
            )

        return city

    @staticmethod
    def normalize_zipcode(zipcode: str) -> str:
        """Normalize and validate zip code format."""
        zipcode = zipcode.strip().replace("-", "").zfill(5)

        if zipcode == "00000" or len(zipcode) > 10 or not zipcode.isnumeric():
            raise BritecoreError.InvalidAddress(f"Invalid Zip Code - {zipcode}")

        zipcode = re.sub(_COMPILED_REGEXES.get("reg_zip", r""), "", zipcode)

        if len(zipcode) > 5:
            zipcode = zipcode[:5] + "-" + zipcode[5:]

        return zipcode

    @classmethod
    def validate_state(cls, state: str, zipcode: str) -> str:
        """Validate and correct state based on zip code."""
        state = state.strip().upper()
        state = re.sub(_COMPILED_REGEXES.get("reg_city_state", r""), "", state)

        tmp_zipcode = zipcode[:5]

        state_lookup = ZIP_CODE_DF
        state_lookup = state_lookup.loc[state_lookup["postal code"] == tmp_zipcode]

        try:
            state_lookup_value = state_lookup["admin code1"].values[0]
        except IndexError:
            state_lookup_value = ""

        if state == "" and state_lookup_value != "":
            state = state_lookup_value

        if state_lookup_value.lower() != state.lower() and state != "":
            LOGGER.debug(
                f"State '{state}' not found in zip code '{zipcode}' - "
                f"zip code matches '{state_lookup_value}'"
            )
            state = "WI"  # Default fallback

        return state

    @staticmethod
    def _normalize_street_name(address: str) -> str | bytes | Literal[""]:
        """Normalize street abbreviations and directions."""
        street_replacements = _COMPILED_REGEXES.get("street_name_replacement", {})

        for pattern, replacement in street_replacements.items():
            address = re.sub(pattern, replacement, address)

        if address != "" and not address[-1].isalnum():
            address = address[:-1]

        return address

    @staticmethod
    def _normalize_street_casing(address: str) -> str:
        """Fix street capitalization quirks (11Th -> 11th, Highway Bb -> Highway BB)."""
        # Fix number streets (11Th -> 11th)
        address = re.sub(r"\s\d..\s*", lambda mo: mo.group(0).lower(), address)

        # Fix doubled letters (Highway BB)
        address = re.sub(
            r"\b(.)\1{1,2}",
            lambda mo: mo.group(0).upper(),
            address,
            0,
            re.IGNORECASE,
        )

        # Fix last character if preceded by space
        if len(address) >= 3 and address[-3:-2].lower() == " ":
            address = address[:-1] + address[-1:].upper()

        return address

    @staticmethod
    def _remove_repeated_punctuation(address: str) -> str:
        """Remove repeated non-alphanumeric characters."""
        reg_dbl_non_letter = r"(\W+|\s..)\1"
        if re.search(reg_dbl_non_letter, address):
            match = re.search(reg_dbl_non_letter, address)
            if match:
                replace_char = match.group(1)[-1]
                address = re.sub(reg_dbl_non_letter, replace_char, address)
        return address

    @classmethod
    def normalize_address_line(cls, address: str | bytes | Literal[""]) -> str:
        """
        Comprehensive address line normalization.

        Args:
            address: Address line to normalize

        Returns:
            Normalized address line
        """
        address = address.strip().title()
        if address == "":
            return ""

        # Skip special formats (e.g., tax parcel IDs)
        if re.search(r"^T:\d", address):
            return address

        # Remove repeated punctuation
        address = cls._remove_repeated_punctuation(address)

        # Remove illegal characters
        address = re.sub(_COMPILED_REGEXES.get("reg_address", r""), "", address)

        # Normalize street names
        address = cls._normalize_street_name(address)
        address = cls._normalize_street_casing(address)

        # Remove business tokens from address lines
        address = re.sub(_COMPILED_REGEXES.get("reg_address2", r""), "", address)

        # Collapse multiple spaces
        address = re.sub(r"\s{2,}", " ", address).strip()

        return address


def normalize_business_name(business_name: str):
    """
    Fix capitalization for business suffix tokens (LLC, LLP, DBA).

    Args:
        business_name: Contact name to fix.

    Returns:
        Name with standardized capitalization for business suffixes.
    """
    check_business = re.findall(
        _COMPILED_REGEXES.get("reg_business_name", ""), business_name
    )
    if check_business:
        for each_business in check_business:
            business_name = business_name.replace(
                each_business,
                f"{each_business.upper().strip().replace(' ', '')}",
            )

    return business_name


def fix_apostrophe_capitalisation(name: str) -> str:
    """Fixes capitalization on names with apostrophe (Karen'S to Karen's)
    Also adds escape character for SQL insert
    :param name: Name to fix
    :return: Fixed name
    """
    name = re.sub(
        _COMPILED_REGEXES.get("reg_double_apostrophe", ""),
        lambda mo: mo.group(0).lower(),
        name,
    )
    return name


def fix_suffix_capitalisation(suffix: str) -> str:
    """Check for repeated letters in suffix and capitalize if necessary
    :param suffix: Suffix
    :return: suffix
    """
    count = {}
    suffix_lower = suffix.lower()
    if suffix_lower == "iv":
        suffix = suffix.upper()
    else:
        for s in suffix_lower:
            if s in count:
                count[s] += 1
            else:
                count[s] = 1
        for key in count:
            if count[key] > 2:
                suffix = suffix.upper()
    return suffix
