"""Class definition and methods for Britecore contacts"""

import datetime
import logging
import os
import re
from ast import literal_eval
from typing import Dict, Literal, Optional

from classes.britecore_exceptions import BritecoreError
from maps.britecore_field_map import (
    field_map_to_britecore,
    field_map_to_named_insured,
    field_map_to_risk_location,
)
from maps.britecore_policy_map import britecore_policy_type_map, policy_map
from maps.britecore_policy_name_map import compiled_regexes
from sclogging import sclogging_main as scl
from utils.zip_code_lookup import zip_codes

_LOGGER: logging.Logger = scl.get_parent_logger()

MUTUAL_SYSTEM = os.environ.get("system")

FIELD_MAP_TO_BRITECORE = field_map_to_britecore
FIELD_MAP_TO_NAMED_INSURED = field_map_to_named_insured
FIELD_MAP_TO_RISK_LOCATION = field_map_to_risk_location

DEFAULT_ADDRESS_TYPE: str = "Mailing/Billing"
DEFAULT_PHONE_TYPE: str = "Home"
DEFAULT_EMAIL_TYPE: str = "Home"

COMMON_CITY_REPLACEMENT: Dict[str, str] = {"Depere": "De Pere"}

ZIP_CODE_DF = zip_codes

COMPILED_REGEXES = compiled_regexes

SITE_TARGET = "test"

JSON_REQUEST_TYPES = {
    "name": str,
    "phones": list,
    "emails": list,
    "addresses": list,
    "type": str,
}


def map_policy_type(policy_code):
    normalize_map = policy_map.get(policy_code, "Unknown")
    britecore_map = britecore_policy_type_map.get(SITE_TARGET).get(
        normalize_map, "Unknown"
    )

    return britecore_map


def fix_business(name: str) -> str:
    """
    Fix capitalization for business suffix tokens (LLC, LLP, DBA).

    Args:
        name: Contact name to fix.

    Returns:
        Name with standardized capitalization for business suffixes.
    """
    check_business = re.findall(
        COMPILED_REGEXES.get("reg_business_name"), name)
    if check_business:
        for each_business in check_business:
            name = name.replace(
                each_business,
                f"{each_business.upper().strip().replace(' ', '')}",
            )

    return name


def fix_apostrophe(name: str) -> str:
    """Fixes capitalization on names with apostrophe (Karen'S to Karen's)
    Also adds escape character for SQL insert
    :param name: Name to fix
    :return: Fixed name
    """
    name = re.sub(
        COMPILED_REGEXES["reg_double_apostrophe"], lambda mo: mo.group(
            0).lower(), name
    )
    return name


def fix_suffix(suffix: str) -> str:
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


