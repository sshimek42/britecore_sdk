"""Unit tests for the newly-implemented v2 endpoint modules.

Covers: attachments, custom_ui, dashboards, data, errors, intacct,
nightly_jobs, notifications, printing, return_premium, search,
settings, signatures, uploads, vendors.

Each test class uses the same parametrized pattern as test_v2_endpoints.py:
  - call the wrapper with representative kwargs
  - assert do_request was called with the correct path + JSON body
  - assert process_result was called with the HTTP response
"""

import importlib
from unittest.mock import MagicMock, patch

import pytest
from urllib3 import BaseHTTPResponse

# ---------------------------------------------------------------------------
# Helpers (mirrors test_v2_endpoints.py)
# ---------------------------------------------------------------------------


def _make_response(
    payload: bytes = b'{"success": true, "data": {"id": "test_id"}}',
    status: int = 200,
) -> MagicMock:
    response = MagicMock(spec=BaseHTTPResponse)
    response.status = status
    response.reason = "OK" if status == 200 else "Error"
    response.data = payload
    return response


def _get_initialized_client(mock_settings):
    import britecore_libraries.api.api_calls as api_calls

    api_calls._api_client = None
    with patch(
        "britecore_libraries.api.britecore_api_client.LoadClientSettings"
    ) as mock_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_config.return_value = mock_settings
        mock_loader.return_value = mock_loader_instance
        return api_calls.get_api_client()


def _run_case(
    mock_settings, module_path, function_name, call_kwargs, expected_json, expected_path
):
    """Run a single endpoint test case."""
    module = importlib.import_module(module_path)
    client = _get_initialized_client(mock_settings)
    mock_response = _make_response(b'{"success": true, "data": {"ok": true}}')

    with (
        patch.object(
            client, "do_request", return_value=mock_response
        ) as mock_do_request,
        patch.object(
            client, "process_result", return_value={"ok": True}
        ) as mock_process_result,
    ):
        result = getattr(module, function_name)(**call_kwargs)

    assert result == {"ok": True}
    mock_do_request.assert_called_once_with(path=expected_path, json=expected_json)
    mock_process_result.assert_called_once_with(mock_response)


# ---------------------------------------------------------------------------
# attachments
# ---------------------------------------------------------------------------

ATTACHMENTS_CASES = [
    (
        "create_folder_in_user_folder",
        {"folder_name": "Docs", "reference_id": "R-1", "reference_type": "policy"},
        {"folder_name": "Docs", "reference_id": "R-1", "reference_type": "policy"},
        "/api/v2/attachments/create_folder_in_user_folder",
    ),
    (
        "delete_photo",
        {"file_id": "F-1"},
        {"file_id": "F-1"},
        "/api/v2/attachments/delete_photo",
    ),
    (
        "get_attachments_file_list",
        {"reference_id": "R-1", "reference_type": "policy", "page": 1},
        {"reference_id": "R-1", "reference_type": "policy", "page": 1},
        "/api/v2/attachments/get_attachments_file_list",
    ),
    (
        "get_file_metadata",
        {"file_id": "F-1"},
        {"file_id": "F-1"},
        "/api/v2/attachments/get_file_metadata",
    ),
    (
        "get_resource_photos",
        {"reference_id": "R-1"},
        {"reference_id": "R-1"},
        "/api/v2/attachments/get_resource_photos",
    ),
    (
        "move_user_file",
        {"file_id": "F-1", "to_folder_id": "FOLD-2"},
        {"file_id": "F-1", "to_folder_id": "FOLD-2"},
        "/api/v2/attachments/move_user_file",
    ),
    (
        "remove_attachments",
        {"attachment_ids": ["A-1", "A-2"]},
        {"attachment_ids": ["A-1", "A-2"]},
        "/api/v2/attachments/remove_attachments",
    ),
    (
        "rename_user_file",
        {"file_id": "F-1", "file_name": "new_name.pdf"},
        {"file_id": "F-1", "file_name": "new_name.pdf"},
        "/api/v2/attachments/rename_user_file",
    ),
    (
        "retrieve_attachments",
        {"reference_id": "R-1", "reference_type": "policy", "page": 1, "page_size": 25},
        {"reference_id": "R-1", "reference_type": "policy", "page": 1, "page_size": 25},
        "/api/v2/attachments/retrieve_attachments",
    ),
    (
        "upload_attachment_to_user_folder",
        {"file_name": "doc.pdf", "file_type": "application/pdf", "folder_id": "FOLD-1"},
        {"file_name": "doc.pdf", "file_type": "application/pdf", "folder_id": "FOLD-1"},
        "/api/v2/attachments/upload_attachment_to_user_folder",
    ),
    (
        "upload_attachment_unified",
        {
            "file_name": "doc.pdf",
            "file_type": "application/pdf",
            "revision_id": "REV-1",
        },
        {"file_name": "doc.pdf", "file_type": "application/pdf", "revisionId": "REV-1"},
        "/api/v2/attachments/upload_attachment_unified",
    ),
]


class TestAttachmentsEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        ATTACHMENTS_CASES,
    )
    def test_attachments_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.attachments",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# custom_ui
# ---------------------------------------------------------------------------

CUSTOM_UI_CASES = [
    ("retrieveurloverrides", {}, {}, "/api/v1/custom_ui/retrieveURLOverrides"),
    (
        "createurloverride",
        {"json_obj": {"url": "/custom"}},
        {"json_obj": {"url": "/custom"}},
        "/api/v1/custom_ui/createURLOverride",
    ),
    (
        "deleteurloverride",
        {"json_obj": {"id": "UI-1"}},
        {"json_obj": {"id": "UI-1"}},
        "/api/v1/custom_ui/deleteURLOverride",
    ),
    (
        "updateurloverride",
        {"json_obj": {"id": "UI-1", "url": "/updated"}},
        {"json_obj": {"id": "UI-1", "url": "/updated"}},
        "/api/v1/custom_ui/updateURLOverride",
    ),
]


class TestCustomUIEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        CUSTOM_UI_CASES,
    )
    def test_custom_ui_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.custom_ui",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# dashboards
# ---------------------------------------------------------------------------

DASHBOARDS_CASES = [
    (
        "get_agency_experience_data",
        {"contact_id": "C-1", "to_date": "2026-03-31"},
        {"contact_id": "C-1", "to_date": "2026-03-31"},
        "/api/v2/dashboards/get_agency_experience_data",
    ),
    (
        "get_csr_data",
        {"contact_id": "C-1"},
        {"contact_id": "C-1"},
        "/api/v2/dashboards/get_csr_data",
    ),
    (
        "get_loss_ratio_chart",
        {"contact_id": "C-1", "to_date": "2026-03-31"},
        {"contact_id": "C-1", "to_date": "2026-03-31"},
        "/api/v2/dashboards/get_loss_ratio_chart",
    ),
    (
        "get_policy_count_data",
        {"contact_id": "C-1", "to_date": "2026-03-31"},
        {"contact_id": "C-1", "to_date": "2026-03-31"},
        "/api/v2/dashboards/get_policy_count_data",
    ),
    (
        "get_premium_data",
        {"contact_id": "C-1", "to_date": "2026-03-31"},
        {"contact_id": "C-1", "to_date": "2026-03-31"},
        "/api/v2/dashboards/get_premium_data",
    ),
    (
        "get_report_url",
        {
            "contact_id": "C-1",
            "from_date": "2026-01-01",
            "to_date": "2026-03-31",
            "payment_types": "cc,ach",
        },
        {
            "contact_id": "C-1",
            "from_date": "2026-01-01",
            "to_date": "2026-03-31",
            "payment_types": "cc,ach",
        },
        "/api/v2/dashboards/get_report_url",
    ),
    (
        "get_transaction_report",
        {
            "contact_id": "C-1",
            "from_date": "2026-01-01",
            "to_date": "2026-03-31",
            "page": 1,
            "records_per_page": "25",
        },
        {
            "contact_id": "C-1",
            "from_date": "2026-01-01",
            "to_date": "2026-03-31",
            "page": 1,
            "records_per_page": "25",
        },
        "/api/v2/dashboards/get_transaction_report",
    ),
    (
        "validate_loss_run",
        {"contact_id": "C-1", "policy_number": "POL-1"},
        {"contact_id": "C-1", "policy_number": "POL-1"},
        "/api/v2/dashboards/validate_loss_run",
    ),
]


class TestDashboardsEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        DASHBOARDS_CASES,
    )
    def test_dashboards_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.dashboards",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# data
# ---------------------------------------------------------------------------

DATA_CASES = [
    (
        "export_data_as_csv",
        {"prep_dfs": "df1", "start_date": "2026-01-01", "end_date": "2026-03-31"},
        {"prep_dfs": "df1", "start_date": "2026-01-01", "end_date": "2026-03-31"},
        "/api/v2/data/export_data_as_csv",
    ),
    (
        "get_available_dashboards",
        {"module": "policies"},
        {"module": "policies"},
        "/api/v2/data/get_available_dashboards",
    ),
]


class TestDataEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"), DATA_CASES
    )
    def test_data_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.data",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# errors
# ---------------------------------------------------------------------------

ERRORS_CASES = [
    (
        "get_internal_error",
        {"internal_error_id": "ERR-1"},
        {"internal_error_id": "ERR-1"},
        "/api/v2/errors/get_internal_error",
    ),
]


class TestErrorsEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"), ERRORS_CASES
    )
    def test_errors_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.errors",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# intacct
# ---------------------------------------------------------------------------

INTACCT_CASES = [
    ("get_intacct_vendor_info", {}, {}, "/api/v2/intacct/get_intacct_vendor_info"),
    (
        "get_unexported_claim_transactions_xml",
        {},
        {},
        "/api/v2/intacct/get_unexported_claim_transactions_xml",
    ),
    (
        "get_unexported_return_premiums_xml",
        {},
        {},
        "/api/v2/intacct/get_unexported_return_premiums_xml",
    ),
    (
        "post_claim_transactions",
        {"payload": {"claim_id": "CLM-1"}},
        {"payload": {"claim_id": "CLM-1"}},
        "/api/v2/intacct/post_claim_transactions",
    ),
    (
        "post_return_premiums",
        {"payload": {"premium_id": "RP-1"}},
        {"payload": {"premium_id": "RP-1"}},
        "/api/v2/intacct/post_return_premiums",
    ),
]


class TestIntacctEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        INTACCT_CASES,
    )
    def test_intacct_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.intacct",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# nightly_jobs
# ---------------------------------------------------------------------------

NIGHTLY_JOBS_CASES = [
    (
        "process_auto_pays",
        {"on_date": "2026-03-31", "policy_number": "POL-1"},
        {"on_date": "2026-03-31", "policy_number": "POL-1"},
        "/api/v2/nightly_jobs/process_auto_pays",
    ),
    (
        "process_cancellation_pending_or_non_renewals",
        {"on_date": "2026-03-31", "policy_number": "POL-1"},
        {"on_date": "2026-03-31", "policy_number": "POL-1"},
        "/api/v2/nightly_jobs/process_cancellation_pending_or_non_renewals",
    ),
    (
        "process_non_pays_and_cancellations",
        {"on_date": "2026-03-31"},
        {"on_date": "2026-03-31"},
        "/api/v2/nightly_jobs/process_non_pays_and_cancellations",
    ),
    (
        "process_renewals",
        {"renew_date": "2026-04-01", "policy_number": "POL-1"},
        {"renew_date": "2026-04-01", "policy_number": "POL-1"},
        "/api/v2/nightly_jobs/process_renewals",
    ),
]


class TestNightlyJobsEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        NIGHTLY_JOBS_CASES,
    )
    def test_nightly_jobs_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.nightly_jobs",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# notifications
# ---------------------------------------------------------------------------

NOTIFICATIONS_CASES = [
    ("acknowledge", {}, {}, "/api/v2/notifications/acknowledge"),
    ("current", {}, {}, "/api/v2/notifications/current"),
]


class TestNotificationsEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        NOTIFICATIONS_CASES,
    )
    def test_notifications_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.notifications",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# printing
