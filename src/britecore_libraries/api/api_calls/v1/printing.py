from json import loads
from logging import Logger
from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse, Retry, Timeout

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger
API_CLIENT: BritecoreAPIClient = api_client


def get_to_be_printed(
    from_date: str,
    to_date: str,
    ignore_state: bool | None = True,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """
    Retrieve a list of files that are pending to be printed within a specified date range.

    This function fetches the list of files scheduled for printing between the given
    from_date and to_date. It allows optional filtering based on state and supports
    additional request parameters.

    Parameters:
        from_date: The start date for filtering files to be printed, formatted as string. (YYYY-MM-DD)
        to_date: The end date for filtering files to be printed, formatted as string. (YYYY-MM-DD)
        ignore_state: If True, includes files regardless of their printing state.
                      Defaults to True.
        **kwargs: Additional keyword arguments passed to the API request, including
                  request_timeout and request_retries.

    Returns:
        The parsed response data containing the list of files to be printed, or None
        if the request fails or returns no data.
    """

    # default parameters
    request_timeout = Timeout(120)
    request_retries = Retry(total=3, status_forcelist=[502, 503, 504])

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

    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v1/printing/getToBePrinted",
        json=required_json,
        **kwargs,
    )

    return_data: Any | None = None
    if result_request:
        return_data = loads(result_request.data.decode("utf-8"))

    return return_data


def mark_as_printed(file_ids: list[str], **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Mark specified files as printed in the system.

    This function sends a request to mark the given file IDs as printed. It constructs
    a JSON payload with the file IDs and sends it to the printing endpoint. The function
    logs the IDs being marked and processes the API response.

    Parameters:
        file_ids: List of file identifiers to mark as printed
        **kwargs: Additional request parameters that will be passed to the API client

    Returns:
        The processed result from the API request, which may contain the response
        data or status information depending on the API client implementation

    Raises:
        Any exceptions that may occur during the HTTP request or response processing
        by the underlying API client
    """

    required_json: dict[str, list] = {"file_ids": file_ids}

    LOGGER.debug(f"Marking IDs\n{file_ids}")

    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v1/printing/markAsPrinted",
        json=required_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)
