"""Class definition and methods for BriteCore contacts"""

import datetime
import re


class Bccontact(dict):
    """Class with all attributes for BriteCore contact"""

    def __new__(cls, policy, name, contact_id, address, phone, email):
        return dict(
            cls.fixed_contact(policy, name, contact_id, address, phone, email))

    def __init__(self, policy, name, contact_id, address, phone, email):
        super().__init__()
        self.policy = policy
        self.name = name
        self.contact_id = contact_id
        self.address = address
        self.phone = phone
        self.email = email

    @classmethod
    def fix_business(cls, name):
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

    @classmethod
    def fixed_contact(cls, policy, name, contact_id, address, phone, email):
        """
        Finalized contact for policy
        :param policy: Policy number
        :type policy: str
        :param name: Contact name
        :type name: str
        :param contact_id: BriteCore contact ID
        :type contact_id: str
        :param address: Contact address
        :type address: [str, list]
        :param phone: Contact phone
        :type phone: [str, list]
        :param email: Contact email
        :type email: [str, list]
        :return: Contact
        :rtype: dict
        """
        final_contact = {
            "policy": policy,
            "name": cls.fix_business(name),
            "contact_id": contact_id,
            "address": address,
            "phone": phone,
            "email": email,
        }
        return final_contact


class Bcaddress:
    """Class for contact address"""

    def __init__(self):
        self.address1 = ""
        self.address2 = ""
        self.city = ""
        self.county = ""
        self.state = ""
        self.zip = ""
        self.address = ""

        self.address_list = []

    def add(
        self,
        address1,
        address2,
        city,
        county,
        state,
        zipcode,
        address_type,
        fix=False,
        address_id="",
    ):
        """
        Adds address to list
        :param address1: Contact address
        :type address1: str
        :param address2: Contact address
        :type address2: str
        :param city: Contact address
        :type city: str
        :param county: Contact address
        :type county: str
        :param state: Contact address
        :type state: str
        :param zipcode: Contact address
        :type zipcode: str
        :param address_type: Contact address
        :type address_type: str
        :param fix: Contact address
        :type fix: bool
        :param address_id: Contact address
        :type address_id: str
        """
        reg_city_state = r"[^0-9a-zA-Z\s]+"
        reg_zip_phone = r"[^0-9a-zA-Z]+"
        if fix:
            address1 = self.fix_address(address1)
            address2 = self.fix_address(address2)
            city = city.strip().title()
            city = re.sub(reg_city_state, "", city)
            city = city.replace(" Du ", " du ")
            city = city.replace(" Des ", " des ")
            state = state.strip().upper()
            state = re.sub(reg_city_state, "", state)
            county = county.strip().title()
            county = county.replace(" Du ", " du ")
            zipcode = re.sub(reg_zip_phone, "", zipcode)
            if len(zipcode) > 5:
                zipcode = zipcode[:5] + "-" + zipcode[5:]

        address = {
            "address1": address1,
            "address2": address2,
            "city": city,
            "state": state,
            "county": county,
            "zip": zipcode,
            "type": address_type,
            "id": address_id,
        }

        self.address_list.append(address)

    def addresses(self, clear=False):
        """
        Returns address list
        :param clear: Clear list after retrieve
        :type clear: bool
        :return: Address list
        :rtype: list
        """
        if clear:
            tmp_list = list(self.address_list)
            self.address_list.clear()
        else:
            tmp_list = list(self.address_list)

        return tmp_list

    def clear(self):
        """Clear list"""
        self.address_list.clear()

    @classmethod
    def fix_street(cls, address):
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

    @classmethod
    def fix_street_name(cls, address):
        """
        Normalizes address different abbreviations
        :param address: Address to normalize
        :type address: str
        :return: Fixed address
        :rtype: str
        """
        address = re.sub(r"Hwy\b", "Highway", address)
        address = re.sub(r"Cty\b", "County", address)
        address = re.sub(r"\DRd\b", " Road", address)
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
        address = re.sub(r"Tr\b", "Terrance", address)
        address = re.sub(r"\sN\s", " North ", address)
        address = re.sub(r"\sS\s", " South ", address)
        address = re.sub(r"\sE\s", " East ", address)
        address = re.sub(r"\sW\s", " West ", address)
        address = re.sub(r"Us\b", "US", address)
        # skipcq: PTC-W0048
        if address != "":
            if not address[-1].isalnum():
                address = address[:-1]
        return address

    @classmethod
    def remove_double_non_letter(cls, address):
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
        address = cls.fix_street_name(address)
        address = cls.fix_street(address)
        address = cls.remove_double_non_letter(address)
        return address


