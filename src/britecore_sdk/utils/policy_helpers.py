"""Utility functions for policy retrieval and related helpers."""

from json import loads
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk.api.api_calls import RequestParameters, api_client


def get_policies(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve policies using the v2 API endpoint.

    Calls /api/v2/policies/get_policies and returns the parsed JSON payload data.

    Parameters:
        **kwargs: Additional request parameters for the API client. These may
            include filters, pagination, or other API-supported options. See
            ``interactive_menu.policy_menu`` for example usage and expected
            parameters.
    """
    request_result: BaseHTTPResponse | HTTPResponse | None = api_client.do_request(
        path="/api/v2/policies/get_policies",
        **kwargs,
    )
    if request_result is None or not hasattr(request_result, "data"):
        raise RuntimeError("No response from get_policies API")
    return loads(request_result.data.decode("utf-8"))
