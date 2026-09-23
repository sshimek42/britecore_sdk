"""Helper utilities for working with API responses.

Provides common patterns for data extraction, pagination, and batch operations.
"""

from collections.abc import Callable, Generator
from typing import Any, TypeVar

from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.exceptions import BritecoreError

T = TypeVar("T")


def _coerce_int(value: Any) -> int | None:
    """Best-effort integer conversion used for metadata normalization."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return None
    return None


def _first_present_key(mapping: dict[str, Any], keys: tuple[str, ...]) -> Any:
    """Return the first non-None key value from a mapping."""
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return None


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


def extract_items(response: Any) -> list[Any]:
    """Extract list-like payloads from common response envelope shapes.

    This accepts canonical ``{"data": [...]}``, nested list containers such as
    ``{"data": {"items": [...]}}``, and top-level ``{"items": [...]}`` fallback
    payloads used by some list endpoints.
    """
    if isinstance(response, dict):
        top_level_items = _first_present_key(response, ("items", "results"))
        if isinstance(top_level_items, list):
            return top_level_items

    try:
        data = extract_data(response)
    except BritecoreError.NoDataReturned:
        return []

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        nested_items = _first_present_key(data, ("items", "results", "data"))
        if isinstance(nested_items, list):
            return nested_items
        return [data]
    return []


def normalize_pagination_envelope(response: Any) -> dict[str, Any]:
    """Normalize paginated response shapes into one stable metadata envelope."""
    items = extract_items(response)
    base: dict[str, Any] = response if isinstance(response, dict) else {}
    data = base.get("data")
    container = data if isinstance(data, dict) else base

    total_count = _coerce_int(
        _first_present_key(container, ("totalCount", "total_count", "total", "count"))
    )
    if total_count is None:
        total_count = len(items)

    page = _coerce_int(
        _first_present_key(container, ("page", "pageNumber", "page_number"))
    )
    if page is None:
        page = 1

    page_size = _coerce_int(
        _first_present_key(container, ("pageSize", "page_size", "per_page", "limit"))
    )
    if page_size is None:
        page_size = len(items)

    explicit_last = _first_present_key(container, ("isLastPage", "is_last_page"))
    if isinstance(explicit_last, bool):
        is_last_page = explicit_last
    elif page_size <= 0:
        is_last_page = True
    else:
        is_last_page = len(items) < page_size

    next_page = _coerce_int(_first_present_key(container, ("nextPage", "next_page")))
    if next_page is None and not is_last_page:
        next_page = page + 1

    return {
        "items": items,
        "total_count": total_count,
        "page": page,
        "page_size": page_size,
        "is_last_page": is_last_page,
        "next_page": next_page,
    }


def normalize_batch_results(response: Any) -> dict[str, Any]:
    """Normalize batch workflow output to canonical ``id``/``data`` result keys."""
    payload = response if isinstance(response, dict) else {}
    raw_results = payload.get("results")
    if not isinstance(raw_results, list):
        raw_results = extract_items(response)

    normalized_results: list[dict[str, Any]] = []
    for idx, item in enumerate(raw_results):
        if not isinstance(item, dict):
            normalized_results.append(
                {
                    "index": idx,
                    "success": False,
                    "id": None,
                    "data": None,
                    "error": "Unexpected non-dict batch item",
                    "error_type": type(item).__name__,
                }
            )
            continue

        normalized_id = _first_present_key(
            item,
            ("id", "quote_id", "contact_id", "policy_id", "revision_id"),
        )
        normalized_data = _first_present_key(
            item,
            ("data", "quote_data", "contact_data", "policy_data"),
        )
        success = item.get("success")
        if not isinstance(success, bool):
            success = item.get("error") in (None, "")

        parsed_index = _coerce_int(item.get("index"))
        normalized_results.append(
            {
                "index": idx if parsed_index is None else parsed_index,
                "success": success,
                "id": normalized_id,
                "data": normalized_data,
                "error": item.get("error"),
                "error_type": _first_present_key(item, ("error_type", "errorType")),
            }
        )

    computed_succeeded = sum(1 for result in normalized_results if result["success"])
    total = _coerce_int(payload.get("total"))
    if total is None:
        total = len(normalized_results)
    total = max(total, len(normalized_results))

    failed = _coerce_int(payload.get("failed"))
    if failed is None:
        failed = total - computed_succeeded

    succeeded = _coerce_int(payload.get("succeeded"))
    if succeeded is None:
        succeeded = total - failed

    return {
        "total": total,
        "succeeded": succeeded,
        "failed": failed,
        "results": normalized_results,
    }


def paginate(
    _client: BritecoreAPIClient,
    endpoint_callable: Callable[..., Any],
    page_size: int = 50,
    max_pages: int | None = None,
    **endpoint_kwargs: Any,
) -> Generator[Any, None, None]:
    """Iterate through paginated API responses.

    Many BriteCore endpoints support pagination via 'page' and 'page_size' parameters.
    This helper automatically iterates through pages and yields individual items.

    Args:
        _client: The API client instance (kept for backward-compatible call shape).
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
    "extract_items",
    "is_successful_response",
    "get_message",
    "paginate",
    "batch_items",
    "transform_response",
    "normalize_pagination_envelope",
    "normalize_batch_results",
]
