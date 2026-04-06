"""BriteCore v2 Data API endpoint wrappers.

Provides:
    export_data_as_csv        -- Export data as a CSV file.
    get_available_dashboards  -- Retrieve the list of available dashboards.
"""

from logging import Logger
from typing import Any, Unpack, cast

from urllib3 import BaseHTTPResponse, HTTPResponse

from britecore_libraries import logger
from britecore_libraries.api.api_calls import (
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
    """Export data as a CSV file.

    Parameters
    ----------
    as_of_date : str, optional
        As-of date for the export in ``YYYY-MM-DD`` format.
    end_date : str, optional
        End date of the export range in ``YYYY-MM-DD`` format.
    nonprep_dfs : str, optional
        Non-prepared data frames to include.
    prep_dfs : str, optional
        Prepared data frames to include.
    start_date : str, optional
        Start date of the export range in ``YYYY-MM-DD`` format.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing the CSV export data.
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
    """Retrieve the list of dashboards available for a module.

    Parameters
    ----------
    module : str, optional
        Module name to filter available dashboards by.
    **kwargs : Unpack[RequestParameters]
        Optional timeout / retry / header overrides.

    Returns
    -------
    Any
        Processed API response containing available dashboard definitions.
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
