"""BriteCore policy model."""

import datetime
from dataclasses import dataclass
from typing import Any

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
    inception_date: datetime.datetime | None = None
    term_type: str = "1 Year"
    renewal_term_type: str = "1 Year"
    is_renewal: bool = True
    as_agent: bool = False
    manual_policy_number: bool = True
    previous_inspection_date: datetime.datetime | None = None
    next_inspection_date: datetime.datetime | None = None

    def to_dict(self) -> dict[Any, Any]:
        """
        Convert policy to dictionary format for API submission.

        Returns:
            Dictionary representation of policy
        """
        return self.__dict__
