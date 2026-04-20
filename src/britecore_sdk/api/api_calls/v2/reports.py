"""BriteCore v2 Reports API endpoint wrappers."""

from typing import Any, Unpack

from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.api.api_calls.v2._common import (
    build_payload as common_build_payload,
)
from britecore_sdk.api.api_calls.v2._common import (
    post as common_post,
)

API_CLIENT: BritecoreAPIClient = api_client


def _post(
    path: str,
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    return common_post(path, payload, client=API_CLIENT, **kwargs)


def list_files(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """List files associated with a report.

    This wrapper sends ``report_id`` to ``/api/v2/reports/list_files`` and
    returns the normalized ``process_result(...)`` payload for the matching
    report files. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/reports/list_files",
        common_build_payload(report_id=report_id),
        **kwargs,
    )


def retrieve_reports(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the available reports.

    This wrapper calls ``/api/v2/reports/retrieve_reports`` and returns the
    normalized ``process_result(...)`` payload for the report list.
    ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post("/api/v2/reports/retrieve_reports", **kwargs)


def retrieve_report(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a report by identifier.

    This wrapper sends ``report_id`` to ``/api/v2/reports/retrieve_report`` and
    returns the normalized ``process_result(...)`` payload for the matching
    report. ``**kwargs`` accepts ``RequestParameters`` overrides.
    """
    return _post(
        "/api/v2/reports/retrieve_report",
        common_build_payload(report_id=report_id),
        **kwargs,
    )


def fetch_prepared_yml(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve prepared YML content for report processing."""
    return _post(
        "/api/v2/reports/fetch_prepared_yml",
        payload,
        **kwargs,
    )


def delete_report(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a report definition."""
    return _post("/api/v2/reports/delete_report", payload, **kwargs)


def rename_report_category(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Rename an existing report category."""
    return _post(
        "/api/v2/reports/rename_report_category",
        payload,
        **kwargs,
    )


def data_frame_preview(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Preview a report data frame."""
    return _post(
        "/api/v2/reports/data_frame_preview",
        payload,
        **kwargs,
    )


def upload_file(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a file used by report processing."""
    return _post("/api/v2/reports/upload_file", payload, **kwargs)


def list_df_caches(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List available dataframe cache entries."""
    return _post(
        "/api/v2/reports/list_df_caches",
        payload,
        **kwargs,
    )


def create_report_category(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a new report category."""
    return _post(
        "/api/v2/reports/create_report_category",
        payload,
        **kwargs,
    )


def delete_report_category(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete an existing report category."""
    return _post(
        "/api/v2/reports/delete_report_category",
        payload,
        **kwargs,
    )


def delete_file(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a report-related file."""
    return _post("/api/v2/reports/delete_file", payload, **kwargs)


def get_s3_token(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve an S3 upload token for report files."""
    return _post("/api/v2/reports/get_s3_token", payload, **kwargs)


def list_df_cache_files(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List files attached to a dataframe cache record."""
    return _post(
        "/api/v2/reports/list_df_cache_files",
        payload,
        **kwargs,
    )


__all__ = [
    "create_report_category",
    "data_frame_preview",
    "delete_file",
    "delete_report",
    "delete_report_category",
    "fetch_prepared_yml",
    "get_s3_token",
    "list_df_cache_files",
    "list_df_caches",
    "list_files",
    "rename_report_category",
    "retrieve_report",
    "retrieve_reports",
    "upload_file",
]
