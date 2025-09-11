"""Class definition and methods for BriteCore contacts"""

import bcexceptions
import re

from sclogging import sclogging_main as scl

from wisconsin_zip_lookup import counties, cities

import replacementdict as rd

SEARCH_NAME_MULT = re.compile(
    r"^((\w*)\W*(\w*))\s(&)\s(\w*\W\w|\w*\W*)(\W\w*|\W\w*\W)(\W\w.*|\b)"
    )
SEARCH_NAME_SINGLE = re.compile(r"^(\w*\W\w|\w*\W*)(\W\w*|\W\w*\W)(\W\w.*|\b)")
SEARCH_EMAIL = re.compile(r"[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,64}")

# RegEx expressions to help remove punctuation from strings
REG_NAME_C = re.compile(r"[^0-9a-zA-Z\s#+&',/-]+")
# REG_AND_OR = re.compile(r"And\b|/Or|Or\b")
REG_ADDRESS = re.compile(r"[^0-9a-zA-Z\s#,/-]+")
REG_ADDRESS2 = re.compile(r"c/o|dba|inc|att|co\W|trust", re.IGNORECASE)
REG_CITY_STATE = re.compile(r"[^0-9a-zA-Z\s]+")
REG_ZIP = re.compile(r"[^0-9a-zA-Z]+")
REG_PHONE = re.compile(r"-|\(|\)|\s")
REG_EMAIL = re.compile(
    r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7})\b"
    )

DEFAULT_ADDRESS_TYPE = "Home"

_LOGGER = scl.get_parent_logger()

class BCAddress:
    """Class for contact address"""

    # logger = get_logger()

    def __init__(self, full_address: dict):
        global _LOGGER
        _LOGGER = scl.get_parent_logger()
        if not full_address:
            raise bcexceptions.InvalidAddress("Missing Address")
        # global _LOGGER

        self.full_address = full_address
        self.zip_code = self.fix_zipcode(full_address.get("zip", ""))
        _address = full_address.get("address1", "")
        if _address == "":
            raise bcexceptions.InvalidAddress("Missing Address")
        self.fixed_address = {
            "address_1"   : self.fix_address(full_address.get("address1", "")),
            "address_2"   : self.fix_address(full_address.get("address2", "")),
            "state"       : self.fix_state(full_address.get("state", "")),
            "country"     : "USA",
            "zip_code"    : self.zip_code,
            "address_type": full_address.get(
                "address_type", DEFAULT_ADDRESS_TYPE
                ),
            "county"      : self.fix_county(
                full_address.get("county", ""), self.zip_code[:5]),
            "city"        : self.fix_city(
                full_address.get("city", ""), self.zip_code[:5])
            }

    @classmethod
    def fix_county(cls, county, zipcode):
        county = county.strip().title()

        for key in rd.replacementcounty.keys():
            county = county.replace(key, rd.replacementcounty[key])

        county_lookup = counties.get(zipcode, "")

        if county == "" and county_lookup != "":
            county = county_lookup

        # if county_lookup != "":
        #     county = county_lookup

        if county_lookup != county and county != "":
            _LOGGER.warning(
                f"County '{county}' not found in zip code '{zipcode}' - "
                f"zip code matches '{county_lookup}'"
                )

        return county

    @classmethod
    def fix_city(cls, city, zipcode):
        city = city.strip().title()

        city = re.sub(REG_CITY_STATE, "", city)
        for key in rd.replacementcity.keys():
            city = city.replace(key, rd.replacementcity[key])

        city_lookup = cities.get(zipcode, "")

        # if city_lookup != "":
        #     city = city_lookup
        if city == "" and city_lookup != "":
            city = city_lookup

        if city_lookup != city and city != "":
            _LOGGER.warning(
                f"City '{city}' not found in zip code '{zipcode}' - zip code "
                f"matches '{city_lookup}'"
                )

        return city

    @staticmethod
    def fix_zipcode(zipcode):
        zipcode = zipcode.strip().replace("-", "")
        if zipcode == "" or len(zipcode) < 5 or len(
                zipcode
                ) > 10 or not zipcode.isnumeric():
            raise bcexceptions.InvalidAddress(f"Invalid Zip Code - {zipcode}")
        zipcode = re.sub(REG_ZIP, "", zipcode)
        if len(zipcode) > 5:
            zipcode = zipcode[:5] + "-" + zipcode[5:]

        return zipcode

    @staticmethod
    def fix_state(state):
        state = state.strip().upper()
        state = re.sub(REG_CITY_STATE, "", state)

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
        # Remove repeated punctuation and illegal address chars
        address = cls.remove_double_non_letter(address)
        address = re.sub(REG_ADDRESS, "", address)
        # Normalize street names and directions, then street casing quirks
        address = cls.fix_street_name(address)
        address = cls.fix_street(address)
        # Remove business-related tokens that don't belong in address lines
        address = re.sub(REG_ADDRESS2, "", address)
        # Collapse multiple spaces and trim
        address = re.sub(r"\s{2,}", " ", address).strip()

        return address



