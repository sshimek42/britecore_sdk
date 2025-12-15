from json import loads
from logging import Logger
from typing import Any, Optional, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse, Timeout, Retry

from britecore_libraries.api.api_calls import BritecoreAPIClient, api_client, RequestParameters
from britecore_libraries import logger

LOGGER:Logger = logger
API_CLIENT: BritecoreAPIClient = api_client


def get_to_be_printed(
    from_date: str,
    to_date: str,
    ignore_state: Optional[bool] = True,
    **kwargs: Unpack[RequestParameters]
) -> Any:
    """
    Get File IDs to be printed
    :param from_date: Start Date (yyyy-mm-dd)
    :type from_date: str
    :param to_date: End Date (yyyy-mm-dd)
    :type to_date: str
    :param ignore_state: Ignore printed state (Default: True)
    :type ignore_state: Optional[bool]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: List of document IDs
    :rtype: Any
    """

    # default parameters
    request_timeout = Timeout(120)
    request_retries = Retry(total=3, status_forcelist=[502,503,504])

    if not kwargs.get("request_timeout"):
        kwargs.update({"request_timeout": request_timeout})

    if not kwargs.get("request_retries"):
        kwargs.update({"request_retries": request_retries})

    required_json: dict[str, dict[str, Any]] = {
        "json_dict": {
            "from_date": from_date,
            "to_date": to_date,
            "ignore_state": ignore_state,
        }
    }

    LOGGER.debug("Getting files to be printed")

    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v1/printing/getToBePrinted",
        json=required_json,
        **kwargs,
    )

    return_data: Optional[Any] = None
    if result_request:
        return_data = loads(result_request.data.decode("utf-8"))

    return return_data


def mark_as_printed(file_ids: list[str], **kwargs:Unpack[RequestParameters]) -> Any:
    """
    Mark files as printed
    :param file_ids: File IDs to mark as printed
    :type file_ids: list[str]
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: Optional[dict[str,Any]]
    :return: Marking results
    :rtype: Any
    """

    required_json: dict[str, list] = {"file_ids": file_ids}

    LOGGER.debug(f"Marking IDs\n%f.yellow%{file_ids}%f%")

    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v1/printing/markAsPrinted",
        json=required_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)
