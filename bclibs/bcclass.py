"""Class definition and methods for BriteCore contacts"""
from pathlib import Path

import bcexceptions
import re
import logging
from typing import Dict,Pattern

from sclogging import sclogging_main as scl

import pandas as pd

_LOGGER: logging.Logger = scl.get_parent_logger()

FIELD_MAP_TO_BRITECORE = {
    "MIPS"    : {
        "policy_list"  : {
            "NAME"          : "name",
            "ADDR 1"        : "address_line1",
            "ADDR 2"        : "address_line2",
            "CITY"          : "address_city",
            "ST"            : "address_state",
            "ZIP"           : "address_zip",
            "PHONE 1"       : "phone_number_h",
            "PHONE 2"       : "phone_number_m",
            "E-MAIL ADDR"   : "email",
            "POLICY #"      : "policy_number",
            "address_fields": ["ADDR 1", "ADDR 2", "CITY", "ST", "ZIP",
                               "PHONE 1", "PHONE 2", "E-MAIL ADDR", "POLICY #"]
            },
        "location_list": {
            "Policy Number" : "policy_number",
            "Legal Address" :
                "address_line1",
            "Legal City"    : "address_city",
            "Legal State"   : "address_state",
            "Legal Zip"     : "address_zip",
            "County"        : "address_county",
            "address_fields": ["Legal Address", "Legal City", "Legal State",
                               "Legal Zip",
                               "Policy Number", "County"]
            }
        },
    "Spectrum": {
        "policy_list"  : {
            "Named Insured" : "name",
            "Address Line 1": "address_line1",
            "Address Line 2": "address_line2",
            "City"          : "address_city",
            "State"         : "address_state",
            "Postal Code"   : "address_zip",
            "Home Phone"    : "phone_number_h",
            "Mobile Phone"  : "phone_number_m",
            "Email Address" : "email",
            "Policy #"      : "policy_number",
            "address_fields": ["Address Line 1", "Address Line 2", "City",
                               "State",
                               "Postal Code", "Home Phone", "Mobile Phone",
                               "Email "
                               "Address", "Policy #"]
            },
        "location_list": {
            "Policy #"        : "policy_number",
            "Physical Address": "address_line1",
            "City"            : "address_city",
            "State"           : "address_state",
            "Zip"             : "address_zip",
            "address_fields"  : ["Physical Address", "City", "State",
                                 "Zip", "Policy #"]
            }
        }
    }

FIELD_MAP_TO_NAMED_INSURED = {
    "MIPS"    : {v: k for k,
    v in FIELD_MAP_TO_BRITECORE[
                     "MIPS"]["policy_list"].items() if k != "address_fields"},
    "Spectrum": {v: k for k, v in FIELD_MAP_TO_BRITECORE[
        "Spectrum"]["policy_list"].items() if k != "address_fields"}
    }

FIELD_MAP_TO_RISK_LOCATION = {
    "MIPS"    : {v: k for k,
    v in FIELD_MAP_TO_BRITECORE[
                     "MIPS"]["location_list"].items() if
                 k != "address_fields"},
    "Spectrum": {v: k for k, v in FIELD_MAP_TO_BRITECORE[
        "Spectrum"]["location_list"].items() if k != "address_fields"}
    }

DEFAULT_ADDRESS_TYPE = "Mailing/Billing"
DEFAULT_PHONE_TYPE = "Home"
DEFAULT_EMAIL_TYPE = "Home"

COMMON_CITY_REPLACEMENT: Dict[str, str] = {
    "Depere": "De Pere"
    }