# ---------------------------------------------------------------------------

PRINTING_CASES = [
    (
        "getattachment",
        {"json_dict": {"attachment_id": "ATT-1"}},
        {"json_dict": {"attachment_id": "ATT-1"}},
        "/api/v1/printing/getAttachment",
    ),
    (
        "gettobeprinted",
        {"json_dict": {"policy_id": "POL-1"}},
        {"json_dict": {"policy_id": "POL-1"}},
        "/api/v1/printing/getToBePrinted",
    ),
    (
        "markasprinted",
        {"json_dict": {"ids": ["P-1", "P-2"]}},
        {"json_dict": {"ids": ["P-1", "P-2"]}},
        "/api/v1/printing/markAsPrinted",
    ),
    (
        "sendprinthawk",
        {"json_dict": {"document_id": "DOC-1"}},
        {"json_dict": {"document_id": "DOC-1"}},
        "/api/v1/printing/sendPrintHawk",
    ),
    ("sendprinthawkemail", {}, {}, "/api/v1/printing/sendPrintHawkEmail"),
]


class TestPrintingEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        PRINTING_CASES,
    )
    def test_printing_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.printing",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# return_premium
# ---------------------------------------------------------------------------

RETURN_PREMIUM_CASES = [
    (
        "exportreturnpremium",
        {"return_premium_id": "RP-1"},
        {"returnPremiumId": "RP-1"},
        "/api/v2/return_premium/exportReturnPremium",
    ),
]


class TestReturnPremiumEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        RETURN_PREMIUM_CASES,
    )
    def test_return_premium_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.return_premium",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# search
# ---------------------------------------------------------------------------

SEARCH_CASES = [
    (
        "add_to_index",
        {"document": {"title": "Policy"}, "id": "DOC-1", "index_name": "policies"},
        {"document": {"title": "Policy"}, "id": "DOC-1", "index_name": "policies"},
        "/api/v2/search/add_to_index",
    ),
    (
        "remove_from_index",
        {"id": "DOC-1", "index_name": "policies"},
        {"id": "DOC-1", "index_name": "policies"},
        "/api/v2/search/remove_from_index",
    ),
]


class TestSearchEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"), SEARCH_CASES
    )
    def test_search_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.search",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# settings
# ---------------------------------------------------------------------------

SETTINGS_CASES = [
    (
        "add_city_to_zip_override",
        {"city": "Springfield", "state_abbreviation": "IL", "zip_code": "62701"},
        {"city": "Springfield", "state_abbreviation": "IL", "zip_code": "62701"},
        "/api/v2/settings/add_city_to_zip_override",
    ),
    (
        "add_counties_to_state",
        {"counties": [{"name": "Sangamon"}], "country": "US"},
        {"counties": [{"name": "Sangamon"}], "country": "US"},
        "/api/v2/settings/add_counties_to_state",
    ),
    (
        "add_county_to_zip_override",
        {"county": "Sangamon", "state_abbreviation": "IL", "zip_code": "62701"},
        {"county": "Sangamon", "state_abbreviation": "IL", "zip_code": "62701"},
        "/api/v2/settings/add_county_to_zip_override",
    ),
    ("get_pdf_engine", {}, {}, "/api/v2/settings/get_pdf_engine"),
    (
        "get_setting_value",
        {"option": "max_retries", "section": "api"},
        {"option": "max_retries", "section": "api"},
        "/api/v2/settings/get_setting_value",
    ),
    ("get_system_tags_list", {}, {}, "/api/v2/settings/get_system_tags_list"),
    (
        "retrieve_credit_permission_prompt",
        {},
        {},
        "/api/v2/settings/retrieve_credit_permission_prompt",
    ),
    (
        "retrieve_property_valuation_availability",
        {"revision_id": "REV-1", "chosen_role": "agent", "is_app": False},
        {"revision_id": "REV-1", "chosen_role": "agent", "is_app": False},
        "/api/v2/settings/retrieve_property_valuation_availability",
    ),
    (
        "retrieve_system_tags",
        {"level": "policy"},
        {"level": "policy"},
        "/api/v2/settings/retrieve_system_tags",
    ),
    (
        "set_pdf_engine",
        {"engine": "weasyprint"},
        {"engine": "weasyprint"},
        "/api/v2/settings/set_pdf_engine",
    ),
    (
        "set_setting_value",
        {"option": "max_retries", "section": "api", "value": "3"},
        {"option": "max_retries", "section": "api", "value": "3"},
        "/api/v2/settings/set_setting_value",
    ),
]


class TestSettingsEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        SETTINGS_CASES,
    )
    def test_settings_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.settings",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# signatures
# ---------------------------------------------------------------------------

SIGNATURES_CASES = [
    (
        "docusign_auth",
        {"action": "login"},
        {"action": "login"},
        "/api/v2/signatures/docusign_auth",
    ),
    (
        "docusign_config",
        {"data": {"key": "value"}},
        {"data": {"key": "value"}},
        "/api/v2/signatures/docusign_config",
    ),
    (
        "get_signatures",
        {"revision_id": "REV-1"},
        {"revision_id": "REV-1"},
        "/api/v2/signatures/get_signatures",
    ),
    (
        "recreate_envelope",
        {"revision_id": "REV-1"},
        {"revision_id": "REV-1"},
        "/api/v2/signatures/recreate_envelope",
    ),
    (
        "update_signatures",
        {"envelope_id": "ENV-1", "status": "completed", "signers": "data"},
        {"envelope_id": "ENV-1", "status": "completed", "signers": "data"},
        "/api/v2/signatures/update_signatures",
    ),
    (
        "void_envelope",
        {"envelope_id": "ENV-1", "revision_id": "REV-1", "void_reason": "mistake"},
        {"envelopeId": "ENV-1", "revisionId": "REV-1", "voidReason": "mistake"},
        "/api/v2/signatures/void_envelope",
    ),
]


class TestSignaturesEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        SIGNATURES_CASES,
    )
    def test_signatures_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.signatures",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# uploads
# ---------------------------------------------------------------------------

UPLOADS_CASES = [
    (
        "attach_file_to_policy",
        {"payload": {"file_id": "F-1", "policy_id": "POL-1"}},
        {"payload": {"file_id": "F-1", "policy_id": "POL-1"}},
        "/api/v2/uploads/attach_file_to_policy",
    ),
]


class TestUploadsEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        UPLOADS_CASES,
    )
    def test_uploads_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.uploads",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# vendors
# ---------------------------------------------------------------------------