class BCPhone:
    """Class for contact phone number"""

    def __init__(self, phone_number):
        self.fixed_phone_number = {
            "phone_number": self.fix_phone(
                phone_number.get("phone_number", "")
                ),
            "phone_type"  : phone_number.get(
                "phone_type", DEFAULT_ADDRESS_TYPE
                )
            }

    @staticmethod
    def fix_phone(phone):
        """
        Normalize phone number
        :param phone: Phone number
        :type phone: str
        :return: Normalized phone number
        :rtype: str
        """
        # reg_zip_phone = r"[^0-9a-zA-Z]+"

        phone = re.sub(REG_PHONE, "", phone)
        if len(phone) != 10 or not phone.isnumeric():
            raise bcexceptions.InvalidPhoneNumber(phone)
        phone = phone[:3] + "-" + phone[3:6] + "-" + phone[6:]
        return phone


class BCEmail:
    """Class for email addresses"""

    def __init__(self, email):
        self.fixed_email = {
            "e_mail_address": self.fix_email(email.get("email_address", "")),
            "e_mail_type"   : email.get("email_type", DEFAULT_ADDRESS_TYPE)
            }

    @staticmethod
    def fix_email(email: str) -> str:
        """
        Strips and lowercases email address
        :param email: Email address
        :type email: str
        :return: Normalized email address
        :rtype: str
        """

        if not email:
            return ""

        email_verify = re.match(REG_EMAIL, email.strip().lower())
        if not email_verify:
            raise bcexceptions.InvalidEmailAddress(email)

        email = email_verify.group(0)
        return email


class BCContact:
    """Class with all attributes for BriteCore contact"""

    # def __new__( policy, name,  address: Bcaddress, phone, email: Bcemail,
    #             contact_id=None):
    # return dict(fixed_contact(policy, name, contact_id, address,
    # phone, email))

    def __init__(
        self, name, address, phone_number, email=None, contact_id=None
        ):
        # super().__init__()
        self.final_contact = {
            "name"      : self.fix_business(name),
            "contact_id": contact_id,
            "address"   : BCAddress(address).fixed_address,
            "phone"     : BCPhone(phone_number).fixed_phone_number,
            "email"     : BCEmail(email).fixed_email,
            }


        _LOGGER.debug(f"Created contact {self.final_contact}")

    @staticmethod
    def fix_business(name):
        """
        Fixes capitalization for LLC, LLP, and DBA
        :param name: Contact name to fix
        :type name: str
        :return: Fixed name
        :rtype: str
        """
        name = name.replace(" LLc", ", LLC")
        name = name.replace(" LLp", ", LLP")
        name = name.replace("Dba", "DBA")
        name = name.replace(" Inc", " Inc.")
        name = name.replace(" Llc", ", LLC")
        name = name.replace(" Llp", ", LLP")
        return name


class BCPolicy:
    """Policy class"""

    def __init__(self, policy_num: str, contacts: BCContact, policy_opt=None):
        self.fixed_policy = {
            "Policy Number" : policy_num,
            "Policy Options":
                policy_opt,
            "Contacts"      : contacts.final_contact
            }

