"""Shared helper utilities for v2 endpoint wrappers."""

from typing import Any, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)


def build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload while omitting ``None`` values."""
    return {key: value for key, value in fields.items() if value is not None}


def post(
    path: str,
    payload: dict[str, Any] | None = None,
    *,
    include_endpoint: bool = False,
    client: BritecoreAPIClient = api_client,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a request and return normalized data via ``process_result(...)``."""
    request_result: BaseHTTPResponse | HTTPResponse | None = client.do_request(
        path=path,
        json=payload or {},
        **kwargs,
    )
    if include_endpoint:
        return client.process_result(cast(Any, request_result), endpoint=path)
    return client.process_result(cast(Any, request_result))