COMPILED_REGEXES: Dict[str, Pattern[str]] = {

    "search_name_mult"     : re.compile(
        r"^(\w*\W\w?\W|\w*\W)(\w*)\s?(\w*)?\s(&)\s(\w*\W\w?\W|\w*)\W?(\w*)?("
        r"\W\w*)?"
        ),
    "search_name_single"   : re.compile(
        r"^(\w*\W\w|\w*\W*)(\W\w*|\W\w*\W)("
        r"\W\w.*|\b)"
        ),
    "search_email"         : re.compile(
        r"[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{"
        r"2,64}"
        ),
    "reg_name_c"           : re.compile(r"[^0-9a-zA-Z\s#+&',/-]+"),
    "reg_and_or"           : re.compile(
        r"\W(&/or|and/or|and|or)\W", re.IGNORECASE
        ),
    "reg_address"          : re.compile(r"[^0-9a-zA-Z\s#,/-]+"),
    "reg_address2"         : re.compile(
        r"c/o|dba|inc|att|co\W|trust", re.IGNORECASE
        ),
    "reg_city_state"       : re.compile(r"[^0-9a-zA-Z\s]+"),
    "reg_zip"              : re.compile(r"[^0-9a-zA-Z]+"),
    "reg_phone"            : re.compile(r"-|\(|\)|\s"),
    "reg_email"            : re.compile(
        r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7})\b"
        ),
    "reg_name"             : re.compile(r"[^0-9a-zA-Z\s#+&'/-]+"),
    "reg_small_name"       : re.compile(r"\s(Du|Des)\s"),
    "reg_business_name"    : re.compile(
        r"\s(llc|llp|dba|inc)(?:\s|$)", re.IGNORECASE
        ),
    "reg_double_apostrophe": re.compile(r"'\w"),
    }

ZIP_CODE_DF =  pd.read_csv(
    f"{Path(__file__).absolute().parent}/zip_codes.csv", dtype=str
    )


def fix_business(name: str) -> str:
    """
    Fix capitalization for business suffix tokens (LLC, LLP, DBA).

    Args:
        name: Contact name to fix.

    Returns:
        Name with standardized capitalization for business suffixes.
    """
    check_business = re.findall(
        COMPILED_REGEXES.get("reg_business_name"), name
        )
    if check_business:
        for each_business in check_business:
            name = name.replace(
                each_business, f"{each_business.upper().strip()}"
                ).replace("  ", " ")

    return name


