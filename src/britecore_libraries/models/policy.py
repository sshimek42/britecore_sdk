"""BriteCore policy model."""

import datetime
from typing import Optional

from britecore_libraries.models.contact import BritecoreContact


class BritecorePolicy:
    """
    BriteCore policy model.

    Represents an insurance policy with associated contacts and metadata.
    """

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
        """
        Initialize a BriteCore policy.

        Args:
            policy_number: Unique policy identifier
            contacts: List of associated contacts
            effective_date: Policy effective date
            policy_type_id: BriteCore policy type UUID
            inception_date: Policy inception date
            term_type: Policy term type
            renewal_term_type: Renewal term type
            is_renewal: Whether this is a renewal
            as_agent: Whether acting as agent
            manual_policy_number: Whether policy number is manual
            previous_inspection_date: Last inspection date
            next_inspection_date: Next inspection date
        """
        self.policy_number = policy_number
        self.contacts = contacts
        self.effective_date = effective_date
        self.policy_type_id = policy_type_id
        self.inception_date = inception_date
        self.term_type = term_type
        self.renewal_term_type = renewal_term_type
        self.is_renewal = is_renewal
        self.as_agent = as_agent
        self.manual_policy_number = manual_policy_number
        self.previous_inspection_date = previous_inspection_date
        self.next_inspection_date = next_inspection_date

    def to_dict(self) -> dict:
        """
        Convert policy to dictionary format for API submission.

        Returns:
            Dictionary representation of policy
        """
        return {
            "contacts": self.contacts,
            "policy_number": self.policy_number,
            "inception_date": self.inception_date,
            "effective_date": self.effective_date,
            "term_type": self.term_type,
            "renewal_term_type": self.renewal_term_type,
            "is_renewal": self.is_renewal,
            "as_agent": self.as_agent,
            "manual_policy_number": self.manual_policy_number,
            "policy_type_id": self.policy_type_id,
            "previous_inspection_date": self.previous_inspection_date,
            "next_inspection_date": self.next_inspection_date,
        }

    # For backward compatibility
    @property
    def fixed_policy(self) -> dict:
        """Backward compatibility property."""
        return self.to_dict()
