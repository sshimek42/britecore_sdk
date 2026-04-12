"""BriteCore v2 Reports API endpoint wrappers.

This module provides wrappers for report listing, report retrieval, and
report-file lookups in the BriteCore v2 reports API.
"""

from typing import Any, Unpack

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

API_CLIENT: BritecoreAPIClient = api_client


def list_files(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """List files associated with a report.

    This wrapper sends ``report_id`` to ``/api/v2/reports/list_files`` and
    returns the normalized ``process_result(...)`` payload for the matching
    report files. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    list_json: dict[str, str] = {"report_id": report_id}

    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v2/reports/list_files",
        json=list_json,
        **kwargs,
    )

    return API_CLIENT.process_result(result_request)


def retrieve_reports(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the available reports.

    This wrapper calls ``/api/v2/reports/retrieve_reports`` and returns the
    normalized ``process_result(...)`` payload for the report list.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    required_json = None

    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v2/reports/retrieve_reports", json=required_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)


def retrieve_report(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a report by identifier.

    This wrapper sends ``report_id`` to ``/api/v2/reports/retrieve_report`` and
    returns the normalized ``process_result(...)`` payload for the matching
    report. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    report_json: dict[str, str] = {"report_id": report_id}

    result_request: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        "/api/v2/reports/retrieve_report", json=report_json, **kwargs
    )

    return API_CLIENT.process_result(result_request)
