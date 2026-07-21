"""Helper utilities for working with API responses.

Provides common patterns for data extraction, pagination, and batch operations.
"""

from collections.abc import Callable, Generator
from typing import Any, TypeVar

from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.exceptions import BritecoreError

T = TypeVar("T")


def extract_data(response: Any) -> Any:
    """Extract 'data' field from a response, raising if missing.

    Most BriteCore API responses follow the pattern:
    ```json
    {
        "success": true,
        "data": { ... actual data ... }
    }
    ```

    This helper extracts the data field or raises an informative error.

    Args:
        response: API response (typically dict).

    Returns:
        The 'data' field contents.

    Raises:
        BritecoreError.NoDataReturned: If 'data' field is missing or None.

    Example::

        from britecore_sdk.api.response_helpers import extract_data
        from britecore_sdk.api.api_calls.v2 import policies

        response = policies.retrieve_policy(policy_number="POL-123")
        policy_data = extract_data(response)
    """
    if (
        isinstance(response, dict)
        and "data" in response
        and response["data"] is not None
    ):
        return response["data"]

    if isinstance(response, dict) and "data" in response:
        raise BritecoreError.NoDataReturned(
            "API returned success but 'data' field is null"
        )

    raise BritecoreError.NoDataReturned(
        f"API response missing 'data' field. Response: {response}"
    )


def is_successful_response(response: Any) -> bool:
    """Check if an API response indicates success.

    Args:
        response: API response (typically dict).

    Returns:
        True if response indicates success, False otherwise.

    Example::

        from britecore_sdk.api.response_helpers import is_successful_response

        response = client.do_request(...)
        if is_successful_response(response):
            data = response.get("data")
    """
    if isinstance(response, dict):
        return response.get("success", False) is True
    return False


def get_message(response: Any) -> str | None:
    """Extract error/info message from response.

    BriteCore API responses may include messages via 'message' or 'messages' fields.
    This helper tries both fields.

    Args:
        response: API response (typically dict).

    Returns:
        Message string if found, None otherwise.

    Example::

        from britecore_sdk.api.response_helpers import get_message

        response = client.do_request(...)
        msg = get_message(response)
        if msg:
            print(f"API message: {msg}")
    """
    if isinstance(response, dict):
        # Try singular 'message' first
        if "message" in response and response["message"]:
            return response["message"]
        # Try plural 'messages' (usually a list)
        if "messages" in response and response["messages"]:
            messages = response["messages"]
            if isinstance(messages, list) and messages:
                return "; ".join(str(m) for m in messages)
            elif isinstance(messages, str):
                return messages
    return None


def paginate(
    client: BritecoreAPIClient,
    endpoint_callable: Callable[..., Any],
    page_size: int = 50,
    max_pages: int | None = None,
    **endpoint_kwargs: Any,
) -> Generator[Any, None, None]:
    """Iterate through paginated API responses.

    Many BriteCore endpoints support pagination via 'page' and 'page_size' parameters.
    This helper automatically iterates through pages and yields individual items.

    Args:
        client: The API client instance.
        endpoint_callable: Endpoint wrapper function to call (e.g., list_policies).
        page_size: Items per page (default 50).
        max_pages: Maximum number of pages to fetch (None = no limit).
        **endpoint_kwargs: Keyword arguments for the endpoint.

    Yields:
        Individual items from all pages combined.

    Example::

        from britecore_sdk.api.response_helpers import paginate
        from britecore_sdk.api.api_calls import get_api_client
        from britecore_sdk.api.api_calls.v2 import contacts

        client = get_api_client()
        for contact in paginate(
            client,
            contacts.list_contacts,
            page_size=100,
            max_pages=5
        ):
            print(contact)
    """
    page = 1
    pages_fetched = 0

    while max_pages is None or pages_fetched < max_pages:
        response = endpoint_callable(
            page=page,
            page_size=page_size,
            **endpoint_kwargs,
        )

        # Extract data
        try:
            data = extract_data(response)
        except BritecoreError.Base:
            # No more data available
            break

        # Handle data (could be list or dict)
        if isinstance(data, list):
            yield from data

            # Check if we got fewer items than requested (last page)
            if len(data) < page_size:
                break
        elif isinstance(data, dict):
            # Single item response
            yield data
            break
        else:
            break

        page += 1
        pages_fetched += 1


def batch_items(
    items: list[T],
    batch_size: int,
) -> Generator[list[T], None, None]:
    """Yield items in batches.

    Useful for breaking up large lists into chunks for batch API operations.

    Args:
        items: Items to batch.
        batch_size: Number of items per batch.

    Yields:
        Lists of items, each with up to batch_size items.

    Example::

        from britecore_sdk.api.response_helpers import batch_items

        large_list = list(range(1000))
        for batch in batch_items(large_list, batch_size=100):
            print(f"Processing batch of {len(batch)} items")
    """
    for i in range(0, len(items), batch_size):
        yield items[i : i + batch_size]


def transform_response(response: Any, transform: Callable[[Any], T]) -> T:
    """Apply a transformation function to extracted response data.

    Convenience function to extract data and immediately transform it.

    Args:
        response: API response.
        transform: Function to apply to extracted data.

    Returns:
        Result of transform function.

    Example::

        from britecore_sdk.api.response_helpers import transform_response

        response = retrieve_policy(...)
        policy_number = transform_response(response, lambda d: d.get("policy_number"))
    """
    data = extract_data(response)
    return transform(data)


__all__ = [
    "extract_data",
    "is_successful_response",
    "get_message",
    "paginate",
    "batch_items",
    "transform_response",
]
