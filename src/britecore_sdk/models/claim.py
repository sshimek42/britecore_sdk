"""BriteCore claim model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BritecoreClaim:
    """BriteCore claim model for create/update payload shaping."""

    claim_number: str
    policy_number: str
    claim_number_origin: str = "manual"
    claim_id: str | None = None
    status: str | None = None
    description: str | None = None
    loss_date: str | None = None
    catastrophe_id: str | None = None
    peril_id: str | None = None
    claimant_ids: list[str] = field(default_factory=list)
    system_tags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert claim data to dictionary format for API submission."""
        payload: dict[str, Any] = {
            "claim_number": self.claim_number,
            "policy_number": self.policy_number,
            "claim_number_origin": self.claim_number_origin,
            "claim_id": self.claim_id,
            "status": self.status,
            "description": self.description,
            "loss_date": self.loss_date,
            "catastrophe_id": self.catastrophe_id,
            "peril_id": self.peril_id,
            "claimant_ids": self.claimant_ids,
            "system_tags": self.system_tags,
        }
        return {
            key: value
            for key, value in payload.items()
            if value is not None and value != [] and value != {}
        }