VENDORS_CASES = [
    (
        "build_ivans_manual_claim",
        {"data_list": [{"id": "C-1"}], "file_date": "2026-03-31"},
        {"data_list": [{"id": "C-1"}], "file_date": "2026-03-31"},
        "/api/v2/vendors/build_ivans_manual_claim",
    ),
    (
        "build_nxtech_initial_load",
        {"contact_id": "CON-1", "file_date": "2026-03-31"},
        {"contact_id": "CON-1", "file_date": "2026-03-31"},
        "/api/v2/vendors/build_nxtech_initial_load",
    ),
    (
        "build_nxtech_manual_transactions",
        {"data_list": [{"id": "T-1"}], "file_date": "2026-03-31"},
        {"data_list": [{"id": "T-1"}], "file_date": "2026-03-31"},
        "/api/v2/vendors/build_nxtech_manual_transactions",
    ),
    (
        "commercial_munichre_indepth_eligibility",
        {"property_id": "PROP-1"},
        {"property_id": "PROP-1"},
        "/api/v2/vendors/commercial_munichre_indepth_eligibility",
    ),
    (
        "fetch_motor_vehicle_report_for_drivers",
        {"drivers": [{"name": "Jane Doe"}], "store_no_hit": True},
        {"drivers": [{"name": "Jane Doe"}], "store_no_hit": True},
        "/api/v2/vendors/fetch_motor_vehicle_report_for_drivers",
    ),
    (
        "get_aon_cat_score",
        {"risk_id": "RISK-1", "geocoding_service": "google"},
        {"risk_id": "RISK-1", "geocoding_service": "google"},
        "/api/v2/vendors/get_aon_cat_score",
    ),
    (
        "get_prefill_services_data",
        {"property_id": "PROP-1"},
        {"property_id": "PROP-1"},
        "/api/v2/vendors/get_prefill_services_data",
    ),
    (
        "get_value360_token",
        {"property_id": "PROP-1", "home_type": "single_family"},
        {"property_id": "PROP-1", "home_type": "single_family"},
        "/api/v2/vendors/get_value360_token",
    ),
    (
        "get_wtw_score",
        {"property_descriptor": "single_family"},
        {"property": "single_family"},
        "/api/v2/vendors/get_wtw_score",
    ),
    (
        "invoice_cloud_autopay_enroll",
        {"policy_number": "POL-1", "enable": True},
        {"policy_number": "POL-1", "enable": True},
        "/api/v2/vendors/invoice_cloud_autopay_enroll",
    ),
    (
        "invoice_cloud_autopay_is_enrolled",
        {"policy_number": "POL-1"},
        {"policy_number": "POL-1"},
        "/api/v2/vendors/invoice_cloud_autopay_is_enrolled",
    ),
    (
        "invoice_cloud_suppress_insured_deliverable_printings",
        {"policy_number": "POL-1", "enable": True},
        {"policy_number": "POL-1", "enable": True},
        "/api/v2/vendors/invoice_cloud_suppress_insured_deliverable_printings",
    ),
    (
        "ivans_edocs_build",
        {"date_cursor": "2026-03-31", "file_ids": ["F-1"]},
        {"date_cursor": "2026-03-31", "file_ids": ["F-1"]},
        "/api/v2/vendors/ivans_edocs_build",
    ),
    (
        "ivans_file_upload",
        {"file_name": "test.txt", "ivans_type": "ACORD"},
        {"file_name": "test.txt", "ivans_type": "ACORD"},
        "/api/v2/vendors/ivans_file_upload",
    ),
    (
        "munichre_indepth_eligibility",
        {"property_id": "PROP-1"},
        {"property_id": "PROP-1"},
        "/api/v2/vendors/munichre_indepth_eligibility",
    ),
    (
        "update_value360_replacement_cost_value",
        {"report_id": "RPT-1", "result": {"rcv": 250000}},
        {"report_id": "RPT-1", "result": {"rcv": 250000}},
        "/api/v2/vendors/update_value360_replacement_cost_value",
    ),
]


class TestVendorsEndpoints:
    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        VENDORS_CASES,
    )
    def test_vendors_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        _run_case(
            mock_settings,
            "britecore_libraries.api.api_calls.v2.vendors",
            function_name,
            call_kwargs,
            expected_json,
            expected_path,
        )


# ---------------------------------------------------------------------------
# Omit-None behaviour: None args must not appear in the JSON body
# ---------------------------------------------------------------------------


class TestNoneOmission:
    """Verify that optional parameters set to None are omitted from the payload."""

    @pytest.mark.unit
    def test_none_params_omitted(self, env_api_key, mock_settings):
        module = importlib.import_module(
            "britecore_libraries.api.api_calls.v2.dashboards"
        )
        client = _get_initialized_client(mock_settings)
        mock_response = _make_response(b'{"success": true, "data": {}}')

        with (
            patch.object(
                client, "do_request", return_value=mock_response
            ) as mock_do_request,
            patch.object(client, "process_result", return_value={}),
        ):
            module.get_csr_data(contact_id=None)

        _, call_kwargs = mock_do_request.call_args
        assert "contact_id" not in call_kwargs["json"]

    @pytest.mark.unit
    def test_all_none_sends_empty_body(self, env_api_key, mock_settings):
        module = importlib.import_module("britecore_libraries.api.api_calls.v2.errors")
        client = _get_initialized_client(mock_settings)
        mock_response = _make_response(b'{"success": true, "data": {}}')

        with (
            patch.object(
                client, "do_request", return_value=mock_response
            ) as mock_do_request,
            patch.object(client, "process_result", return_value={}),
        ):
            module.get_internal_error()

        _, call_kwargs = mock_do_request.call_args
        assert call_kwargs["json"] == {}
