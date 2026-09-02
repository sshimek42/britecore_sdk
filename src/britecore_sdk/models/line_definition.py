"""BriteCore line definition model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BritecoreLineDefinition:
    """Line definition payload for line/policy-type workflows."""

    location_id: str
    effective_date_id: str
    name: str
    policy_types: list[str] = field(default_factory=list)
    id: str | None = None
    description: str | None = None
    line: dict[str, Any] | None = None
    system_tags: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert line definition data to API payload format."""
        payload: dict[str, Any] = {
            "id": self.id,
            "location_id": self.location_id,
            "effective_date_id": self.effective_date_id,
            "name": self.name,
            "description": self.description,
            "policy_types": self.policy_types,
            "line": self.line,
            "system_tags": self.system_tags,
        }
        return {
            key: value
            for key, value in payload.items()
            if value is not None and value != [] and value != {}
        }
