"""BriteCore contact model."""

from typing import Literal

from britecore_libraries import logger
from britecore_libraries.validators.address_validator import AddressValidator
from britecore_libraries.validators.email_validator import EmailValidator
from britecore_libraries.validators.name_validator import NameValidator
from britecore_libraries.validators.phone_validator import PhoneValidator

LOGGER = logger

ROLETYPES = Literal[
    "Additional Insured",
    "Additional Interest",
    "Administrator",
    "Agent",
    "Attorney",
    "Board Member",
    "Claim Administrator",
    "Claimant",
    "Claims Adjuster",
    "Claims Supervisor",
    "Contractor",
    "Driver",
    "Employee",
    "External Claims Adjuster",
    "In Care Of",
    "Inspector",
    "Loss Payee",
    "Medical Provider",
    "Named Insured",
    "Public Claims Adjuster",
    "Surplus Lines Producer",
    "Underwriter",
    "Unlisted Payor",
    "Vendor",
]


class BritecoreContact:
    """
    BriteCore contact with validation and processing.

    Represents a contact entity (individual or organization) with associated
    address, phone, and email information.
    """

    def __init__(
        self,
        name: str,
        address: dict[str, str],
        policy_number: str | None = None,
        phone_number: list[dict[str, str]] | None = None,
        email: list[dict[str, str]] | None = None,
        contact_id: str | None = None,
        contact_type: Literal["individual", "organization"] | None = "individual",
    ):
        """
        Initialize a BriteCore contact.

        Args:
            name: Contact name
            address: Address dictionary
            policy_number: Associated policy number
            phone_number: List of phone number dictionaries
            email: List of email dictionaries
            contact_id: Unique contact identifier
            contact_type: Type of contact (individual or organization)
        """
        self.name = name
        self.address = address
        self.policy_number = policy_number
        self.phone_number = phone_number or []
        self.email = email or []
        self.contact_id = contact_id
        self.contact_type = contact_type

    def process_contact(self) -> dict:
        """
        Process and validate contact data.

        Returns:
            Dictionary with processed contact information ready for BriteCore API
        """
        # Default empty lists if None
        phone_number = self.phone_number if self.phone_number else [{}]
        email = self.email if self.email else [{}]

        final_contact = {
            "name": NameValidator.normalize_business_name(self.name),
            "contact_id": self.contact_id,
            "addresses": AddressValidator(self.address).process(),
            "phones": PhoneValidator(phone_number).process(),
            "emails": EmailValidator(email).process(),
            "type": self.contact_type,
            "policy_number": self.policy_number,
        }

        LOGGER.debug(f"Created contact {final_contact}")

        return final_contact
