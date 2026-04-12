"""BriteCore v2 Data API endpoint wrappers.

This module provides wrappers for data export and dashboard-discovery endpoints
in the BriteCore v2 data API.
"""

from logging import Logger
from typing import Any, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_sdk import logger
from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)

LOGGER: Logger = logger

API_CLIENT: BritecoreAPIClient = api_client


def _build_payload(**fields: Any) -> dict[str, Any]:
    """Build a JSON payload, omitting keys whose value is ``None``."""
    return {key: value for key, value in fields.items() if value is not None}


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Send a data request and normalize the response."""
    LOGGER.debug("Calling data endpoint %s", path)
    request_result: BaseHTTPResponse | HTTPResponse | None = API_CLIENT.do_request(
        path=path,
        json=payload if payload is not None else {},
        **kwargs,
    )
    return API_CLIENT.process_result(cast(Any, request_result))


def export_data_as_csv(
    as_of_date: str | None = None,
    end_date: str | None = None,
    nonprep_dfs: str | None = None,
    prep_dfs: str | None = None,
    start_date: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Export CSV data for the requested date range and data sets.

    This wrapper sends the supplied date filters and prepared/non-prepared data
    frame selections to ``/api/v2/data/export_data_as_csv`` and returns the
    normalized ``process_result(...)`` payload for the export request.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/data/export_data_as_csv",
        _build_payload(
            as_of_date=as_of_date,
            end_date=end_date,
            nonprep_dfs=nonprep_dfs,
            prep_dfs=prep_dfs,
            start_date=start_date,
        ),
        **kwargs,
    )


def get_available_dashboards(
    module: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve dashboards available for a module.

    This wrapper sends the optional ``module`` filter to
    ``/api/v2/data/get_available_dashboards`` and returns the normalized
    ``process_result(...)`` payload describing the available dashboard
    definitions. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/data/get_available_dashboards",
        _build_payload(module=module),
        **kwargs,
    )


__all__ = [
    "export_data_as_csv",
    "get_available_dashboards",
]
