"""BriteCore vehicle model."""

from dataclasses import dataclass
from typing import Any


@dataclass
class BritecoreVehicle:
    """Vehicle payload model for create/update operations."""

    quote_id: str
    vehicle_year: int
    vehicle_make: str
    vehicle_model: str
    vehicle_type: str
    vehicle_number: int
    address_line1: str
    address_city: str
    address_state: str
    address_zip: str
    address_county: str
    id: str | None = None
    address_line2: str | None = None
    cost_new: float | int | None = None
    included_in_policy: bool = True
    deleted: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert vehicle data to API payload format."""
        payload: dict[str, Any] = {
            "id": self.id,
            "quote_id": self.quote_id,
            "vehicle_year": self.vehicle_year,
            "vehicle_make": self.vehicle_make,
            "vehicle_model": self.vehicle_model,
            "vehicle_type": self.vehicle_type,
            "vehicle_number": self.vehicle_number,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "address_city": self.address_city,
            "address_state": self.address_state,
            "address_zip": self.address_zip,
            "address_county": self.address_county,
            "cost_new": self.cost_new,
            "included_in_policy": self.included_in_policy,
            "deleted": self.deleted,
        }
        return {
            key: value
            for key, value in payload.items()
            if value is not None and value != [] and value != {}
        }
