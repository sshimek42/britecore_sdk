"""BriteCore policy model."""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

LOGGER = logging.getLogger("britecore_libraries")


@dataclass
class BritecoreQuote:
    """BriteCore quote model."""

    number: str
    policy_type_id: str
    agency_id: str
    named_insureds: list[str]
    risks: list[str]
    underwriting_questions: list = field(default_factory=list)
    description: str | None = ""
    number_origin: str = "manual"
    transaction_type: str = "renewal"
    term_type: str = "1 Year"
    inception_date: str = datetime.today().strftime("%Y-%m-%d")
    effective_date: str = datetime.today().strftime("%Y-%m-%d")

    next_inspection_date: str | None = None
    previous_inspection_date: str | None = None

    def to_dict(self) -> dict[Any, Any]:
        """
        Convert policy to dictionary format for API submission.

        Returns:
            Dictionary representation of policy
        """
        if not isinstance(self.underwriting_questions, list):
            LOGGER.debug("Missing or invalid underwriting questions")
            self.underwriting_questions = []

        quote_dict = self.__dict__

        if self.description == "":
            quote_dict.update({"description": f"From Policy {self.number[3:]}"})

        if not self.next_inspection_date:
            del quote_dict["next_inspection_date"]

        if not self.previous_inspection_date:
            del quote_dict["previous_inspection_date"]

        return quote_dict
