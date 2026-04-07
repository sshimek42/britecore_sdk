"""BriteCore v2 Quotes API endpoint wrappers.

These wrappers cover quote creation and retrieval workflows exposed by the SDK's
current v2 quote surface. The quote paths remain known spec-gap wrappers, so the
docstrings describe the intended API contract first and call out SDK-specific
response normalization where needed.
"""

from logging import Logger
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def create_full_quote(
    quote_json: dict[str, Any], **kwargs: Unpack[RequestParameters]
) -> tuple[dict[str, Any] | None, str | None]:
    """Create a quote from the supplied quote payload.

    This wrapper submits ``quote_json`` to ``/api/v2/quotes/create_full_quote``
    and normalizes the response through ``process_result(...)``. As an SDK-
    specific convenience, it returns a tuple of ``(quote_data, quote_id)``,
    where ``quote_id`` is extracted from the normalized payload when present.
    ``**kwargs`` accepts ``RequestParameters`` overrides such as timeout,
    headers, or retry settings.
    """
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/quotes/create_full_quote", json=quote_json, **kwargs
    )

    json_info: Any = API_CLIENT.process_result(request_result)

    if not json_info:
        return None, None

    return json_info, json_info["id"]


def get_quote(id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a quote by quote identifier.

    This wrapper sends ``id`` to ``/api/v2/quotes/get_quote`` and returns the
    normalized ``process_result(...)`` payload for the requested quote.
    ``**kwargs`` accepts ``RequestParameters`` overrides such as timeout,
    headers, or retry settings.
    """
    quote_json: dict[str, str] = {"id": id}

    LOGGER.debug("Getting quote")

    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path="/api/v2/quotes/get_quote", json=quote_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)


__all__ = ["create_full_quote", "get_quote"]
