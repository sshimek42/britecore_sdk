"""v2.0.0 Pagination Iterator Helpers.

Provides iterator and async iterator support for list endpoints,
eliminating manual page management.

**Basic Usage (Iterator Pattern):**

    from britecore_sdk import BritecoreAPIClient
    from britecore_sdk.api.iterators import iter_quotes

    client = BritecoreAPIClient("site").init_client()

    # Automatic pagination - no manual page management
    for quote in iter_quotes(client=client, limit=100):
        print(f"Quote: {quote['quoteNumber']}")
        process_quote(quote)

**Async Iterator Pattern:**

    from britecore_sdk.api.iterators import aiter_quotes

    async with AsyncBritecoreAPIClient("site").init_client() as client:
        async for quote in aiter_quotes(client=client):
            await process_quote(quote)

**Collect All Results:**

    # Get all results as a list
    all_quotes = list(iter_quotes(client=client))

    # Get all with async
    all_quotes = [q async for q in aiter_quotes(client=client)]
"""

from collections.abc import AsyncIterator, Iterator
from logging import Logger
from typing import Any, Unpack

from britecore_sdk import logger
from britecore_sdk.api.api_calls import (
    RequestParameters,
    aresolve_client,
    resolve_client,
)
from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.api.britecore_async_api_client import AsyncBritecoreAPIClient

LOGGER: Logger = logger


# ============================================================================
# QUOTES ITERATORS
# ============================================================================


def iter_quotes(
    *,
    client: BritecoreAPIClient | None = None,
    limit: int = 100,
    **kwargs: Unpack[RequestParameters],
) -> Iterator[dict[str, Any]]:
    """Iterate over all quotes with automatic pagination.

    This is a convenience iterator that handles page management automatically.
    Each quote is yielded individually, and pages are fetched on demand.

    Args:
        client: Optional explicit client. If omitted, uses module-level client.
        limit: Page size for each request (default: 100).
        **kwargs: Additional RequestParameters (timeout, headers, retry, etc.)

    Yields:
        dict: Individual quote records.

    Example:

        from britecore_sdk import BritecoreAPIClient
        from britecore_sdk.api.iterators import iter_quotes

        client = BritecoreAPIClient("site").init_client()

        for quote in iter_quotes(client=client):
            print(f"Quote: {quote['quoteNumber']}")
    """
    effective_client = resolve_client(client)
    page = 1

    while True:
        # Import here to avoid circular dependency
        from britecore_sdk.api.api_calls.v2 import quotes

        response = quotes.list_quotes(
            page=page, limit=limit, client=effective_client, **kwargs
        )

        if not response or not response.get("data"):
            break

        yield from response["data"]

        # Check if we've reached the last page
        if len(response.get("data", [])) < limit:
            break

        page += 1


async def aiter_quotes(
    *,
    client: AsyncBritecoreAPIClient | None = None,
    limit: int = 100,
    **kwargs: Unpack[RequestParameters],
) -> AsyncIterator[dict[str, Any]]:
    """Async iterator for quotes with automatic pagination.

    This is the async equivalent of iter_quotes().

    Args:
        client: Optional explicit async client. If omitted, uses module-level async client.
        limit: Page size for each request (default: 100).
        **kwargs: Additional RequestParameters.

    Yields:
        dict: Individual quote records.

    Example:

        from britecore_sdk import AsyncBritecoreAPIClient
        from britecore_sdk.api.iterators import aiter_quotes

        async with AsyncBritecoreAPIClient("site").init_client() as client:
            async for quote in aiter_quotes(client=client):
                print(f"Quote: {quote['quoteNumber']}")
    """
    effective_client = aresolve_client(client)
    page = 1

    while True:
        # Import here to avoid circular dependency
        from britecore_sdk.api.api_calls.v2 import async_quotes

        response = await async_quotes.alist_quotes(
            page=page, limit=limit, client=effective_client, **kwargs
        )

        if not response or not response.get("data"):
            break

        for item in response["data"]:
            yield item

        # Check if we've reached the last page
        if len(response.get("data", [])) < limit:
            break

        page += 1


# ============================================================================
# POLICIES ITERATORS
# ============================================================================


def iter_policies(
    *,
    client: BritecoreAPIClient | None = None,
    limit: int = 100,
    **kwargs: Unpack[RequestParameters],
) -> Iterator[dict[str, Any]]:
    """Iterate over all policies with automatic pagination."""
    effective_client = resolve_client(client)
    page = 1

    while True:
        from britecore_sdk.api.api_calls.v2 import policies

        response = policies.list_policies(
            page=page, limit=limit, client=effective_client, **kwargs
        )

        if not response or not response.get("data"):
            break

        yield from response["data"]

        if len(response.get("data", [])) < limit:
            break

        page += 1


async def aiter_policies(
    *,
    client: AsyncBritecoreAPIClient | None = None,
    limit: int = 100,
    **kwargs: Unpack[RequestParameters],
) -> AsyncIterator[dict[str, Any]]:
    """Async iterator for policies with automatic pagination."""
    effective_client = aresolve_client(client)
    page = 1

    while True:
        from britecore_sdk.api.api_calls.v2 import async_policies

        response = await async_policies.alist_policies(
            page=page, limit=limit, client=effective_client, **kwargs
        )

        if not response or not response.get("data"):
            break

        for item in response["data"]:
            yield item

        if len(response.get("data", [])) < limit:
            break

        page += 1


# ============================================================================
# CONTACTS ITERATORS
# ============================================================================


def iter_contacts(
    *,
    client: BritecoreAPIClient | None = None,
    limit: int = 100,
    **kwargs: Unpack[RequestParameters],
) -> Iterator[dict[str, Any]]:
    """Iterate over all contacts with automatic pagination."""
    effective_client = resolve_client(client)
    page = 1

    while True:
        from britecore_sdk.api.api_calls.v2 import contacts

        response = contacts.list_contacts(
            page=page, limit=limit, client=effective_client, **kwargs
        )

        if not response or not response.get("data"):
            break

        yield from response["data"]

        if len(response.get("data", [])) < limit:
            break

        page += 1


async def aiter_contacts(
    *,
    client: AsyncBritecoreAPIClient | None = None,
    limit: int = 100,
    **kwargs: Unpack[RequestParameters],
) -> AsyncIterator[dict[str, Any]]:
    """Async iterator for contacts with automatic pagination."""
    effective_client = aresolve_client(client)
    page = 1

    while True:
        from britecore_sdk.api.api_calls.v2 import async_contacts

        response = await async_contacts.alist_contacts(
            page=page, limit=limit, client=effective_client, **kwargs
        )

        if not response or not response.get("data"):
            break

        for item in response["data"]:
            yield item

        if len(response.get("data", [])) < limit:
            break

        page += 1


__all__ = [
    "iter_quotes",
    "aiter_quotes",
    "iter_policies",
    "aiter_policies",
    "iter_contacts",
    "aiter_contacts",
]
