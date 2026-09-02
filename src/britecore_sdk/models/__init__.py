"""BriteCore domain models."""

from britecore_sdk.models.claim import BritecoreClaim
from britecore_sdk.models.contact import BritecoreContact
from britecore_sdk.models.policy import BritecorePolicy
from britecore_sdk.models.quote import BritecoreQuote
from britecore_sdk.models.workflow_results import (
    BatchItemResult,
    to_legacy_contact_result,
    to_legacy_quote_result,
)

__all__ = [
    "BatchItemResult",
    "BritecoreClaim",
    "BritecoreContact",
    "BritecorePolicy",
    "BritecoreQuote",
    "to_legacy_contact_result",
    "to_legacy_quote_result",
]
