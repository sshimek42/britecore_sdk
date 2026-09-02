import warnings
from contextlib import contextmanager
from contextvars import ContextVar
from typing import NotRequired, TypedDict, cast

from britecore_sdk.api.britecore_api_client import (
    BritecoreAPIClient,
    RequestParameters,
)
from britecore_sdk.api.britecore_async_api_client import AsyncBritecoreAPIClient
from britecore_sdk.exceptions import BritecoreError
from britecore_sdk.settings import get_target_site


class InitClientParams(TypedDict):
    """Typed parameters for BritecoreAPIClient.init_client()."""

    client_dry_run: NotRequired[bool]
    debug_include_request_body: NotRequired[bool]
    base_url: NotRequired[str | None]
    api_key: NotRequired[str | None]
    client_id: NotRequired[str | None]
    client_secret: NotRequired[str | None]
    enable_rate_limiter: NotRequired[bool | None]
    rate_limiter_requests_per_second: NotRequired[float | None]
    rate_limiter_burst_size: NotRequired[int | None]
    rate_limiter_adaptive_backoff: NotRequired[bool | None]
    rate_limiter_backoff_timeout_seconds: NotRequired[float | None]


class AsyncInitClientParams(TypedDict):
    """Typed parameters for AsyncBritecoreAPIClient initialization."""

    client_dry_run: NotRequired[bool]
    base_url: NotRequired[str | None]
    api_key: NotRequired[str | None]
    client_id: NotRequired[str | None]
    client_secret: NotRequired[str | None]


_TARGET_SITE_UNSET = object()
_DEPRECATION_REMOVAL_VERSION = "v3.0.0"
_INIT_API_CLIENT_DEPRECATION = (
    "init_api_client() is deprecated as a primary application pattern and will be "
    f"removed in {_DEPRECATION_REMOVAL_VERSION}. Create a BritecoreAPIClient(...)."
    "init_client() instance explicitly and pass client=... to wrappers or workflows."
)
_INIT_ASYNC_API_CLIENT_DEPRECATION = (
    "init_async_api_client() is deprecated as a primary application pattern and will "
    f"be removed in {_DEPRECATION_REMOVAL_VERSION}. Create an "
    "AsyncBritecoreAPIClient(...) explicitly and pass client=... to async wrappers "
    "or workflows."
)
_RESET_API_CLIENT_DEPRECATION = (
    f"reset_api_client() is deprecated and will be removed in {_DEPRECATION_REMOVAL_VERSION}. "
    "Prefer explicit client instances or scoped use_api_client(...) binding instead of "
    "resetting module-level state."
)
_IMPLICIT_SYNC_CLIENT_FALLBACK_DEPRECATION = (
    "Implicit wrapper client fallback without explicit client= is deprecated and will "
    f"be removed in {_DEPRECATION_REMOVAL_VERSION}. Pass client=... explicitly, or "
    "use use_api_client(...) for scoped sync wrapper calls."
)
_IMPLICIT_ASYNC_CLIENT_FALLBACK_DEPRECATION = (
    "Implicit async wrapper client fallback without explicit client= is deprecated and "
    f"will be removed in {_DEPRECATION_REMOVAL_VERSION}. Pass client=... explicitly "
    "to async wrappers or workflows."
)
_context_api_client: ContextVar[BritecoreAPIClient | None] = ContextVar(
    "_context_api_client", default=None
)


def _set_module_client_state(name: str, client: object) -> None:
    """Set module-level client state without using global statements."""
    globals()[name] = client


def _warn_deprecated_runtime_path(message: str, *, stacklevel: int) -> None:
    """Emit a deprecation warning for legacy runtime patterns retained for compatibility."""
    warnings.warn(message, DeprecationWarning, stacklevel=stacklevel)


