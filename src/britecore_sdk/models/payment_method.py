"""BriteCore payment method model."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class BritecorePaymentMethod:
    """Payment method payload model for create/update operations."""

    contact_id: str
    method: str
    account_name: str
    name_on_account: str
    masked_number: str
    id: str | None = None
    account_type: str | None = None
    masked_routing: str | None = None
    expire_date: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    address_city: str | None = None
    address_state: str | None = None
    address_zip: str | None = None
    primary_account: bool = False
    active: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert payment method data to API payload format."""
        payload: dict[str, Any] = {
            "id": self.id,
            "contact_id": self.contact_id,
            "method": self.method,
            "account_type": self.account_type,
            "account_name": self.account_name,
            "name_on_account": self.name_on_account,
            "masked_number": self.masked_number,
            "masked_routing": self.masked_routing,
            "expire_date": self.expire_date,
            "address_line1": self.address_line1,
            "address_line2": self.address_line2,
            "address_city": self.address_city,
            "address_state": self.address_state,
            "address_zip": self.address_zip,
            "primary_account": self.primary_account,
            "active": self.active,
            "metadata": self.metadata,
        }
        return {
            key: value
            for key, value in payload.items()
            if value is not None and value != [] and value != {}
        }
