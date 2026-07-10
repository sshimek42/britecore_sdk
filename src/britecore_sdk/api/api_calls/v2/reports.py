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

# --- Autogenerated spec wrappers ---


def check_report_process_status(
    report_process_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/reports/check_report_process_status``."""
    request_json: dict[str, Any] = {
        "report_process_id": report_process_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/check_report_process_status",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/reports/check_report_process_status"
    )


def download_report_file(
    file_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/reports/download_report_file``."""
    request_json: dict[str, Any] = {
        "file_id": file_id,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/download_report_file",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/reports/download_report_file"
    )


def generate_consolidated_declaration(
    policy_group: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/reports/generate_consolidated_declaration``."""
    request_json: dict[str, Any] = {
        "policy_group": policy_group,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/generate_consolidated_declaration",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/reports/generate_consolidated_declaration"
    )


def retrieve_report_categories(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/reports/retrieve_report_categories``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/retrieve_report_categories",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/reports/retrieve_report_categories"
    )


def retrieve_sql_reports(
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/reports/retrieve_sql_reports``."""
    request_json: dict[str, Any] = {}
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/retrieve_sql_reports",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/reports/retrieve_sql_reports"
    )


def run_report(
    additional_report_configuration: dict[str, Any] | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    report_name: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/reports/run_report``."""
    request_json: dict[str, Any] = {
        "additional_report_configuration": additional_report_configuration,
        "start_date": start_date,
        "end_date": end_date,
        "report_name": report_name,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/run_report",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/reports/run_report"
    )


def save_report(
    report_data: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Autogenerated wrapper for ``POST /api/v2/reports/save_report``."""
    request_json: dict[str, Any] = {
        "report_data": report_data,
    }
    filtered_json = {k: v for k, v in request_json.items() if v is not None}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/save_report",
        json=filtered_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result, endpoint="/api/v2/reports/save_report"
    )


__all__.extend(
    [
        "check_report_process_status",
        "download_report_file",
        "generate_consolidated_declaration",
        "retrieve_report_categories",
        "retrieve_sql_reports",
        "run_report",
        "save_report",
    ]
)
