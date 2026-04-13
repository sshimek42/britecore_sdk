"""BriteCore v2 Data API endpoint wrappers.

This module provides wrappers for data export and dashboard-discovery endpoints
in the BriteCore v2 data API.
"""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import RequestParameters
from britecore_sdk.api.api_calls.v2._common import build_payload, post


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
    return post(
        "/api/v2/data/export_data_as_csv",
        build_payload(
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
    return post(
        "/api/v2/data/get_available_dashboards",
        build_payload(module=module),
        **kwargs,
    )


__all__ = [
    "export_data_as_csv",
    "get_available_dashboards",
]
