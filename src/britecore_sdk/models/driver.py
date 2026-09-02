"""BriteCore driver model."""

from dataclasses import dataclass
from typing import Any


@dataclass
class BritecoreDriver:
    """Driver payload model for create/update operations."""

    quote_id: str
    name: str
    date_of_birth: str
    license_state: str
    license_number: str
    id: str | None = None
    gender: str | None = None
    license_class: str | None = None
    marital_status: str | None = None
    occupation: str | None = None
    years_driving_experience: int | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert driver data to API payload format."""
        payload: dict[str, Any] = {
            "id": self.id,
            "quote_id": self.quote_id,
            "name": self.name,
            "date_of_birth": self.date_of_birth,
            "gender": self.gender,
            "license_state": self.license_state,
            "license_number": self.license_number,
            "license_class": self.license_class,
            "marital_status": self.marital_status,
            "occupation": self.occupation,
            "years_driving_experience": self.years_driving_experience,
        }
        return {
            key: value
            for key, value in payload.items()
            if value is not None and value != [] and value != {}
        }
