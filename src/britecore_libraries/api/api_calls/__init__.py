import os
from typing import cast

from britecore_libraries.api.britecore_api_client import (
    BritecoreAPIClient,
    RequestParameters,
)
from britecore_libraries.api.britecore_async_api_client import AsyncBritecoreAPIClient
from britecore_libraries.exceptions import BritecoreError


def init_api_client(target_site: str | None = None) -> BritecoreAPIClient:
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


def init_async_api_client(target_site: str | None = None) -> AsyncBritecoreAPIClient:
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
        BritecoreError.Base: If lazy initialization fails.
        Any exceptions from BritecoreAPIClient.init_client() if initialization fails.
    """
    global _api_client
    if _api_client is None:
        _api_client = init_api_client()
    if _api_client is None:
        raise BritecoreError.Base(
            "API client initialization returned None; check configuration"
        )
    return _api_client


def get_async_api_client() -> AsyncBritecoreAPIClient:
    """
    Get or lazily initialize the global async API client instance.

    Returns:
        AsyncBritecoreAPIClient: A configured async API client instance.

    Raises:
        BritecoreError.Base: If lazy initialization fails.
    """
    global _async_api_client
    if _async_api_client is None:
        _async_api_client = init_async_api_client()
    if _async_api_client is None:
        raise BritecoreError.Base(
            "Async API client initialization returned None; check configuration"
        )
    return _async_api_client


# Backward compatibility: module-level api_client proxy that triggers lazy init
class _LazyAPIClient:
    """Lazy-loading proxy for the global API client.

    ``__func__ = None`` prevents Python 3.14's ``unittest.mock._is_async_obj``
    from triggering lazy initialisation via ``hasattr(proxy, '__func__')``.
    """

    __func__ = None  # sentinel: stops mock.__enter__ from probing __getattr__

    def __getattr__(self, name: str):
        return getattr(get_api_client(), name)


api_client: BritecoreAPIClient = cast(
    BritecoreAPIClient, cast(object, _LazyAPIClient())
)


class _LazyAsyncAPIClient:
    """Lazy-loading proxy for the global async API client.

    ``__func__ = None`` prevents Python 3.14's ``unittest.mock._is_async_obj``
    from triggering lazy initialisation via ``hasattr(proxy, '__func__')``.
    """

    __func__ = None  # sentinel: stops mock.__enter__ from probing __getattr__

    def __getattr__(self, name: str):
        return getattr(get_async_api_client(), name)


async_api_client: AsyncBritecoreAPIClient = cast(
    AsyncBritecoreAPIClient, cast(object, _LazyAsyncAPIClient())
)


# Safe fallback timeout values used by modules that import these names at
# import-time. They intentionally do not force client initialization.
# Once a client is initialized, request methods still use the client's own
# configured timeout values unless a wrapper explicitly passes these fallbacks.
web_timeout_long: int = 50
web_timeout: int = 5


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
    "web_timeout_long",
    "web_timeout",
]


def __getattr__(name: str):
    """
    Lazily expose module attributes via PEP 562.

    Timeout values are read from the initialized API client instance so that
    multiple clients with different configurations do not share one global
    timeout state.
    """
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
