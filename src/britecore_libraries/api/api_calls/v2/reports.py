from typing import Unpack, Any, Optional

from britecore_libraries.api.api_calls import api_client, BritecoreAPIClient, RequestParameters
from urllib3 import BaseHTTPResponse, HTTPResponse

API_CLIENT: BritecoreAPIClient = api_client


def list_files(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Get list of files associated with report
    :param report_id: UUID of the report associated with the file
    :type report_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Files related to report
    :rtype: Any
    """
    list_json: dict[str,str] = {"report_id": report_id}

    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v2/reports/list_files",
        json=list_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)


def retrieve_reports(**kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieves all available Reports, grouped in their Report Categories
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Reports
    :rtype: Any
    """
    required_json = None

    result_request: Optional[BaseHTTPResponse | HTTPResponse]  = API_CLIENT.do_request(
        "/api/v2/reports/retrieve_reports", json=required_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def retrieve_report(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """
    Retrieves a single report's full definition
    :param report_id: Report UUID
    :type report_id: str
    :param kwargs: Keywords to pass to urllib3 request
    :type kwargs: dict[str,Any]
    :return: Report definition
    :rtype: Any
    """
    report_json: dict[str,str] = {"report_id": report_id}

    result_request: Optional[BaseHTTPResponse | HTTPResponse] = API_CLIENT.do_request(
        "/api/v2/reports/retrieve_report", json=report_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)
