"""Address validation and normalization."""

import re
from ast import literal_eval
from re import Pattern
from typing import Any

from britecore_libraries import logger
from britecore_libraries.constants import COMMON_CITY_REPLACEMENT, DEFAULT_ADDRESS_TYPE
from britecore_libraries.exceptions import BritecoreError
from britecore_libraries.maps import load_regexes
from britecore_libraries.utils.zip_code_lookup import zip_codes

LOGGER = logger
FIX_ADDRESS = False
NO_ADDRESS_CHANGE = "NO CHANGES MADE"
ADDRESS_CHANGE = "ADDRESS UPDATED"

# Reference to zip code data
ZIP_CODE_LOOKUP = zip_codes
# Backward-compatible alias retained for external imports.
ZIP_CODE_DF = ZIP_CODE_LOOKUP

# Valid US state/territory abbreviations
VALID_US_STATES: frozenset[str] = frozenset(
    {
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "OR",
        "PA",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
        "DC",
        "PR",
        "VI",
        "GU",
        "AS",
        "MP",
    }
)

# Lazy-loaded regex patterns
_COMPILED_REGEXES: dict[str | Any, Pattern[str] | Any] = {}


def _get_regexes() -> dict[str | Any, Pattern[str] | Any]:
    """
    Retrieves compiled regular expressions used for parsing and processing.

    This function manages a global cache of compiled regular expressions to avoid
    recompiling them on each call. It initializes the cache if it hasn't been
    populated yet by calling the load_regexes() function.

    Returns:
        Dict: A dictionary containing compiled regular expressions that can be
            used for pattern matching and text processing operations.
    """
    global _COMPILED_REGEXES
    if not _COMPILED_REGEXES:
        _COMPILED_REGEXES, _name_groups = load_regexes()
    return _COMPILED_REGEXES


