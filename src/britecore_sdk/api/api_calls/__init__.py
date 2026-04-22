# ...existing code...
from typing import cast

from britecore_sdk.api.britecore_api_client import (
    BritecoreAPIClient,
    RequestParameters,
)
from britecore_sdk.api.britecore_async_api_client import AsyncBritecoreAPIClient
from britecore_sdk.exceptions import BritecoreError
from britecore_sdk.settings import get_target_site

_TARGET_SITE_UNSET = object()


def _set_module_client_state(name: str, client: object) -> None:
    """Set module-level client state without using global statements."""
    globals()[name] = client


def init_api_client(
    target_site: str | None | object = _TARGET_SITE_UNSET,
) -> BritecoreAPIClient:
    """
    Initializes and returns a configured Britecore API client instance.

    This function creates a new BritecoreAPIClient object using the specified target site
    and initializes the client connection.

    Calling this function also sets the module-level ``_api_client`` so that the
    lazy proxy (``api_client``) used by endpoint wrappers resolves to this instance
    rather than re-initialising without a site on first use.

    Args:
        target_site: The target site URL or identifier for the Britecore API.
                     If omitted, this is resolved from settings via
                     ``get_target_site()``. Passing ``None`` or an empty value
                     explicitly is treated as invalid input.

    Returns:
        BritecoreAPIClient: A configured and initialized Britecore API client instance.

    """
    resolved = get_target_site() if target_site is _TARGET_SITE_UNSET else target_site
    if not isinstance(resolved, str) or not resolved:
        raise BritecoreError.ConfigurationError(
            "target_site must be specified: pass a non-empty value, or omit the argument "
            "to use configured fallback resolution."
        )
    client: BritecoreAPIClient = BritecoreAPIClient(resolved)
    client.init_client()
    _set_module_client_state("_api_client", client)
    return client


def init_async_api_client(
    target_site: str | None | object = _TARGET_SITE_UNSET,
) -> AsyncBritecoreAPIClient:
    """Initialize and return a lazy async API client wrapper.

    The target site may be provided explicitly. If omitted, it is resolved
    from settings via ``get_target_site()``.

    Also sets the module-level ``_async_api_client`` so the lazy proxy resolves
    to this instance rather than re-initialising without a site on first use.
    """
    resolved = get_target_site() if target_site is _TARGET_SITE_UNSET else target_site
    if not isinstance(resolved, str) or not resolved:
        raise BritecoreError.ConfigurationError(
            "target_site must be specified: pass a non-empty value, or omit the argument "
            "to use configured fallback resolution."
        )
    client = AsyncBritecoreAPIClient(resolved)
    _set_module_client_state("_async_api_client", client)
    return client


def reset_api_client() -> None:
    """Reset the module-level API client to ``None``.

    Useful for test isolation and multi-site workflows where a fresh client
    should be initialized for a different target site.  After calling this,
    the next call to :func:`get_api_client` (or any endpoint wrapper) will
    raise :class:`~britecore_sdk.exceptions.BritecoreError.ConfigurationError`
    until :func:`init_api_client` is called again.

    Example::

        from britecore_sdk.api.api_calls import init_api_client, reset_api_client

        client_a = init_api_client("site_a")
        reset_api_client()
        client_b = init_api_client("site_b")
    """
    _set_module_client_state("_api_client", None)
    _set_module_client_state("_async_api_client", None)


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
    if _api_client is None:
        raise BritecoreError.ConfigurationError(
            "API client has not been initialized. Call init_api_client(target_site=...) first.\n"
            "Tip: To check your site configuration, run: python -m britecore_sdk.utils.check_site_configs"
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
    if _async_api_client is None:
        raise BritecoreError.ConfigurationError(
            "Async API client has not been initialized. Call init_async_api_client(target_site=...) first."
        )
    return _async_api_client


# Module-level api_client proxy that triggers lazy init
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


# Default timeout values used by modules that import these names at
# import-time. They intentionally do not force client initialization.
# Once a client is initialized, request methods still use the client's own
# configured timeout values unless a wrapper explicitly passes these values.
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
    "reset_api_client",
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
