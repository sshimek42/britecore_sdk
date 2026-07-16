"""v2.0.0 Typed Response Models for BriteCore API.

This module provides dataclass-based response models for all major API domains,
enabling type-safe access to API responses with IDE autocomplete support.

**Basic Usage:**

    from britecore_sdk import BritecoreAPIClient
    from britecore_sdk.api.api_calls.v2 import quotes
    from britecore_sdk.api.responses import QuoteResponse

    client = BritecoreAPIClient("site").init_client()

    # Returns typed QuoteResponse instead of dict
    quote: QuoteResponse = quotes.retrieve_quote(
        quote_number="Q123",
        client=client
    )

    # Type-safe access with IDE autocomplete
    print(f"Premium: {quote.premium}")
    print(f"Status: {quote.status}")
    print(f"Term Days: {quote.term_days}")

**Response Envelope Pattern:**

For complex responses, use ResponseEnvelope to access metadata:

    from britecore_sdk.api.responses import ResponseEnvelope

    envelope: ResponseEnvelope = api_client.process_result(...)
    print(f"Success: {envelope.success}")
    print(f"Request ID: {envelope.request_id}")
    print(f"Status Code: {envelope.status_code}")
    print(f"Data: {envelope.data}")
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ResponseEnvelope:
    """Base envelope for all API responses.

    This wraps the typical BriteCore API response format:

    .. code-block:: json

        {
            "success": true,
            "data": { ... },
            "message": "Success",
            "messages": []
        }
    """

    success: bool = True
    data: Any = None
    message: str | None = None
    messages: list[str] = field(default_factory=list)
    request_id: str = ""
    status_code: int = 200

    @classmethod
    def from_api(
        cls, data: dict[str, Any], request_id: str = "", status_code: int = 200
    ) -> "ResponseEnvelope":
        """Parse API response dict into ResponseEnvelope."""
        return cls(
            success=data.get("success", True),
            data=data.get("data"),
            message=data.get("message"),
            messages=data.get("messages", []),
            request_id=request_id,
            status_code=status_code,
        )


# ============================================================================
# QUOTE RESPONSES
# ============================================================================


@dataclass
class QuoteResponse:
    """Typed response for quote operations."""

    id: str
    quote_number: str
    status: str
    premium: float
    term_days: int
    effective_date: str
    expiration_date: str | None = None
    created_date: str | None = None
    modified_date: str | None = None
    quote_type: str | None = None
    carrier: str | None = None
    renewal_date: str | None = None
    renewal_premium: float | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "QuoteResponse":
        """Parse API response dict into QuoteResponse."""
        return cls(
            id=data.get("id", ""),
            quote_number=data.get("quoteNumber", data.get("quote_number", "")),
            status=data.get("status", ""),
            premium=float(data.get("premium", 0.0)),
            term_days=int(data.get("termDays", data.get("term_days", 0))),
            effective_date=data.get("effectiveDate", data.get("effective_date", "")),
            expiration_date=data.get("expirationDate", data.get("expiration_date")),
            created_date=data.get("createdDate", data.get("created_date")),
            modified_date=data.get("modifiedDate", data.get("modified_date")),
            quote_type=data.get("quoteType", data.get("quote_type")),
            carrier=data.get("carrier"),
            renewal_date=data.get("renewalDate", data.get("renewal_date")),
            renewal_premium=data.get("renewalPremium", data.get("renewal_premium")),
            raw_data=data,
        )


# ============================================================================
# POLICY RESPONSES
# ============================================================================


@dataclass
class PolicyResponse:
    """Typed response for policy operations."""

    id: str
    policy_number: str
    status: str
    customer_id: str | None = None
    effective_date: str | None = None
    expiration_date: str | None = None
    created_date: str | None = None
    modified_date: str | None = None
    policy_type: str | None = None
    carrier: str | None = None
    premium: float | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "PolicyResponse":
        """Parse API response dict into PolicyResponse."""
        return cls(
            id=data.get("id", ""),
            policy_number=data.get("policyNumber", data.get("policy_number", "")),
            status=data.get("status", ""),
            customer_id=data.get("customerId", data.get("customer_id")),
            effective_date=data.get("effectiveDate", data.get("effective_date")),
            expiration_date=data.get("expirationDate", data.get("expiration_date")),
            created_date=data.get("createdDate", data.get("created_date")),
            modified_date=data.get("modifiedDate", data.get("modified_date")),
            policy_type=data.get("policyType", data.get("policy_type")),
            carrier=data.get("carrier"),
            premium=data.get("premium"),
            raw_data=data,
        )


# ============================================================================
# CONTACT RESPONSES
# ============================================================================


@dataclass
class ContactResponse:
    """Typed response for contact operations."""

    id: str
    name: str
    email: str | None = None
    phone: str | None = None
    phone_extension: str | None = None
    contact_type: str | None = None
    company: str | None = None
    title: str | None = None
    address: str | None = None
    city: str | None = None
    state: str | None = None
    zip_code: str | None = None
    country: str | None = None
    created_date: str | None = None
    modified_date: str | None = None
    raw_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "ContactResponse":
        """Parse API response dict into ContactResponse."""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            email=data.get("email"),
            phone=data.get("phone"),
            phone_extension=data.get("phoneExtension", data.get("phone_extension")),
            contact_type=data.get("contactType", data.get("contact_type")),
            company=data.get("company"),
            title=data.get("title"),
            address=data.get("address"),
            city=data.get("city"),
            state=data.get("state"),
            zip_code=data.get("zipCode", data.get("zip_code")),
            country=data.get("country"),
            created_date=data.get("createdDate", data.get("created_date")),
            modified_date=data.get("modifiedDate", data.get("modified_date")),
            raw_data=data,
        )


# ============================================================================
# LIST RESPONSES
# ============================================================================


@dataclass
class ListResponse:
    """Generic list response wrapper with pagination metadata."""

    items: list[dict[str, Any]] = field(default_factory=list)
    total_count: int = 0
    page: int = 1
    page_size: int = 100
    is_last_page: bool = False
    raw_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "ListResponse":
        """Parse API response dict into ListResponse."""
        items = data.get("data", data.get("items", []))
        if not isinstance(items, list):
            items = [items] if items else []

        return cls(
            items=items,
            total_count=data.get("totalCount", data.get("total_count", len(items))),
            page=data.get("page", 1),
            page_size=data.get("pageSize", data.get("page_size", len(items))),
            is_last_page=data.get(
                "isLastPage", data.get("is_last_page", len(items) < 100)
            ),
            raw_data=data,
        )


# ============================================================================
# BATCH OPERATION RESPONSES
# ============================================================================


@dataclass
class BatchOperationResult:
    """Result for a single item in a batch operation."""

    index: int
    success: bool
    data: Any | None = None
    error: str | None = None
    error_code: str | None = None


@dataclass
class BatchOperationResponse:
    """Response for batch operations (quotes, policies, contacts)."""

    total: int
    succeeded: int
    failed: int
    results: list[BatchOperationResult] = field(default_factory=list)
    raw_data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "BatchOperationResponse":
        """Parse API response dict into BatchOperationResponse."""
        results_data = data.get("results", [])
        results = [
            BatchOperationResult(
                index=r.get("index", i),
                success=r.get("success", False),
                data=r.get("data"),
                error=r.get("error"),
                error_code=r.get("errorCode", r.get("error_code")),
            )
            for i, r in enumerate(results_data)
        ]

        succeeded = sum(1 for r in results if r.success)
        failed = len(results) - succeeded

        return cls(
            total=data.get("total", len(results)),
            succeeded=succeeded,
            failed=failed,
            results=results,
            raw_data=data,
        )


__all__ = [
    "ResponseEnvelope",
    "QuoteResponse",
    "PolicyResponse",
    "ContactResponse",
    "ListResponse",
    "BatchOperationResult",
    "BatchOperationResponse",
]