class AddressValidator:
    """
    Validates and normalizes address information.

    This class processes address components to ensure they meet validation
    criteria and are properly formatted. It handles zip code lookup, state
    and city validation, and normalizes address line formatting.

    Attributes:
        full_address: Dictionary containing address components to be validated
    """

    def __init__(self, full_address: dict[str, str]) -> None:
        """

        Initialize the object with a full address dictionary.

        This constructor sets up the instance with the provided full address
        and initializes any necessary regex patterns for address parsing.

        Args:
            full_address: A dictionary containing address components with string keys
                          and string values representing the full address information.

        """
        self.full_address = full_address
        _get_regexes()

    def process(self) -> list[dict[str, str]]:
        """
        Processes and validates address components from a full address dictionary.

        This method extracts individual address components such as zip code, street lines,
        state, county, city, and property name from the full address. It performs validation
        on the address lines and ensures that missing zip codes are looked up using a
        ZIP lookup index. The method also normalizes and validates the extracted values
        before returning a standardized address dictionary.

        The method raises BritecoreError.InvalidAddress if the address is missing or
        invalid, particularly when required fields like address line 1 are absent or
        when a zip code cannot be determined.

        Returns:
            list[dict[str, str]]: A list containing a single dictionary with standardized
            address components including address_line1, address_line2, address_state,
            address_country, address_zip, type, address_county, address_city, and property.
        """
        full_address = self.full_address

        if not full_address:
            raise BritecoreError.InvalidAddress("Missing Address")

        if isinstance(self.full_address, str):
            try:
                # Handle various string representations of dicts
                # Try: direct evaluation first (standard dict string repr)
                try:
                    full_address = literal_eval(self.full_address)
                except (ValueError, SyntaxError):
                    # Fallback: Try with slicing (for edge cases like "({'key': 'value'})")
                    full_address = literal_eval(str(self.full_address)[1:-2])

                if not isinstance(full_address, dict):
                    raise BritecoreError.InvalidAddress(
                        "Address must be a dictionary"
                    )
            except (ValueError, SyntaxError) as e:
                raise BritecoreError.InvalidAddress(
                    f"Invalid address format: {str(e)}"
                ) from e

        # Extract components, supporting both canonical keys and short aliases
        zip_code = (
            full_address.get("address_zip") or full_address.get("zip", "")
        ).strip()
        address1 = (
            full_address.get("address_line1") or full_address.get("street", "")
        ).strip()
        address2 = (full_address.get("address_line2", "")).strip()
        state = (
            full_address.get("address_state") or full_address.get("state", "")
        ).upper()
        county = (
            (full_address.get("address_county") or full_address.get("county", ""))
            .strip()
            .title()
        )
        city = (
            (full_address.get("address_city") or full_address.get("city", ""))
            .title()
            .strip()
        )
        property_name = full_address.get("property", "").title().strip()

        # Validate address lines
        if address1 == "" and address2 != "":
            address1 = address2
            address2 = ""
        elif address1 == "":
            raise BritecoreError.InvalidAddress("Missing Address")

        # Lookup missing zip code
        if zip_code == "":
            zip_code = ZIP_CODE_LOOKUP.get_zip_by_state_city(state, city)
            if zip_code:
                LOGGER.warning(
                    f"Zip code missing - using {zip_code} for city of {city} "
                    f"and state of {state}"
                )
            else:
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
        """
        Validates and returns the county name based on the provided county string and zipcode.

        This method performs validation of the county name by checking against a lookup table
        using the first five digits of the zipcode. It handles cases where the county might
        be missing or different from the zip code lookup, and applies common city replacements
        when necessary.

        Parameters:
            county (str): The county name to validate
            zipcode (str): The zipcode to use for lookup validation

        Returns:
            str: The validated county name, which may be the original county name,
                 a replacement from common city replacements, or the county name from
                 the zip code lookup table
        """
        county_lookup = ZIP_CODE_LOOKUP.get_record_by_zip(zipcode)
        county_lookup_value = county_lookup.admin_name2 if county_lookup else ""

        county = COMMON_CITY_REPLACEMENT.get(county, county)

        if county == "" and county_lookup_value != "":
            county = county_lookup_value

        if county_lookup_value.lower() != county.lower() and county != "":
            log_string = (
                f"County '{county}' not found in zip code '{zipcode}' "
                f"- zip code matches '{county_lookup_value}'"
            )

            if FIX_ADDRESS:
                county = county_lookup_value
                LOGGER.info(f"{log_string} - {ADDRESS_CHANGE}")
            else:
                LOGGER.debug(f"{log_string} - {NO_ADDRESS_CHANGE}")

        return county

    @classmethod
    def validate_city(cls, city: str, zipcode: str) -> str:
        """
        Validates and normalizes a city name based on provided zipcode data.

        This method processes the input city name by removing certain regex patterns,
        checking against a zip code lookup table, and applying common replacements
        and abbreviations normalization. If the city name is not found in the lookup
        table, it will attempt to use the matched city from the zip code data.

        Parameters:
            city (str): The city name to validate and normalize.
            zipcode (str): The zip code associated with the city for lookup purposes.

        Returns:
            str: The validated and normalized city name. If no match is found in the
            lookup table, the original city name is returned after processing.
        """
        city = re.sub(_COMPILED_REGEXES.get("reg_city_state", r""), "", city)

        city_lookup = ZIP_CODE_LOOKUP.get_record_by_zip(zipcode)
        city_lookup_value = city_lookup.place_name if city_lookup else ""

        city = COMMON_CITY_REPLACEMENT.get(city, city)

        # Normalize common abbreviations
        if city.startswith("St "):
            city = city.replace("St ", "Saint ", 1)
        if city.startswith("Mt "):
            city = city.replace("Mt ", "Mount ", 1)

        if city == "" and city_lookup_value != "":
            city = city_lookup_value

        if city_lookup_value.lower() != city.lower() and city != "":
            log_string = (
                f"City '{city}' not found in zip code '{zipcode}' "
                f"- zip code matches '{city_lookup_value}'"
            )

            if FIX_ADDRESS:
                city = city_lookup_value
                LOGGER.info(f"{log_string} - {ADDRESS_CHANGE}")
            else:
                LOGGER.debug(f"{log_string} - {NO_ADDRESS_CHANGE}")
        return city

    @staticmethod
    def normalize_zipcode(zipcode: str) -> str:
        """
        Normalizes a zip code string to a standard 5-digit format or 5-digit+4-digit format.

        This static method processes a zip code string by removing hyphens, padding with
        leading zeros if necessary, and validating the format. It handles various input
        formats and ensures the output conforms to standard zip code formatting rules.

        Parameters:
            zipcode (str): The zip code string to normalize. May contain hyphens,
                           spaces, or be improperly padded.

        Returns:
            str: The normalized zip code in either 5-digit format (e.g., "12345") or
                 5-digit+4-digit format (e.g., "12345-6789").

        Raises:
            BritecoreError.InvalidAddress: If the zip code is invalid due to:
                - Being exactly "00000"
                - Having more than 10 digits
                - Containing non-numeric characters after cleaning
        """
        zipcode = zipcode.strip().replace("-", "").zfill(5)

        if zipcode == "00000" or len(zipcode) > 10 or not zipcode.isnumeric():
            raise BritecoreError.InvalidAddress(f"Invalid Zip Code - {zipcode}")

        zipcode = re.sub(_COMPILED_REGEXES.get("reg_zip", r""), "", zipcode)

        if len(zipcode) > 5:
            zipcode = zipcode[:5] + "-" + zipcode[5:]

        return zipcode

    @classmethod
    def validate_state(cls, state: str, zipcode: str) -> str:
        """
        Validates and corrects a state abbreviation based on postal code lookup.

        This method processes a state string by normalizing it and attempts to
        validate it against a postal code database. If the state cannot be
        validated, a default fallback is applied.

        Parameters:
            state (str): The state abbreviation to validate, may contain
                whitespace or special characters
            zipcode (str): The postal code used for validation lookup

        Returns:
            str: The validated state abbreviation, potentially corrected
                based on postal code database or default fallback

        Notes:
            This method uses a global ZIP code lookup index for lookups and
            a global LOGGER for debug output. The method applies regex
            normalization to the state string before lookup.
        """
        state = state.strip().upper()
        state = re.sub(_COMPILED_REGEXES.get("reg_city_state", r""), "", state)

        # Reject state codes that are not valid US state/territory abbreviations
        if state and state not in VALID_US_STATES:
            raise BritecoreError.InvalidAddress(f"Invalid State - {state}")

        state_lookup = ZIP_CODE_LOOKUP.get_record_by_zip(zipcode)
        state_lookup_value = state_lookup.admin_code1 if state_lookup else ""

        if state == "" and state_lookup_value != "":
            state = state_lookup_value

        if state_lookup_value.lower() != state.lower() and state != "":
            log_string = (
                f"State '{state}' not found in zip code '{zipcode}' "
                f"- zip code matches '{state_lookup_value}'"
            )

            if FIX_ADDRESS:
                state = state_lookup_value
                LOGGER.info(f"{log_string} - {ADDRESS_CHANGE}")
            else:
                LOGGER.debug(f"{log_string} - {NO_ADDRESS_CHANGE}")
                state = "WI"  # Default fallback

        return state

    @staticmethod
    def _normalize_street_name(address: str) -> str:
        """
        Normalizes street names in addresses by applying regex replacements.

        This static method processes an address string to normalize street names
        by applying a series of regex substitutions defined in the street name
        replacements dictionary. It also handles trailing non-alphanumeric characters
        in the normalized address.

        Parameters:
            address (str): The input address string to normalize

        Returns:
            str: The normalized address string, or empty string if input is empty
        """
        street_replacements = _COMPILED_REGEXES.get("street_name_replacement", {})

        pattern: Pattern[str]
        replacement: str

        for pattern, replacement in street_replacements.items():
            address = re.sub(pattern, replacement, address)

        if address != "" and not address[-1].isalnum():
            address = address[:-1]

        return str(address)

    @staticmethod
    def _normalize_street_casing(address: str) -> str:
        """
        Normalizes street casing in address strings.

        This static method applies several normalization rules to street address
        strings to ensure consistent formatting. It handles number street
        capitalization, removes excessive letter repetitions, and corrects
        capitalization of the last character when preceded by a space.

        Parameters:
            address (str): The input address string to normalize

        Returns:
            str: The normalized address string with consistent casing
        """
        # Fix number streets (11Th -> 11th)
        address = re.sub(r"\s\d..\s*", lambda mo: mo.group(0).lower(), address)

        # Fix doubled letters (Highway BB)
        address = re.sub(
            r"\b(.)\1{1,2}",
            lambda mo: mo.group(0).upper(),
            address,
            count=0,
            flags=re.IGNORECASE,
        )

        # Fix last character if preceded by space
        if len(address) >= 3 and address[-3:-2].lower() == " ":
            address = address[:-1] + address[-1:].upper()

        return address

    @staticmethod
    def _remove_repeated_punctuation(address: str) -> str:
        """
        Remove repeated punctuation from address string.

        This static method identifies and removes repeated punctuation characters
        or sequences of non-letter characters that appear consecutively in the
        address string. It uses a regular expression pattern to detect duplicate
        non-letter characters and replaces them with a single instance of the
        last character in the repeated sequence.

        Parameters:
            address (str): The input address string that may contain repeated
                        punctuation characters

        Returns:
            str: The address string with repeated punctuation characters
                 removed, leaving only single instances of consecutive
                 non-letter characters
        """
        reg_dbl_non_letter: str = r"(\W+|\s..)\1"
        if re.search(reg_dbl_non_letter, address):
            match = re.search(reg_dbl_non_letter, address)
            if match:
                replace_char = match.group(1)[-1]
                address = re.sub(reg_dbl_non_letter, replace_char, address)
        return address

    @classmethod
    def normalize_address_line(cls, address: str) -> str:
        """
        Normalize an address line by applying multiple cleaning and formatting operations.

        This method processes an address string by stripping whitespace, converting to title case,
        and applying various normalization rules including removal of repeated punctuation,
        illegal characters, and business tokens. Special formats like tax parcel IDs are preserved
        as-is. Street names are normalized and casing is adjusted. Multiple spaces are collapsed
        into single spaces.

        Parameters:
            address (str): The address string to normalize

        Returns:
            str: The normalized address string
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
        address = str(cls._normalize_street_name(address))
        address = cls._normalize_street_casing(address)

        # Remove business tokens from address lines
        address = re.sub(_COMPILED_REGEXES.get("reg_address2", r""), "", address)

        # Collapse multiple spaces
        address = re.sub(r"\s{2,}", " ", address).strip()

        return address


def normalize_business_name(business_name: str) -> str:
    """
    Fix capitalization for business suffix tokens (LLC, LLP, DBA).

    Args:
        business_name (str): Contact name to fix.

    Returns:
        str: Name with standardized capitalization for business suffixes.
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


def fix_apostrophe_capitalization(name: str) -> str:
    """
    Fix apostrophe capitalization in a given name string.

    This function processes a name string to ensure that double apostrophes
    are properly lowercased, which helps maintain consistent formatting
    across different name representations.

    Parameters:
        name (str): The input name string that may contain double apostrophes
                    which need capitalization correction.

    Returns:
        str: The processed name string with double apostrophes converted to
             lowercase format.
    """
    name = re.sub(
        _COMPILED_REGEXES.get("reg_double_apostrophe", ""),
        lambda mo: mo.group(0).lower(),
        name,
    )
    return name


def fix_suffix_capitalization(suffix: str) -> str:
    """
    Fix capitalization of suffix string based on specific rules.

    This function processes a suffix string to determine appropriate capitalization.
    If the suffix is "iv", it is converted to uppercase. For other suffixes, the
    function analyzes character frequency and converts the entire suffix to uppercase
    if any character appears more than twice.

    Parameters:
        suffix (str): The suffix string to process

    Returns:
        str: The suffix with adjusted capitalization according to the rules
    """
    count: dict[Any, Any] = {}
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
