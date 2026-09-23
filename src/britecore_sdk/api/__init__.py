"""BriteCore API client and authentication."""

from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.britecore_async_api_client import AsyncBritecoreAPIClient
from britecore_sdk.api.britecore_oauth_token_manager import OAuthToken
from britecore_sdk.api.request_cache import RequestCache, build_cache_key
from britecore_sdk.api.response_helpers import (
    extract_data,
    extract_items,
    get_message,
    is_successful_response,
    normalize_batch_results,
    normalize_pagination_envelope,
)

__all__ = [
    "OAuthToken",
    "BritecoreAPIClient",
    "AsyncBritecoreAPIClient",
    "RequestCache",
    "build_cache_key",
    "extract_data",
    "extract_items",
    "get_message",
    "is_successful_response",
    "normalize_batch_results",
    "normalize_pagination_envelope",
]
