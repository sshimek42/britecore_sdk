"""BriteCore coverage model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BritecoreCoverage:
    """Coverage payload model for create/update operations."""

    name: str
    coverage_type: str
    id: str | None = None
    description: str | None = None
    limit_amount: float | int | None = None
    deductible_amount: float | int | None = None
    annual_premium: float | int | None = None
    sub_line_id: str | None = None
    policy_type_item_id: str | None = None
    system_tags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert coverage data to API payload format."""
        payload: dict[str, Any] = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "coverage_type": self.coverage_type,
            "limit_amount": self.limit_amount,
            "deductible_amount": self.deductible_amount,
            "annual_premium": self.annual_premium,
            "sub_line_id": self.sub_line_id,
            "policy_type_item_id": self.policy_type_item_id,
            "system_tags": self.system_tags,
        }
        return {
            key: value
            for key, value in payload.items()
            if value is not None and value != [] and value != {}
        }
