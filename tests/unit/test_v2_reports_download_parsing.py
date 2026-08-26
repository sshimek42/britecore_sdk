"""Unit tests for report download content decoding helpers."""

import gzip
import json
from io import BytesIO
from unittest.mock import MagicMock, patch
from zipfile import ZipFile

import pytest

from britecore_sdk.api.api_calls.v2 import reports
from britecore_sdk.exceptions import BritecoreError


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        for name, payload in files.items():
            archive.writestr(name, payload)
    return buffer.getvalue()


@pytest.mark.unit
def test_parse_report_file_content_json_bytes() -> None:
    payload = b'{"success": true, "data": {"id": "R-1"}}'

    parsed = reports.parse_report_file_content(payload)

    assert parsed["success"] is True
    assert parsed["data"]["id"] == "R-1"


@pytest.mark.unit
def test_parse_report_file_content_gzip_json() -> None:
    payload = gzip.compress(b'{"report": {"name": "loss-run"}}')

    parsed = reports.parse_report_file_content(payload)

    assert parsed == {"report": {"name": "loss-run"}}


@pytest.mark.unit
def test_parse_report_file_content_zip_single_json_file() -> None:
    payload = _zip_bytes({"report.json": b'{"rows": 25}'})

    parsed = reports.parse_report_file_content(payload)

    assert parsed == {"rows": 25}


@pytest.mark.unit
def test_parse_report_file_content_zip_multiple_files_returns_member_bytes() -> None:
    payload = _zip_bytes(
        {
            "report.csv": b"a,b\n1,2\n",
            "readme.txt": b"notes",
        }
    )

    parsed = reports.parse_report_file_content(payload)

    assert isinstance(parsed, dict)
    assert parsed["report.csv"] == b"a,b\n1,2\n"
    assert parsed["readme.txt"] == b"notes"


@pytest.mark.unit
def test_parse_report_file_content_raw_bytes_passthrough() -> None:
    payload = b"\x00\x01\x02\x03"

    parsed = reports.parse_report_file_content(payload)

    assert parsed == payload


@pytest.mark.unit
def test_download_report_file_decoded_uses_content_type_header() -> None:
    response = MagicMock()
    response.data = json.dumps({"ok": True, "count": 3}).encode("utf-8")
    response.headers = {"Content-Type": "application/json; charset=utf-8"}

    with patch.object(reports, "API_CLIENT") as mock_client:
        mock_client.do_request.return_value = response

        result = reports.download_report_file_decoded(file_id="F-1")

    assert result == {"ok": True, "count": 3}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/reports/download_report_file",
        json={"file_id": "F-1"},
        method="POST",
    )


@pytest.mark.unit
def test_download_report_file_raises_on_http_error() -> None:
    response = MagicMock()
    response.status = 500
    response.reason = "Server Error"
    response.data = b'{"success": false, "message": "bad"}'
    response.headers = {"Content-Type": "application/json"}

    class FakeClient:
        @staticmethod
        def _raise_for_http_status(*args, **kwargs):
            raise BritecoreError.ServerError(
                "Error - 500 - Server Error",
                http_status=500,
                endpoint="/api/v2/reports/download_report_file",
            )

        do_request = MagicMock(return_value=response)

    original_client = reports.API_CLIENT
    reports.API_CLIENT = FakeClient()
    try:
        with pytest.raises(BritecoreError.ServerError):
            reports.download_report_file(file_id="F-2")
    finally:
        reports.API_CLIENT = original_client


@pytest.mark.unit
def test_download_report_file_decoded_is_used_by_public_wrapper() -> None:
    response = MagicMock()
    response.data = gzip.compress(b'{"ok": true, "count": 7}')
    response.headers = {"Content-Type": "application/gzip"}

    with patch.object(reports, "API_CLIENT") as mock_client:
        mock_client.do_request.return_value = response

        result = reports.download_report_file(file_id="F-2")

    assert result == {"ok": True, "count": 7}
    mock_client.do_request.assert_called_once_with(
        path="/api/v2/reports/download_report_file",
        json={"file_id": "F-2"},
        method="POST",
    )
