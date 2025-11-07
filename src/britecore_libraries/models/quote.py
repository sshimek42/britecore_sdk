"""BriteCore policy model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Union

from sclogging import sclogging_main as scl

_LOGGER = scl.get_parent_logger()


@dataclass
class BritecoreQuote:
    """
    BriteCore quote model.
    """

    number: str
    policy_type_id: str
    agency_id: str
    named_insureds: list
    risks: list
    underwriting_questions: Union[list, None] = None
    description: Optional[str] = ""
    number_origin: str = "manual"
    transaction_type: str = "renewal"
    term_type: str = "1 Year"
    inception_date: str = datetime.today().strftime("%Y-%m-%d")
    effective_date: str = datetime.today().strftime("%Y-%m-%d")
    next_inspection_date: Union[None, str] = None
    previous_inspection_date: Union[None, str] = None

    def to_dict(self) -> dict:
        """
        Convert policy to dictionary format for API submission.

        Returns:
            Dictionary representation of policy
        """

        if not isinstance(self.underwriting_questions, list):
            _LOGGER.debug("Missing or invalid underwriting questions")
            self.underwriting_questions = []

        # if isinstance(self.inception_date, str):
        #     self.inception_date = datetime.strptime(
        #         self.inception_date, "%Y-%m-%d"
        #         )

        quote_dict = {
            "number": self.number,
            "number_origin": self.number_origin,
            "underwriting_questions": self.underwriting_questions,
            "effective_date": self.effective_date,
            "policy_type_id": self.policy_type_id,
            "transaction_type": self.transaction_type,
            "term_type": self.term_type,
            "agency_id": self.agency_id,
            "named_insureds": self.named_insureds,
            "risks": self.risks,
            "inception_date": self.inception_date,
            "description": self.description,
        }

        if self.description == "":
            quote_dict.update({"description": f"From Policy {self.number[3:]}"})

        if self.next_inspection_date:
            quote_dict.update({"next_inspection_date": self.next_inspection_date})

        if self.previous_inspection_date:
            quote_dict.update(
                {"previous_inspection_date": self.previous_inspection_date}
            )

        return quote_dict
