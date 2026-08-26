"""BriteCore v2 Reports API endpoint wrappers."""

import gzip
import json
from io import BytesIO
from typing import Any, Unpack
from zipfile import BadZipFile, ZipFile

from britecore_sdk.api.api_calls import (
    BritecoreAPIClient,
    RequestParameters,
    api_client,
)
from britecore_sdk.api.api_calls.v2._common import (
    build_payload as common_build_payload,
)
from britecore_sdk.exceptions import BritecoreError

API_CLIENT: BritecoreAPIClient = api_client


def _normalize_content_type(content_type: str | None) -> str:
    if not content_type:
        return ""
    return content_type.split(";", 1)[0].strip().lower()


def _looks_like_json(payload: bytes) -> bool:
    stripped = payload.lstrip()
    return stripped.startswith(b"{") or stripped.startswith(b"[")


def _extract_content_type(response: Any) -> str | None:
    headers = getattr(response, "headers", None)
    if headers is None:
        return None
    for header_name in ("content-type", "Content-Type", "CONTENT-TYPE"):
        header_value = headers.get(header_name)
        if header_value:
            return str(header_value)
    return None


def parse_report_file_content(
    file_content: bytes,
    content_type: str | None = None,
) -> Any:
    """Parse downloaded report bytes into JSON, ZIP members, or raw bytes.

    Returns parsed JSON for JSON payloads (including gzip/zip-compressed JSON),
    a ``dict[str, bytes]`` for ZIP archives with non-JSON payloads, or raw
    ``bytes`` when content is not parseable.
    """
    if not isinstance(file_content, bytes):
        raise TypeError("file_content must be bytes")

    normalized_content_type = _normalize_content_type(content_type)

    if normalized_content_type.endswith("json") or "+json" in normalized_content_type:
        return json.loads(file_content.decode("utf-8-sig"))

    is_gzip = normalized_content_type in {
        "application/gzip",
        "application/x-gzip",
        "gzip",
    } or file_content.startswith(b"\x1f\x8b")
    if is_gzip:
        try:
            decompressed = gzip.decompress(file_content)
            return parse_report_file_content(decompressed)
        except OSError:
            return file_content

    is_zip = normalized_content_type in {
        "application/zip",
        "application/x-zip-compressed",
    } or file_content.startswith((b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"))
    if is_zip:
        try:
            with ZipFile(BytesIO(file_content)) as archive:
                members = [
                    name for name in archive.namelist() if not name.endswith("/")
                ]
                if not members:
                    return {}
                if len(members) == 1:
                    member_name = members[0]
                    member_bytes = archive.read(member_name)
                    if member_name.lower().endswith(".json") or _looks_like_json(
                        member_bytes
                    ):
                        return parse_report_file_content(
                            member_bytes,
                            content_type="application/json",
                        )
                return {name: archive.read(name) for name in members}
        except (BadZipFile, OSError):
            return file_content

    if _looks_like_json(file_content):
        try:
            return json.loads(file_content.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            return file_content

    return file_content


def list_files(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """List files associated with a report.

    POST /api/v2/reports/list_files
    """
    request_json = common_build_payload(report_id=report_id)
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/list_files",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/list_files",
    )


def retrieve_reports(**kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve the available reports.

    POST /api/v2/reports/retrieve_reports
    """
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/retrieve_reports",
        json={},
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/retrieve_reports",
    )


def retrieve_report(report_id: str, **kwargs: Unpack[RequestParameters]) -> Any:
    """Retrieve a report by identifier.

    POST /api/v2/reports/retrieve_report
    """
    request_json = common_build_payload(report_id=report_id)
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/retrieve_report",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/retrieve_report",
    )


def fetch_prepared_yml(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve prepared YML content for report processing."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/fetch_prepared_yml",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/fetch_prepared_yml",
    )


def delete_report(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a report definition."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/delete_report",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/delete_report",
    )


def rename_report_category(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Rename an existing report category."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/rename_report_category",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/rename_report_category",
    )


def data_frame_preview(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Preview a report data frame."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/data_frame_preview",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/data_frame_preview",
    )


def upload_file(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Upload a file used by report processing."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/upload_file",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/upload_file",
    )


def list_df_caches(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List available dataframe cache entries."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/list_df_caches",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/list_df_caches",
    )


def create_report_category(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Create a new report category."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/create_report_category",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/create_report_category",
    )


def delete_report_category(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete an existing report category."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/delete_report_category",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/delete_report_category",
    )


def delete_file(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Delete a report-related file."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/delete_file",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/delete_file",
    )


def get_s3_token(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Retrieve an S3 upload token for report files."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/get_s3_token",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/get_s3_token",
    )


def list_df_cache_files(
    payload: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """List files attached to a dataframe cache record."""
    request_json = payload or {}
    request_result = API_CLIENT.do_request(
        path="/api/v2/reports/list_df_cache_files",
        json=request_json,
        method="POST",
        **kwargs,
    )
    return API_CLIENT.process_result(
        request_result,
        endpoint="/api/v2/reports/list_df_cache_files",
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
    """Check Report Process Status.

    POST /api/v2/reports/check_report_process_status
    """
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
    """Download Report File.

    POST /api/v2/reports/download_report_file
    """
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
    if request_result is None:
        raise BritecoreError.NoDataReturned(
            "Error - No response",
            endpoint="/api/v2/reports/download_report_file",
        )

    API_CLIENT._raise_for_http_status(
        request_result,
        endpoint="/api/v2/reports/download_report_file",
        client=API_CLIENT,
        request_id=(getattr(request_result, "headers", {}) or {}).get(
            "X-SDK-Request-ID"
        ),
        sanitized_body=filtered_json,
    )

    raw_bytes = bytes(getattr(request_result, "data", b"") or b"")
    return parse_report_file_content(
        raw_bytes,
        content_type=_extract_content_type(request_result),
    )


def download_report_file_decoded(
    file_id: str | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Download and auto-decode report content (JSON, gzip, zip, or raw bytes).

    This bypasses ``process_result(...)`` so binary response bodies are handled
    safely. Use this helper when the endpoint returns file content directly.
    """
    return download_report_file(file_id=file_id, **kwargs)


def generate_consolidated_declaration(
    policy_group: Any | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Generate Consolidated Declaration.

    POST /api/v2/reports/generate_consolidated_declaration
    """
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
    """Retrieve Report Categories.

    POST /api/v2/reports/retrieve_report_categories
    """
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
    """Retrieve Sql Reports.

    POST /api/v2/reports/retrieve_sql_reports
    """
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
    parameters: dict[str, Any] | None = None,
    **kwargs: Unpack[RequestParameters],
) -> Any:
    """Run Report.

    POST /api/v2/reports/run_report
    """
    request_json: dict[str, Any] = {
        "additional_report_configuration": additional_report_configuration,
        "start_date": start_date,
        "end_date": end_date,
        "report_name": report_name,
        "parameters": parameters,
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
    """Save Report.

    POST /api/v2/reports/save_report
    """
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
        "download_report_file_decoded",
        "generate_consolidated_declaration",
        "parse_report_file_content",
        "retrieve_report_categories",
        "retrieve_sql_reports",
        "run_report",
        "save_report",
    ]
)
