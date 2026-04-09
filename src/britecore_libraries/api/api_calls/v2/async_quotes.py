"""BriteCore v2 Async Quotes API endpoint wrappers.

Asynchronous (cached) counterparts to the synchronous wrappers in quotes.py.
Uses AsyncBritecoreAPIClient for non-blocking, TTL-cached HTTP requests.

Provides:
    async_create_full_quote -- Async create a full quote from a JSON payload.
    async_get_quote         -- Async retrieve a quote by ID (cached by default).
"""

from logging import Logger
from typing import Any, Unpack

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    AsyncBritecoreAPIClient,
    RequestParameters,
    async_api_client,
)

LOGGER: Logger = logger

API_CLIENT: AsyncBritecoreAPIClient = async_api_client
QUOTE_CACHE_NAMESPACE = "quotes"
DEFAULT_CACHE_TTL_SECONDS = 60


def _apply_quote_read_cache(
    kwargs: dict[str, Any], *, cache_key_parts: list[str] | None = None
) -> dict[str, Any]:
    """Apply default caching for quote read requests while allowing overrides."""
    kwargs.setdefault("cache_enabled", True)
    kwargs.setdefault("cache_namespace", QUOTE_CACHE_NAMESPACE)
    kwargs.setdefault("cache_ttl_seconds", DEFAULT_CACHE_TTL_SECONDS)
    if cache_key_parts:
        kwargs.setdefault("cache_key_parts", cache_key_parts)
    return kwargs


def _apply_quote_mutation_cache(kwargs: dict[str, Any]) -> dict[str, Any]:
    """Invalidate cached quote reads after a successful quote mutation."""
    kwargs.setdefault("cache_invalidate_on_success", [QUOTE_CACHE_NAMESPACE])
    return kwargs


async def acreate_full_quote(
    quote_json: dict[str, Any], **kwargs: Unpack[RequestParameters]
) -> tuple[dict[str, Any] | None, str | None]:
    """Create a full quote asynchronously.

    Use ``quote_json`` for the complete quote payload expected by the quote-create
    workflow exposed by this SDK. Returns the async ``aprocess_result(...)``
    payload together with the extracted quote ID, invalidates cached quote reads
    on success, and accepts ``RequestParameters`` overrides via ``**kwargs``.
    """
    request_kwargs = _apply_quote_mutation_cache(dict(kwargs))
    request_result: Any = await API_CLIENT.ado_request(
        path="/api/v2/quotes/create_full_quote",
        json=quote_json,
        **request_kwargs,
    )
    json_info: Any = await API_CLIENT.aprocess_result(request_result)

    if not json_info:
        return None, None

    return json_info, json_info.get("id")


async def aget_quote(id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a quote by ID with short-lived async caching enabled by default.

    The request uses ``id`` to fetch the quote through the async quote client and
    enables the default quote read cache unless the caller overrides it. Returns
    the async ``aprocess_result(...)`` payload, and ``**kwargs`` accepts
    ``RequestParameters`` plus cache override settings.
    """
    quote_json: dict[str, str] = {"id": id}
    LOGGER.debug("Getting quote")
    request_kwargs = _apply_quote_read_cache(
        dict(kwargs), cache_key_parts=[f"quote:{id}"]
    )
    request_result: Any = await API_CLIENT.ado_request(
        path="/api/v2/quotes/get_quote",
        json=quote_json,
        **request_kwargs,
    )
    return await API_CLIENT.aprocess_result(request_result)


__all__ = ["acreate_full_quote", "aget_quote"]