def init_api_client(
    target_site: str | None | object = _TARGET_SITE_UNSET,
    *,
    client_dry_run: bool = False,
    base_url: str | None = None,
    api_key: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
    enable_rate_limiter: bool | None = None,
    rate_limiter_requests_per_second: float | None = None,
    rate_limiter_burst_size: int | None = None,
    rate_limiter_adaptive_backoff: bool | None = None,
    rate_limiter_backoff_timeout_seconds: float | None = None,
) -> BritecoreAPIClient:
    """
    Initializes and returns a configured Britecore API client instance.

    This function creates a new BritecoreAPIClient object using the specified target site
    and initializes the client connection.

    Calling this function also sets the module-level ``_api_client`` so that the
    lazy proxy (``api_client``) used by endpoint wrappers resolves to this instance
    rather than re-initialising without a site on first use.

    Credentials can be supplied in two ways:

    **File-based (default):** omit all credential kwargs.  The client reads credentials
    from the layered config file search hierarchy (SDK defaults →
    ``~/.britecore/`` → CWD → ``BRITECORE_SDK_SETTINGS_FILE``).

    **Explicit (inline):** pass ``base_url`` (required) plus any combination of
    ``api_key``, ``client_id``, and ``client_secret``.  When ``base_url`` is given,
    no config files are read and ``target_site`` becomes optional (defaults to
    ``"explicit"`` when omitted).

    **Rate Limiting (optional):** pass ``enable_rate_limiter=True`` to enable
    client-side rate limiting. Configuration can be provided explicitly via
    ``rate_limiter_*`` parameters, or read from settings.toml if omitted.

    Args:
        target_site: The target site URL or identifier for the Britecore API.
                     If omitted, this is resolved from settings via
                     ``get_target_site()``. Passing ``None`` or an empty value
                     explicitly is treated as invalid input **unless** ``base_url``
                     is also provided, in which case ``"explicit"`` is used as the
                     site label.
        client_dry_run: When ``True``, requests made through this client inherit
                         dry-run behavior unless explicitly overridden per call.
        base_url: Override the site base URL directly.  When provided, file-based
            credential lookup is bypassed and ``target_site`` becomes optional.
        api_key: Explicit API key (used only when ``base_url`` is also given).
        client_id: Explicit OAuth client ID (used only when ``base_url`` is given).
        client_secret: Explicit OAuth client secret (used only when ``base_url`` is given).
        enable_rate_limiter: Enable client-side rate limiting. When ``None`` (default),
            reads from settings ``rate_limiter_enabled``. When ``True`` or ``False``,
            overrides the setting.
        rate_limiter_requests_per_second: Target request rate for rate limiter
            (default: 10.0 req/s from settings). Only used if rate limiter is enabled.
        rate_limiter_burst_size: Maximum burst capacity for rate limiter
            (default: 20 requests from settings). Only used if rate limiter is enabled.
        rate_limiter_adaptive_backoff: Enable automatic backoff on 429 responses
            (default: True from settings). Only used if rate limiter is enabled.
        rate_limiter_backoff_timeout_seconds: Duration to back off after 429
            (default: 60.0 seconds from settings). Only used if rate limiter is enabled.

    Returns:
        BritecoreAPIClient: A configured and initialized Britecore API client instance.

    """
    _warn_deprecated_runtime_path(_INIT_API_CLIENT_DEPRECATION, stacklevel=2)

    if base_url is not None:
        # Explicit-credential mode: target_site is optional
        if (
            target_site is _TARGET_SITE_UNSET
            or not isinstance(target_site, str)
            or not target_site
        ):
            resolved: str = "explicit"
        else:
            resolved = target_site
    else:
        resolved = cast(
            str,
            get_target_site() if target_site is _TARGET_SITE_UNSET else target_site,
        )
        if not isinstance(resolved, str) or not resolved:
            raise BritecoreError.ConfigurationError(
                "target_site must be specified: pass a non-empty value, or omit the argument "
                "to use configured fallback resolution."
            )

    client: BritecoreAPIClient = BritecoreAPIClient(resolved)
    kwargs: InitClientParams = {"client_dry_run": client_dry_run}
    if base_url is not None:
        # Explicit-credential mode: always pass all credential kwargs explicitly
        kwargs["base_url"] = base_url
        kwargs["api_key"] = api_key
        kwargs["client_id"] = client_id
        kwargs["client_secret"] = client_secret
    else:
        # File-based mode: only pass credentials if they're provided
        if api_key is not None:
            kwargs["api_key"] = api_key
        if client_id is not None:
            kwargs["client_id"] = client_id
        if client_secret is not None:
            kwargs["client_secret"] = client_secret
    # Rate limiter options — always forwarded (None means "use settings default")
    kwargs["enable_rate_limiter"] = enable_rate_limiter
    if rate_limiter_requests_per_second is not None:
        kwargs["rate_limiter_requests_per_second"] = rate_limiter_requests_per_second
    if rate_limiter_burst_size is not None:
        kwargs["rate_limiter_burst_size"] = rate_limiter_burst_size
    if rate_limiter_adaptive_backoff is not None:
        kwargs["rate_limiter_adaptive_backoff"] = rate_limiter_adaptive_backoff
    if rate_limiter_backoff_timeout_seconds is not None:
        kwargs["rate_limiter_backoff_timeout_seconds"] = (
            rate_limiter_backoff_timeout_seconds
        )
    client.init_client(**kwargs)
    _set_module_client_state("_api_client", client)
    return client