class BritecoreAddress:
    """Class for contact address"""

    def __init__(self, full_address) -> None:
        global _LOGGER
        _LOGGER = scl.get_parent_logger()
        self.full_address = full_address

    def process_address(self) -> list:
        full_address = self.full_address
        if not full_address:
            raise BritecoreError.InvalidAddress("Missing Address")

        if isinstance(self.full_address, str):
            full_address = literal_eval(str(self.full_address)[1:-2])

        zip_code = full_address.get("address_zip", "").strip()
        address1 = full_address.get("address_line1", "").strip()
        address2 = full_address.get("address_line2", "").strip()
        state = full_address.get("address_state", "").upper()
        county = full_address.get("address_county", "").strip().title()
        city = full_address.get("address_city", "").title().strip()
        property = full_address.get("property", "").title().strip()

        if address1 == "" and address2 != "":
            address1 = address2
            address2 = ""
        elif address1 == "":
            raise BritecoreError.InvalidAddress("Missing Address")

        if zip_code == "":
            try:
                zip_code = ZIP_CODE_DF.loc[
                    (
                        (state == ZIP_CODE_DF["admin code1"])
                        & (city == ZIP_CODE_DF["place name"])
                    )
                ]["postal code"].values[0]
                _LOGGER.info(
                    f"Zip code missing - using {zip_code} for city of {city} "
                    f"and state of {state}"
                )
            except IndexError:
                raise BritecoreError.InvalidAddress("Missing Zip Code")

        zip_code = self.fix_zipcode(zip_code)

        fixed_address = [
            {
                "address_line1": self.fix_address(address1),
                "address_line2": self.fix_address(address2),
                "address_state": self.fix_state(state, zip_code),
                "address_country": "USA",
                "address_zip": zip_code,
                "type": full_address.get("type", DEFAULT_ADDRESS_TYPE),
                "address_county": self.fix_county(county, zip_code[:5]),
                "address_city": self.fix_city(city, zip_code),
                "property": property,
            }
        ]
        _LOGGER.debug(f"Created address {fixed_address}")

        return fixed_address

    @classmethod
    def fix_county(cls, county: str, zipcode: str) -> str:
        tmp_zipcode = zipcode[:5]
        county_lookup = ZIP_CODE_DF
        county_lookup = county_lookup.loc[county_lookup["postal code"]
                                          == tmp_zipcode]

        try:
            county_lookup = county_lookup["admin name2"].values[0]
        except IndexError:
            county_lookup = ""

        county = COMMON_CITY_REPLACEMENT.get(county, county)

        if county == "" and county_lookup != "":
            county = county_lookup

        if county_lookup.lower() != county.lower() and county != "":
            _LOGGER.info(
                f"County '{county}' not found in zip code '{zipcode}' - "
                f"zip code matches '{county_lookup}'"
            )

        return county

    @classmethod
    def fix_city(cls, city: str, zipcode: str) -> str:
        city = re.sub(COMPILED_REGEXES.get("reg_city_state"), "", city)

        tmp_zipcode = zipcode[:5]

        city_lookup = ZIP_CODE_DF
        city_lookup = city_lookup.loc[city_lookup["postal code"]
                                      == tmp_zipcode]
        try:
            city_lookup = city_lookup["place name"].values[0]
        except IndexError:
            city_lookup = ""

        city = COMMON_CITY_REPLACEMENT.get(city, city)

        if city.startswith("St "):
            city = city.replace("St ", "Saint ", 1)

        if city.startswith("Mt "):
            city = city.replace("Mt ", "Mount ", 1)

        if city == "" and city_lookup != "":
            city = city_lookup

        if city_lookup.lower() != city.lower() and city != "":
            _LOGGER.info(
                f"City '{city}' not found in zip code '{zipcode}' - zip code "
                f"matches '{city_lookup}'"
            )

        return city

    @staticmethod
    def fix_zipcode(zipcode: str) -> str:
        zipcode = zipcode.strip().replace("-", "").zfill(5)
        if zipcode == "00000" or len(zipcode) > 10 or not zipcode.isnumeric():
            raise BritecoreError.InvalidAddress(
                f"Invalid Zip Code - {zipcode}")
        zipcode = re.sub(COMPILED_REGEXES.get("reg_zip"), "", zipcode)
        if len(zipcode) > 5:
            zipcode = zipcode[:5] + "-" + zipcode[5:]

        return zipcode

    @classmethod
    def fix_state(cls, state: str, zipcode: str) -> str:
        state = state.strip().upper()
        state = re.sub(COMPILED_REGEXES.get("reg_city_state"), "", state)

        tmp_zipcode = zipcode[:5]

        state_lookup = ZIP_CODE_DF
        state_lookup = state_lookup.loc[state_lookup["postal code"]
                                        == tmp_zipcode]
        try:
            state_lookup = state_lookup["admin code1"].values[0]
        except IndexError:
            state_lookup = ""

        if state == "" and state_lookup != "":
            state = state_lookup

        if state_lookup.lower() != state.lower() and state != "":
            _LOGGER.info(
                f"State '{state}' not found in zip code '{zipcode}' - zip "
                f"code "
                f"matches '{state_lookup}'"
            )
            state = "WI"

        return state

    @staticmethod
    def fix_street(address: str) -> str:
        """
        Fixes number street capitalization (11Th to 11th)
        Also fixes capitalization on roads ending with 2 letters
        (Highway Bb/Cb, Highway BB/CB)
        :param address: Address to fix
        :type address: str
        :return: Fixed address
        :rtype: str
        """
        address = re.sub(r"\s\d..\s*", lambda mo: mo.group(0).lower(), address)
        address = re.sub(
            r"\b(.)\1{1,2}",
            lambda mo: mo.group(0).upper(),
            address,
            0,
            re.IGNORECASE,
        )
        if address[-3:-2].lower() == " ":
            address = address[:-1] + address[-1:].upper()
        return address

    @staticmethod
    def fix_street_name(address: str) -> str | bytes | Literal[""]:
        """
        Normalizes address different abbreviations
        :param address: Address to normalize
        :type address: str
        :return: Fixed address
        :rtype: str
        """

        for k, v in COMPILED_REGEXES.get("street_name_replacement").items():
            address = re.sub(k, v, address)

        if address != "":
            if not address[-1].isalnum():
                address = address[:-1]
        return address

    @staticmethod
    def remove_double_non_letter(address: str) -> str:
        """
        Remove repeated non-alphanumeric characters
        (Name11  Name22, Name11 Name22)
        :param address: Address to fix
        :type address: str
        :return: Fixed address
        :rtype: str
        """
        reg_dbl_non_letter = r"(\W+|\s..)\1"
        if re.search(reg_dbl_non_letter, address):
            replace_char = re.search(reg_dbl_non_letter, address).group(1)[-1]
            address = re.sub(reg_dbl_non_letter, replace_char, address)
        return address

    @classmethod
    def fix_address(cls, address: str | bytes | Literal[""]) -> str:
        """
        Runs all functions to normalize address
        :param address: Address to normalize
        :type address: str
        :return: Normalized address
        :rtype: str
        """

        address = address.strip().title()
        if address == "":
            return ""
        if re.search(r"^T:\d", address):
            return address
        # Remove repeated punctuation and illegal address chars
        address = cls.remove_double_non_letter(address)
        address = re.sub(COMPILED_REGEXES.get("reg_address"), "", address)
        # Normalize street names and directions, then street casing quirks
        address = cls.fix_street_name(address)
        address = cls.fix_street(address)
        # Remove business-related tokens that don't belong in address lines
        address = re.sub(COMPILED_REGEXES.get("reg_address2"), "", address)
        # Collapse multiple spaces and trim
        address = re.sub(r"\s{2,}", " ", address).strip()

        return address