def fix_apostrophe(name: str) -> str:
    """Fixes capitalization on names with apostrophe (Karen'S to Karen's)
    Also adds escape character for SQL insert
    :param name: Name to fix
    :return: Fixed name
    """
    name = re.sub(
        COMPILED_REGEXES["reg_double_apostrophe"],
        lambda mo: mo.group(0).lower(), name
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


class BCAddress:
    """Class for contact address"""

    def __init__(self, full_address: dict):
        global _LOGGER
        _LOGGER = scl.get_parent_logger()
        if not full_address:
            raise bcexceptions.InvalidAddress("Missing Address")

        self.full_address = full_address
        zip_code = full_address.get("address_zip", "").strip()
        address1 = full_address.get("address_line1", "").strip()
        address2 = full_address.get("address_line2", "").strip()
        state = full_address.get(
            "address_state",
            ""
            ).upper()
        county = full_address.get("address_county", "").strip().title()
        city = full_address.get("address_city", "").title().strip()

        if address1 == "" and address2 != "":
            address1 = address2
            address2 = ""
        elif address1 == "":
            raise bcexceptions.InvalidAddress("Missing Address")

        if zip_code == "":
            try:
                zip_code = ZIP_CODE_DF.loc[((state == ZIP_CODE_DF["admin code1"]) & (
                                                        city ==
                                                        ZIP_CODE_DF[
                                                            "place name"]))][
                    "postal code"].values[0]
                _LOGGER.warning(f"Zip code missing - using {zip_code} for city of {city} and state of {state}")
            except IndexError:
                raise bcexceptions.InvalidAddress(
                    "Missing Zip Code"
                    )

        self.zip_code = self.fix_zipcode(zip_code)


        self.fixed_address = [{
            "address_line1"  : self.fix_address(address1),
            "address_line2"  : self.fix_address(address2),
            "address_state"  : self.fix_state(
                state
                , self.zip_code
                ),
            "address_country": "USA",
            "address_zip"    : self.zip_code,
            "type"           : full_address.get(
                "type", DEFAULT_ADDRESS_TYPE
                ),
            "address_county" : self.fix_county(
                county
                , self.zip_code[:5]
                ),
            "address_city"   : self.fix_city(
                city, self.zip_code
                )
            }]
        _LOGGER.debug(f"Created address {self.fixed_address}")

    @classmethod
    def fix_county(cls, county, zipcode):

        tmp_zipcode = zipcode[:5]
        county_lookup = ZIP_CODE_DF
        county_lookup = county_lookup.loc[
            county_lookup["postal code"] == tmp_zipcode]

        try:
            county_lookup = county_lookup["admin name2"].values[0]
        except IndexError:
            county_lookup = ""

        county = COMMON_CITY_REPLACEMENT.get(county, county)

        if county == "" and county_lookup != "":
            county = county_lookup

        if county_lookup.lower() != county.lower() and county != "":
            _LOGGER.warning(
                f"County '{county}' not found in zip code '{zipcode}' - "
                f"zip code matches '{county_lookup}'"
                )

        return county

    @classmethod
    def fix_city(cls, city, zipcode):

        city = re.sub(COMPILED_REGEXES.get("reg_city_state"), "", city)

        tmp_zipcode = zipcode[:5]

        city_lookup = ZIP_CODE_DF
        city_lookup = city_lookup.loc[
            city_lookup["postal code"] == tmp_zipcode]
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
            _LOGGER.warning(
                f"City '{city}' not found in zip code '{zipcode}' - zip code "
                f"matches '{city_lookup}'"
                )

        return city

    @staticmethod
    def fix_zipcode(zipcode):

        zipcode = zipcode.strip().replace("-", "").zfill(5)
        if zipcode == "00000" or len(
                zipcode
                ) > 10 or not zipcode.isnumeric():
            raise bcexceptions.InvalidAddress(f"Invalid Zip Code - {zipcode}")
        zipcode = re.sub(COMPILED_REGEXES.get("reg_zip"), "", zipcode)
        if len(zipcode) > 5:
            zipcode = zipcode[:5] + "-" + zipcode[5:]

        return zipcode

    @classmethod
    def fix_state(cls, state, zipcode):
        state = state.strip().upper()
        state = re.sub(COMPILED_REGEXES.get("reg_city_state"), "", state)

        tmp_zipcode = zipcode[:5]

        state_lookup = ZIP_CODE_DF
        state_lookup = state_lookup.loc[
            state_lookup["postal code"] == tmp_zipcode]
        try:
            state_lookup = state_lookup["admin code1"].values[0]
        except IndexError:
            state_lookup = ""

        if state == "" and state_lookup != "":
            state = state_lookup

        if state_lookup.lower() != state.lower() and state != "":
            _LOGGER.warning(
                f"State '{state}' not found in zip code '{zipcode}' - zip "
                f"code "
                f"matches '{state_lookup}'"
                )
            state = "WI"

        return state

    @staticmethod
    def fix_street(address):
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
    def fix_street_name(address):
        """
        Normalizes address different abbreviations
        :param address: Address to normalize
        :type address: str
        :return: Fixed address
        :rtype: str
        """
        address = re.sub(r"Hwy\b", "Highway", address)
        address = re.sub(r"Cty\b", "County", address)
        address = re.sub(r"Rd\b", " Road", address)
        address = re.sub(r"Ave\b", "Avenue", address)
        address = re.sub(r"St\b", "Street", address)
        address = re.sub(r"Ln\b", "Lane", address)
        address = re.sub(r"Ct\b", "Court", address)
        address = re.sub(r"Dr\b", "Drive", address)
        address = re.sub(r"Po\b", "PO", address)
        address = re.sub(r"P\sO\b", "PO", address)
        address = re.sub(r"Cir\b", "Circle", address)
        address = re.sub(r"Pt\b", "Point", address)
        address = re.sub(r"Tk\b", "Trunk", address)
        address = re.sub(r"Tr\b", "Trail", address)
        address = re.sub(r"Trl\b", "Trail", address)
        address = re.sub(r"Ter\b", "Terrace", address)
        address = re.sub(r"\sN\s", " North ", address)
        address = re.sub(r"\sS\s", " South ", address)
        address = re.sub(r"\sE\s", " East ", address)
        address = re.sub(r"\sW\s", " West ", address)
        address = re.sub(r"Us\b", "US", address)

        if address != "":
            if not address[-1].isalnum():
                address = address[:-1]
        return address

    @staticmethod
    def remove_double_non_letter(address):
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
    def fix_address(cls, address):
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


class BCPhone:
    """Class for contact phone number"""

    def __init__(self, phone_number):
        phone_number_list = []
        for each_phone_number in phone_number:
            phone_number = each_phone_number.get("phone", "")
            phone_type = each_phone_number.get("type", "")
            if phone_type == "":
                phone_type = DEFAULT_PHONE_TYPE
            if (phone_number == "" or phone_number == "0" or
                    phone_number.strip() == "-"):
                self.fixed_phone_number = []
                break
            fixed_phone_number = {
                "phone": self.fix_phone(
                    phone_number
                    ),
                "type" : phone_type
                }
            phone_number_list.append(fixed_phone_number)
        self.fixed_phone_number = phone_number_list

    @staticmethod
    def fix_phone(phone):
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


class BCEmail:
    """Class for email addresses"""

    def __init__(self, email):
        email_address_list = []
        for each_email in email:
            email_address = each_email.get("email", "").lower()
            email_type = each_email.get("type", "")
            if email_type == "":
                email_type = DEFAULT_EMAIL_TYPE

            fixed_email = {
                "email": self.fix_email(email_address),
                "type" : email_type
                }

            email_address_list.append(fixed_email)
        self.fixed_email = email_address_list

    @staticmethod
    def fix_email(email: str):
        """
        Strips and lowercases email address
        :param email: Email address
        :type email: str
        :return: Normalized email address
        :rtype: str
        """

        email_verify = re.match(
            COMPILED_REGEXES.get("reg_email"),
            email
            )
        if not email_verify:
            if email:
                _LOGGER.warning(f"Invalid email address: {email}")
            return ""
        email = email_verify.group(0)
        return email


class BCContact:
    """Class with all attributes for BriteCore contact"""

    def __init__(
        self, name, address, effective_date, policy_type_id,
        policy_number=None,
        phone_number=None, email=None,
        contact_id=None, inception_date=None,term_type="1 Year",
        renewal_term_type="1 Year",is_renewal=True,as_agent=False,
        manual_policy_number=True
        ):
        if not phone_number:
            phone_number = [{}]
        if not email:
            email = [{}]
        if not contact_id and policy_number:
            contact_id = policy_number
        self.final_contact = {
            "name"      : fix_business(name),
            "contact_id": contact_id,
            "addresses" : BCAddress(address).fixed_address,
            "phones"    : BCPhone(phone_number).fixed_phone_number,
            "emails"    : BCEmail(email).fixed_email,
            "policy_number": policy_number,
            "type"      : "individual",
            "inception_date": inception_date,
            "effective_date": effective_date,
            "term_type" : term_type,
            "renewal_term_type": renewal_term_type,
            "is_renewal": is_renewal,
            "as_agent": as_agent,
            "manual_policy_number": manual_policy_number,
            "policy_type_id": policy_type_id
            }

        _LOGGER.debug(f"Created contact {self.final_contact}")


class BCPolicy:
    """Policy class"""

    def __init__(self, policy_num: str, contacts: BCContact, policy_opt=None):
        self.fixed_policy = {
            "Policy Number" : policy_num,
            "Policy Options":
                policy_opt,
            "Contacts"      : contacts.final_contact
            }
