import os
from typing import Optional

from britecore_libraries.api.britecore_async_api_client import AsyncBritecoreAPIClient
from britecore_libraries.api.britecore_api_client import (
    BritecoreAPIClient,
    RequestParameters,
)


def init_api_client(target_site: Optional[str] = None) -> BritecoreAPIClient:
    """
    Initializes and returns a configured Britecore API client instance.

    This function creates a new BritecoreAPIClient object using the specified target site
    and initializes the client connection. The target site can be provided as an argument
    or will default to the value of the 'target_site' environment variable.

    Args:
        target_site: The target site URL or identifier for the Britecore API.
                     Defaults to the value of the 'target_site' environment variable.

    Returns:
        BritecoreAPIClient: A configured and initialized Britecore API client instance.

    """

    resolved_target_site = target_site or os.environ.get("target_site")
    _api_client: BritecoreAPIClient = BritecoreAPIClient(resolved_target_site)
    _api_client.init_client()
    return _api_client


def init_async_api_client(target_site: Optional[str] = None) -> AsyncBritecoreAPIClient:
    """Initialize and return a lazy async API client wrapper."""
    resolved_target_site = target_site or os.environ.get("target_site")
    return AsyncBritecoreAPIClient(resolved_target_site)


# Lazy initialization: _api_client is only created on first access to avoid
# import-time failures in contexts without config/env setup.
_api_client: BritecoreAPIClient | None = None
_async_api_client: AsyncBritecoreAPIClient | None = None


def get_api_client() -> BritecoreAPIClient:
    """
    Get or lazily initialize the global API client instance.

    Returns:
        BritecoreAPIClient: A configured and initialized Britecore API client instance.

    Raises:
        Any exceptions from BritecoreAPIClient.init_client() if initialization fails.
    """
    global _api_client
    if _api_client is None:
        _api_client = init_api_client()
    return _api_client


def get_async_api_client() -> AsyncBritecoreAPIClient:
    """Get or lazily initialize the global async API client instance."""
    global _async_api_client
    if _async_api_client is None:
        _async_api_client = init_async_api_client()
    return _async_api_client


# Backward compatibility: module-level api_client proxy that triggers lazy init
class _LazyAPIClient:
    """Lazy-loading proxy for the global API client."""

    def __getattr__(self, name: str):
        return getattr(get_api_client(), name)


api_client = _LazyAPIClient()


class _LazyAsyncAPIClient:
    """Lazy-loading proxy for the global async API client."""

    def __getattr__(self, name: str):
        return getattr(get_async_api_client(), name)


async_api_client = _LazyAsyncAPIClient()


# Lazy module attributes for timeouts (accessed via get_api_client())
class _LazyModule:
    """Module-level lazy loader for timeout attributes."""

    @property
    def web_timeout_long(self) -> int:
        """Get or lazily initialize web_timeout_long from the API client."""
        return get_api_client().web_timeout_long

    @property
    def web_timeout(self) -> int:
        """Get or lazily initialize web_timeout from the API client."""
        return get_api_client().web_timeout


# Fallback values for direct access (will be overridden by lazy loading on first access)
def _get_web_timeout_long() -> int:
    """Lazy getter for web_timeout_long."""
    return get_api_client().web_timeout_long


def _get_web_timeout() -> int:
    """Lazy getter for web_timeout."""
    return get_api_client().web_timeout


__all__ = [
    "RequestParameters",
    "api_client",
    "async_api_client",
    "get_api_client",
    "get_async_api_client",
    "init_api_client",
    "init_async_api_client",
    "BritecoreAPIClient",
    "AsyncBritecoreAPIClient",
]