class BritecorePhone:
    """Class for contact phone number"""

    def __init__(self, phone_number: list[Dict[str, str]]) -> None:
        global _LOGGER
        _LOGGER = scl.get_parent_logger()
        self.phone_number = phone_number

    def process_phone(
        self,
    ) -> list:
        phone_number = self.phone_number
        phone_number_list = []
        for each_phone_number in phone_number:
            phone_number = each_phone_number.get("phone", "")
            phone_type = each_phone_number.get("type", "")
            if phone_type == "":
                phone_type = DEFAULT_PHONE_TYPE
            if phone_number == "" or phone_number == "0" or phone_number.strip() == "-":
                break
            fixed_phone_number = {
                "phone": self.fix_phone(phone_number),
                "type": phone_type,
            }
            phone_number_list.append(fixed_phone_number)
        fixed_phone_number = phone_number_list

        return fixed_phone_number

    @staticmethod
    def fix_phone(phone: str) -> str | None:
        """
        Normalize phone number
        :param phone: Phone number
        :type phone: str
        :return: Normalized phone number
        :rtype: str
        """

        phone = re.sub(COMPILED_REGEXES.get("reg_phone"), "", phone)
        if len(phone) != 10 or not phone.isnumeric():
            return None
        phone = "1-" + phone[:3] + "-" + phone[3:6] + "-" + phone[6:]
        return phone


class BritecoreEmail:
    """Class for email addresses"""

    def __init__(self, email: list[Dict[str, str]]) -> None:
        global _LOGGER
        _LOGGER = scl.get_parent_logger()
        self.email = email

    def process_email(self) -> list:
        email = self.email
        email_address_list = []
        for each_email in email:
            email_address = each_email.get("email", "").lower()
            email_type = each_email.get("type", "")
            if email_type == "":
                email_type = DEFAULT_EMAIL_TYPE

            fixed_email = {"email": self.fix_email(
                email_address), "type": email_type}

            email_address_list.append(fixed_email)
        fixed_email = email_address_list

        return fixed_email

    @staticmethod
    def fix_email(email: str) -> str:
        """
        Strips and lowercases email address
        :param email: Email address
        :type email: str
        :return: Normalized email address
        :rtype: str
        """

        email_verify = re.match(COMPILED_REGEXES.get("reg_email"), email)
        if not email_verify:
            if email:
                _LOGGER.info(f"Invalid email address: {email}")
            return ""
        email = email_verify.group(0)
        return email


class BritecoreContact:
    """Class with all attributes for Britecore contact"""

    def __init__(
        self,
        name: str,
        address: Dict[str, str],
        policy_number: Optional[str] = None,
        phone_number: Optional[list[Dict[str, str]]] = None,
        email: Optional[list[Dict[str, str]]] = None,
        contact_id: Optional[str] = None,
        contact_type: str = "individual",
    ):
        global _LOGGER
        _LOGGER = scl.get_parent_logger()

        self.name = name
        self.address = address
        self.policy_number = policy_number
        self.phone_number = phone_number
        self.email = email
        self.contact_id = contact_id
        self.contact_type = contact_type

    def process_contact(self):
        name = self.name
        address = self.address
        policy_number = self.policy_number
        phone_number = self.phone_number
        email = self.email
        contact_id = self.contact_id
        contact_type = self.contact_type

        if not phone_number:
            phone_number = [{}]
        if not email:
            email = [{}]
        final_contact = {
            "name": fix_business(name),
            "contact_id": contact_id,
            "addresses": BritecoreAddress(address).process_address(),
            "phones": BritecorePhone(phone_number).process_phone(),
            "emails": BritecoreEmail(email).process_email(),
            "type": contact_type,
            "policy_number": policy_number,
        }

        _LOGGER.debug(f"Created contact {final_contact}")

        return final_contact


class BritecorePolicy:
    """Policy classes"""

    def __init__(
        self,
        policy_number: str,
        contacts: list[BritecoreContact],
        effective_date: datetime.datetime,
        policy_type_id: str,
        inception_date: Optional[datetime.datetime] = None,
        term_type: str = "1 Year",
        renewal_term_type: str = "1 Year",
        is_renewal: bool = True,
        as_agent: bool = False,
        manual_policy_number: bool = True,
        previous_inspection_date: Optional[datetime.datetime] = None,
        next_inspection_date: Optional[datetime.datetime] = None,
    ):
        self.fixed_policy = {
            "contacts": contacts,
            "policy_number": policy_number,
            "inception_date": inception_date,
            "effective_date": effective_date,
            "term_type": term_type,
            "renewal_term_type": renewal_term_type,
            "is_renewal": is_renewal,
            "as_agent": as_agent,
            "manual_policy_number": manual_policy_number,
            "policy_type_id": policy_type_id,
            "previous_inspection_date": previous_inspection_date,
            "next_inspection_date": next_inspection_date,
        }