class Bcphone:
    """Class for contact phone number"""

    def __init__(self):
        self.phone = ""
        self.phone_list = []

    def add(self, phone, phone_type="Home", fix=False, phone_id=""):
        """
        Phone number to add to list
        :param phone: Phone number
        :type phone: str
        :param phone_type: Contact phone type
        :type phone_type: str
        :param fix: Normalize phone number
        :type fix: bool
        :param phone_id: BriteCore phone ID
        :type phone_id: str
        """
        if fix:
            phone = self.fixed_phone(phone)

        self.phone_list.append({phone_type: phone, "id": phone_id})
        # return phone

    def fix(self, phone):
        """
        Return fixed number, don't add to list
        :param phone: Phone number
        :type phone: str
        :return: Phone number
        :rtype: str
        """
        phone = self.fixed_phone(phone)
        return phone

    def phones(self, clear=False):
        """
        Returns and optionally clears phone list
        :param clear: Clear list
        :type clear: bool
        :return: Phone list
        :rtype: list
        """
        if clear:
            tmp_phone = list(self.phone_list)
            self.phone_list.clear()
        else:
            tmp_phone = list(self.phone_list)

        return tmp_phone

    def clear(self):
        """Clear phone list"""
        self.phone_list.clear()

    @classmethod
    def fixed_phone(cls, phone):
        """
        Normalize phone number
        :param phone: Phone number
        :type phone: str
        :return: Normalized phone number
        :rtype: str
        """
        reg_zip_phone = r"[^0-9a-zA-Z]+"

        phone = re.sub(reg_zip_phone, "", phone)
        if phone:
            phone = phone[:3] + "-" + phone[3:6] + "-" + phone[6:]
        return phone


class Bcemail:
    """Class for email addresses"""

    def __init__(self):
        self.email = ""
        self.email_list = []

    def add(self, email, email_type="Home", fix=False, email_id="") -> None:
        """
        Add email to list
        :param email: Email to add
        :type email: str
        :param email_type: Type of email e.g. Home, Business, etc.
        :type email_type: str
        :param fix: Option to normalize email address
        :type fix:
        :param email_id: Existing BriteCore email ID
        :type email_id: str
        :return:
        :rtype: None
        """
        if fix:
            email = self.fixed_email(email)

        self.email_list.append({email_type: email, "id": email_id})

    def emails(self, clear=False) -> list:
        """
        Returns email address list and optionally clears list
        :param clear: Option to clear list
        :type clear: bool
        :return: List of emails addresses
        :rtype: list
        """
        if clear:
            tmp_email = list(self.email_list)
            self.email_list.clear()
        else:
            tmp_email = list(self.email_list)

        return tmp_email

    def fix(self, email: str) -> str:
        """
        Normalize email address
        :param email: Email address to normalize
        :type email: str
        :return: Normalized email address
        :rtype: str
        """
        email = self.fixed_email(email)
        return email

    def clear(self) -> None:
        """
        Clears email list
        :return:
        :rtype: None
        """
        self.email_list.clear()

    @classmethod
    def fixed_email(cls, email: str) -> str:
        """
        Strips and lowercases email address
        :param email: Email address
        :type email: str
        :return: Normalized email address
        :rtype: str
        """
        return email.strip().lower()


class Policy:
    """Policy class"""

    def __init__(self, policy_num, policy_opt, contacts):
        self.policy_num = policy_num
        self.policy_opt = policy_opt
        self.contacts = contacts

    def get(self) -> dict:
        """
        Returns policy info
        :return: Policy info
        :rtype: dict
        """
        policy_dict = {
            "policy_number":
            self.policy_num,
            "inception_date":
            self.policy_opt.get(
                "inception_date",
                datetime.datetime.now().strftime("%m"
                                                 "/%d/%Y"),
            ),
            "term_type":
            self.policy_opt.get("term", "1 year"),
            "renewal_term_type":
            self.policy_opt.get("renewal_term", "1 year"),
            "as_agent":
            False,
            "manual_policy_number":
            True,
            "policy_type_id":
            self.policy_opt.get("policy_type_id"),
            "underwriting_questions":
            self.policy_opt.get("underwriting_questions"),
            "underwriting_options":
            self.policy_opt.get("underwriting_options"),
            "policy_contacts":
            self.contacts,
        }

        return policy_dict
