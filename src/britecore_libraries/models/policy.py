"""BriteCore policy model."""

import datetime
from dataclasses import dataclass
from typing import Optional

from britecore_libraries.models.contact import BritecoreContact

@dataclass()
class BritecorePolicy:
    """
    BriteCore policy model.

    Represents an insurance policy with associated contacts and metadata.
    """
    policy_number: str
    contacts: list[BritecoreContact]
    effective_date: datetime.datetime
    policy_type_id: str
    inception_date: Optional[datetime.datetime] = None
    term_type: str = "1 Year"
    renewal_term_type: str = "1 Year"
    is_renewal: bool = True
    as_agent: bool = False
    manual_policy_number: bool = True
    previous_inspection_date: Optional[datetime.datetime] = None
    next_inspection_date: Optional[datetime.datetime] = None

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
