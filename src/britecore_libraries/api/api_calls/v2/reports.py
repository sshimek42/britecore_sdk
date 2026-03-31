"""BriteCore v2 Reports API endpoint wrappers.

Provides:
    list_files       -- List files associated with a report ID.
    retrieve_reports -- Retrieve all available reports.
    retrieve_report  -- Retrieve a single report by ID.
"""
from typing import Any, Optional, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

API_CLIENT: BritecoreAPIClient = api_client


def list_files(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve a list of files associated with a specific report.

    This function fetches the list of files linked to a given report ID by making a
    request to the API endpoint for report files.

    Parameters
    ----------
    report_id : str
        The unique identifier of the report for which to retrieve file list.
    **kwargs : Unpack[RequestParameters]
        Additional keyword arguments to pass to the API request.

    Returns
    -------
    Any
        The result of processing the API response, typically containing the list
        of files associated with the report.

    Raises
    ------
    Any exceptions raised by the underlying API client or request processing
    mechanism are propagated as-is.
    """
    list_json: dict[str, str] = {"report_id": report_id}

    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v2/reports/list_files",
        json=list_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)


def retrieve_reports(**kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve reports from the API endpoint.

    This function sends a request to the API to retrieve reports. It uses the
    API client to perform the HTTP request and processes the result.

    Parameters
    ----------
    **kwargs : Unpack[RequestParameters]
        Additional keyword arguments to pass to the API client's do_request method.
        These parameters are unpacked from a RequestParameters type.

    Returns
    -------
    Any
        The processed result from the API request, which can be of any type
        depending on the response data structure.

    Raises
    ------
    Any exceptions raised by the underlying API client or HTTP request
    mechanism are propagated as-is.

    Notes
    -----
    - The function internally uses API_CLIENT.do_request to perform the actual
      HTTP request to the "/api/v2/reports/retrieve_reports" endpoint.
    - The required_json parameter is set to None, indicating no JSON payload
      is sent with the request.
    - The result from the request is processed using API_CLIENT.process_result
      before being returned.
    """
    required_json = None

    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v2/reports/retrieve_reports", json=required_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def retrieve_report(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieve a report by its ID from the API.

    This function fetches a report from the API using the provided report ID. It constructs
    a request with the report ID and sends it to the API endpoint for report retrieval.

    Parameters
    ----------
    report_id : str
        The unique identifier of the report to retrieve
    **kwargs : Unpack[RequestParameters]
        Additional keyword arguments to pass to the API request

    Returns
    -------
    Any
        The result of the API request processing, typically the report data

    Raises
    ------
    Any exceptions raised by the underlying API client or request processing
    """
    report_json: dict[str, str] = {"report_id": report_id}

    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v2/reports/retrieve_report", json=report_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)
