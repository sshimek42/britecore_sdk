from logging import Logger
from typing import Any, Unpack, Optional

from britecore_libraries.api.api_calls import (api_client, RequestParameters,
                                               BritecoreAPIClient)
from britecore_libraries import logger

from urllib3 import BaseHTTPResponse, HTTPResponse

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def create_full_quote(quote_json: dict[str,Any], **kwargs: Unpack[
    RequestParameters]) -> tuple[dict[str,
Any] | None, str | None]:
    """
    Create new quote
    :param quote_json: Full quote JSON
    :type quote_json: dict[str,Any]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Quote JSON and quote UUID
    :rtype: tuple[dict[str,Any] | None, str | None]
    """
    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/quotes/create_full_quote", json=quote_json, **kwargs
    )

    json_info: Any = API_CLIENT.process_result(request_result)

    if not json_info:
        return None, None

    return json_info, json_info["id"]


def get_quote(id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieves a quote
    :param id: Quote UUID
    :type id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Quote information in JSON format
    :rtype: Any
    """
    quote_json: dict[str,str] = {"id": id}

    LOGGER.debug("Getting quote")

    request_result: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        path="/api/v2/quotes/get_quote", json=quote_json, **kwargs
    )

    return API_CLIENT.process_result(request_result)