def init_async_api_client(
    target_site: str | None | object = _TARGET_SITE_UNSET,
    *,
    client_dry_run: bool = False,
    base_url: str | None = None,
    api_key: str | None = None,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> AsyncBritecoreAPIClient:
    """Initialize and return a lazy async API client wrapper.

    The target site may be provided explicitly. If omitted, it is resolved
    from settings via ``get_target_site()``.

    Also sets the module-level ``_async_api_client`` so the lazy proxy resolves
    to this instance rather than re-initialising without a site on first use.

    Credentials can be supplied in two ways:

    **File-based (default):** omit all credential kwargs.  The client reads credentials
    from the layered config file search hierarchy.

    **Explicit (inline):** pass ``base_url`` plus optional ``api_key``,
    ``client_id``, and ``client_secret``.  File-based lookup is bypassed, and
    ``target_site`` defaults to ``"explicit"`` when omitted.

    Args:
        target_site: Explicit target site name. If omitted, resolve from settings.
        client_dry_run: When ``True``, async requests inherit dry-run behavior
            unless explicitly overridden per call.
        base_url: Override the site base URL directly.
        api_key: Explicit API key (used only when ``base_url`` is also given).
        client_id: Explicit OAuth client ID (used only when ``base_url`` is given).
        client_secret: Explicit OAuth client secret (used only when ``base_url`` is given).
    """
    _warn_deprecated_runtime_path(_INIT_ASYNC_API_CLIENT_DEPRECATION, stacklevel=2)

    if base_url is not None:
        if (
            target_site is _TARGET_SITE_UNSET
            or not isinstance(target_site, str)
            or not target_site
        ):
            resolved = "explicit"
        else:
            resolved = target_site
    else:
        resolved = cast(
            str,
            get_target_site() if target_site is _TARGET_SITE_UNSET else target_site,
        )
        if not isinstance(resolved, str) or not resolved:
            raise BritecoreError.ConfigurationError(
                "target_site must be specified: pass a non-empty value, or omit the argument "
                "to use configured fallback resolution."
            )
    async_kwargs: AsyncInitClientParams = {
        "client_dry_run": client_dry_run,
    }
    if base_url is not None:
        async_kwargs["base_url"] = base_url
    if api_key is not None:
        async_kwargs["api_key"] = api_key
    if client_id is not None:
        async_kwargs["client_id"] = client_id
    if client_secret is not None:
        async_kwargs["client_secret"] = client_secret
    client = AsyncBritecoreAPIClient(resolved, **async_kwargs)
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
    _warn_deprecated_runtime_path(_RESET_API_CLIENT_DEPRECATION, stacklevel=2)
    _set_module_client_state("_api_client", None)
    _set_module_client_state("_async_api_client", None)


@contextmanager
def use_api_client(client: BritecoreAPIClient):
    """Temporarily bind a specific sync client for endpoint wrapper calls.

    Within this context, wrappers that access ``api_client``/``API_CLIENT``
    resolve to ``client`` instead of the module-level global ``_api_client``.
    This enables safe multi-site workflows without resetting global state.
    """
    token = _context_api_client.set(client)
    try:
        yield client
    finally:
        _context_api_client.reset(token)


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
    context_client = _context_api_client.get()
    if context_client is not None:
        return context_client

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


def resolve_client(
    client: BritecoreAPIClient | None = None,
) -> BritecoreAPIClient:
    """
    Resolve an explicit client or fall back to the module-level client.

    This helper is used by endpoint wrappers to support the v2.0.0 explicit client
    pattern while maintaining backwards compatibility with implicit module-level client usage.

    **Explicit client (v2.0.0 recommended):**

    .. code-block:: python

        from britecore_sdk import BritecoreAPIClient
        from britecore_sdk.api.api_calls.v2 import quotes

        client = BritecoreAPIClient("site").init_client()
        quote = quotes.retrieve_quote(quote_number="Q123", client=client)

    **Implicit client (v1.x pattern, still works but deprecated in v2.0.0):**

    .. code-block:: python

        from britecore_sdk.api.api_calls import init_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        init_api_client(target_site="site")
        quote = quotes.retrieve_quote(quote_number="Q123")  # Uses module-level client

    Args:
        client: Optional explicit client instance. If ``None``, falls back to the
            module-level client via ``get_api_client()``.

    Returns:
        BritecoreAPIClient: The resolved client instance.

    Raises:
        BritecoreError.ConfigurationError: If no client is provided and the
            module-level client has not been initialized.
    """
    if client is not None:
        return client
    if _context_api_client.get() is None:
        _warn_deprecated_runtime_path(
            _IMPLICIT_SYNC_CLIENT_FALLBACK_DEPRECATION,
            stacklevel=3,
        )
    return get_api_client()


def aresolve_client(
    client: AsyncBritecoreAPIClient | None = None,
) -> AsyncBritecoreAPIClient:
    """
    Resolve an explicit async client or fall back to the module-level async client.

    This is the async equivalent of :func:`resolve_client`.

    Args:
        client: Optional explicit async client instance. If ``None``, falls back to the
            module-level async client via ``get_async_api_client()``.

    Returns:
        AsyncBritecoreAPIClient: The resolved async client instance.

    Raises:
        BritecoreError.ConfigurationError: If no client is provided and the
            module-level async client has not been initialized.
    """
    if client is not None:
        return client
    _warn_deprecated_runtime_path(
        _IMPLICIT_ASYNC_CLIENT_FALLBACK_DEPRECATION,
        stacklevel=3,
    )
    return get_async_api_client()


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
    "resolve_client",
    "aresolve_client",
    "use_api_client",
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
