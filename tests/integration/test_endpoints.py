"""Integration tests for API endpoint wrappers.

All tests in this file run with mocked HTTP transports (no live network call).
Tests that need a real BriteCore sandbox are decorated with
``@requires_sandbox`` (defined in conftest.py) and are skipped by default.

Run the full suite locally:
    pytest tests/integration/ -v

Run only live sandbox tests (requires env vars — see conftest.py):
    BRITECORE_INTEGRATION_TESTS=true BRITECORE_SANDBOX_URL=... pytest tests/integration/ -m sandbox -v
"""

from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from tests.integration.conftest import requires_sandbox

# ===========================================================================
# Quotes
# ===========================================================================


class TestQuotesEndpoints:
    """Tests for v2/quotes.py endpoint wrappers."""

    @pytest.mark.integration
    def test_create_full_quote(self):
        """create_full_quote returns (data_dict, quote_id) on success."""
        with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"id": "q-123", "number": "Q001"}

            from britecore_sdk.api.api_calls.v2.quotes import create_full_quote

            result, quote_id = create_full_quote(
                {"number": "Q001", "policy_type_id": "pt-1"}
            )

            assert result == {"id": "q-123", "number": "Q001"}
            assert quote_id == "q-123"
            mock.do_request.assert_called_once_with(
                path="/api/v2/quotes/create_full_quote",
                json={"number": "Q001", "policy_type_id": "pt-1"},
            )

    @pytest.mark.integration
    def test_create_full_quote_no_data_returns_none_tuple(self):
        """create_full_quote returns (None, None) when process_result gives falsy."""
        with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = None

            from britecore_sdk.api.api_calls.v2.quotes import create_full_quote

            result, quote_id = create_full_quote({"policy_type_id": "pt-1"})

            assert result is None
            assert quote_id is None

    @pytest.mark.integration
    def test_create_full_quote_returns_tuple_type(self):
        """create_full_quote always returns a 2-tuple."""
        with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"id": "q-xyz"}

            from britecore_sdk.api.api_calls.v2.quotes import create_full_quote

            result = create_full_quote({"policy_type_id": "pt-1"})
            assert isinstance(result, tuple)
            assert len(result) == 2

    @pytest.mark.integration
    def test_get_quote(self):
        """get_quote forwards the id and returns API data."""
        with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"id": "q-999", "number": "Q999"}

            from britecore_sdk.api.api_calls.v2.quotes import get_quote

            result = get_quote("q-999")

            assert result["id"] == "q-999"
            call_kwargs = mock.do_request.call_args
            assert call_kwargs.kwargs["json"]["id"] == "q-999"

    @pytest.mark.integration
    def test_get_quote_api_error_propagates(self):
        """get_quote propagates NoDataReturned from process_result."""
        from britecore_sdk.exceptions import BritecoreError

        with patch("britecore_sdk.api.api_calls.v2.quotes.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.side_effect = BritecoreError.NoDataReturned("Not found")

            from britecore_sdk.api.api_calls.v2.quotes import get_quote

            with pytest.raises(BritecoreError.NoDataReturned):
                get_quote("missing-id")


# ===========================================================================
# Policies
# ===========================================================================


class TestPoliciesEndpoints:
    """Tests for v2/policies.py endpoint wrappers."""

    @pytest.mark.integration
    def test_retrieve_policy_by_number(self):
        """retrieve_policy resolves the policy_number parameter."""
        with patch("britecore_sdk.api.api_calls.v2.policies.API_CLIENT") as mock:
            mock.multiple_parameter_verification.return_value = {
                "policy_number": "POL001"
            }
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {
                "id": "pol-1",
                "policy_number": "POL001",
            }

            from britecore_sdk.api.api_calls.v2.policies import retrieve_policy

            result = retrieve_policy(policy_number="POL001")

            assert result["policy_number"] == "POL001"

    @pytest.mark.integration
    def test_retrieve_policy_by_id(self):
        """retrieve_policy resolves the policy_id parameter."""
        with patch("britecore_sdk.api.api_calls.v2.policies.API_CLIENT") as mock:
            mock.multiple_parameter_verification.return_value = {"policy_id": "pol-42"}
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"id": "pol-42"}

            from britecore_sdk.api.api_calls.v2.policies import retrieve_policy

            result = retrieve_policy(policy_id="pol-42")

            assert result["id"] == "pol-42"

    @pytest.mark.integration
    def test_add_line_item_success(self):
        """add_line_item returns True on success."""
        with patch("britecore_sdk.api.api_calls.v2.policies.API_CLIENT") as mock:
            mock.json_dict_builder.return_value = {
                "revision_id": "rev-1",
                "item_id": "itm-1",
            }
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"added_items": ["itm-1"]}

            from britecore_sdk.api.api_calls.v2.policies import add_line_item

            result = add_line_item("rev-1", "itm-1")
            assert result is True

    @pytest.mark.integration
    def test_retrieve_policy_ids_extracts_revision_and_property(self):
        """retrieve_policy_ids returns (revision_id, primary_property_id)."""
        with patch("britecore_sdk.api.api_calls.v2.policies.retrieve_policy") as mock:
            mock.return_value = {
                "active_revision": {
                    "id": "rev-99",
                    "primary_property_id": "prop-99",
                }
            }

            from britecore_sdk.api.api_calls.v2.policies import (
                retrieve_policy_ids,
            )

            rev_id, prop_id = retrieve_policy_ids("POL-99")

            assert rev_id == "rev-99"
            assert prop_id == "prop-99"


# ===========================================================================
# Contacts (v2)
# ===========================================================================


class TestContactsV2Endpoints:
    """Tests for v2/contacts.py endpoint wrappers."""

    @pytest.mark.integration
    def test_get_contact_by_id(self):
        """get_contact returns contact data for a given ID."""
        with patch("britecore_sdk.api.api_calls.v2.contacts.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"id": "c-1", "name": "Jane Doe"}

            from britecore_sdk.api.api_calls.v2.contacts import get_contact

            result = get_contact("c-1")

            assert result["id"] == "c-1"
            assert result["name"] == "Jane Doe"

    @pytest.mark.integration
    def test_new_contact_returns_id(self):
        """new_contact returns (contact_data, contact_id) on success."""
        with patch("britecore_sdk.api.api_calls.v2.contacts.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {
                "contact_id": "c-new-1",
                "name": "John Smith",
            }

            from britecore_sdk.api.api_calls.v2.contacts import new_contact

            contact_data, contact_id = new_contact(
                name="John Smith",
                address=[
                    {
                        "street": "123 Main St",
                        "city": "Springfield",
                        "state": "IL",
                        "zip": "62701",
                    }
                ],
            )

            contact_data = cast(dict[str, Any], contact_data)
            assert contact_id == "c-new-1"
            assert contact_data["name"] == "John Smith"

    @pytest.mark.integration
    def test_new_contact_missing_contact_id_key(self):
        """new_contact returns (None, None) when contact_id key is absent from response."""
        with patch("britecore_sdk.api.api_calls.v2.contacts.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"name": "No ID Here"}

            from britecore_sdk.api.api_calls.v2.contacts import new_contact

            result, contact_id = new_contact(name="No ID Here", address=[{}])
            # When contact_id key is missing the function logs an error and returns (None, None)
            assert result is None
            assert contact_id is None


# ===========================================================================
# Claims
# ===========================================================================


class TestClaimsEndpoints:
    """Tests for v2/claims.py endpoint wrappers."""

    @pytest.mark.integration
    def test_get_claim_success(self):
        """get_claim sends claim_id and returns claim data."""
        with patch("britecore_sdk.api.api_calls.v2.claims.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"claim_id": "clm-1", "status": "open"}

            from britecore_sdk.api.api_calls.v2.claims import get_claim

            result = get_claim("clm-1")

            assert result["claim_id"] == "clm-1"
            call_kwargs = mock.do_request.call_args.kwargs
            assert call_kwargs["json"]["claim_id"] == "clm-1"
            assert call_kwargs["path"] == "/api/v2/claims/get_claim"

    @pytest.mark.integration
    def test_get_claim_not_found_raises(self):
        """get_claim propagates NoDataReturned when process_result raises."""
        from britecore_sdk.exceptions import BritecoreError

        with patch("britecore_sdk.api.api_calls.v2.claims.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.side_effect = BritecoreError.NoDataReturned(
                "Claim not found"
            )

            from britecore_sdk.api.api_calls.v2.claims import get_claim

            with pytest.raises(BritecoreError.NoDataReturned, match="Claim not found"):
                get_claim("missing")


# ===========================================================================
# Deliverables
# ===========================================================================


class TestDeliverablesEndpoints:
    """Tests for v2/deliverables.py endpoint wrappers."""

    @pytest.mark.integration
    def test_list_attachments_by_policy(self):
        """list_attachments sends correct path and returns attachment list."""
        with (
            patch("britecore_sdk.api.api_calls.v2.deliverables.API_CLIENT") as mock,
            patch(
                "britecore_sdk.api.api_calls.v2.deliverables.api_client"
            ) as mock_module,
        ):
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = [{"file_id": "f-1"}, {"file_id": "f-2"}]
            mock_module.multiple_parameter_verification.return_value = {
                "policy_id": "pol-5"
            }

            from britecore_sdk.api.api_calls.v2.deliverables import (
                list_attachments,
            )

            result = list_attachments(policy_id="pol-5")

            assert isinstance(result, list)
            assert (
                mock.do_request.call_args.kwargs["path"]
                == "/api/v2/deliverables/list_attachments"
            )

    @pytest.mark.integration
    def test_get_attachment_success(self):
        """get_attachment sends file_id and returns attachment data."""
        with patch("britecore_sdk.api.api_calls.v2.deliverables.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {
                "file_id": "f-99",
                "url": "https://cdn.example.com/f-99.pdf",
            }

            from britecore_sdk.api.api_calls.v2.deliverables import get_attachment

            result = get_attachment("f-99")

            assert result["file_id"] == "f-99"
            assert mock.do_request.call_args.kwargs["json"]["file_id"] == "f-99"

    @pytest.mark.integration
    def test_get_edeliverables_sends_date_range(self):
        """get_edeliverables sends correct date range payload."""
        with patch("britecore_sdk.api.api_calls.v2.deliverables.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = [{"deliverable_id": "ed-1"}]

            from britecore_sdk.api.api_calls.v2.deliverables import (
                get_edeliverables,
            )

            result = get_edeliverables("2026-01-01", "2026-03-31")

            assert isinstance(result, list)
            sent_json = mock.do_request.call_args.kwargs["json"]
            assert sent_json["date_from"] == "2026-01-01"
            assert sent_json["date_to"] == "2026-03-31"


# ===========================================================================
# Inspections
# ===========================================================================


class TestInspectionsEndpoints:
    """Tests for v2/inspections.py endpoint wrappers."""

    @pytest.mark.integration
    def test_update_inspection_dates_by_policy_number(self):
        """update_inspection_dates resolves policy_number and sends dates."""
        with (
            patch("britecore_sdk.api.api_calls.v2.inspections.API_CLIENT") as mock,
            patch(
                "britecore_sdk.api.api_calls.v2.inspections.api_client"
            ) as mock_module,
        ):
            mock_module.multiple_parameter_verification.return_value = {
                "policy_number": "POL-INS"
            }
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {"updated": True}

            from britecore_sdk.api.api_calls.v2.inspections import (
                update_inspection_dates,
            )

            result = update_inspection_dates(
                policy_number="POL-INS",
                next_inspection_date="2026-06-01",
            )

            assert result == {"updated": True}
            assert (
                mock.do_request.call_args.kwargs["path"]
                == "/api/v2/inspections/update_inspection_dates"
            )


# ===========================================================================
# Insured
# ===========================================================================


class TestInsuredEndpoints:
    """Tests for v2/insured.py endpoint wrappers."""

    @pytest.mark.integration
    def test_get_property_information_and_photos(self):
        """get_property_information_and_photos sends property_id and returns data."""
        with patch("britecore_sdk.api.api_calls.v2.insured.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = {
                "property_id": "prop-1",
                "address": "123 Main St",
                "photos": [],
            }

            from britecore_sdk.api.api_calls.v2.insured import (
                get_property_information_and_photos,
            )

            result = get_property_information_and_photos("prop-1")

            assert result["property_id"] == "prop-1"
            call_kwargs = mock.do_request.call_args.kwargs
            assert call_kwargs["json"]["property_id"] == "prop-1"
            assert "insured" in call_kwargs["path"]

    @pytest.mark.integration
    def test_get_property_information_propagates_error(self):
        """get_property_information_and_photos propagates NoDataReturned."""
        from britecore_sdk.exceptions import BritecoreError

        with patch("britecore_sdk.api.api_calls.v2.insured.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.side_effect = BritecoreError.NoDataReturned(
                "Property not found"
            )

            from britecore_sdk.api.api_calls.v2.insured import (
                get_property_information_and_photos,
            )

            with pytest.raises(BritecoreError.NoDataReturned):
                get_property_information_and_photos("no-such-property")


# ===========================================================================
# Notes
# ===========================================================================


class TestNotesEndpoints:
    """Tests for v2/notes.py endpoint wrappers."""

    @pytest.mark.integration
    def test_retrieve_notes_default_params(self):
        """retrieve_notes returns list of records on success."""
        import json as json_mod

        raw_payload = json_mod.dumps(
            {"records": [{"id": "n-1", "text": "Note A"}]}
        ).encode()

        with patch("britecore_sdk.api.api_calls.v2.notes.API_CLIENT") as mock:
            mock_resp = MagicMock()
            mock_resp.data = raw_payload
            mock.do_request.return_value = mock_resp

            from britecore_sdk.api.api_calls.v2.notes import retrieve_notes

            result = retrieve_notes("entity-id-1")

            assert isinstance(result, list)
            assert result[0]["id"] == "n-1"

    @pytest.mark.integration
    def test_retrieve_notes_returns_empty_on_no_response(self):
        """retrieve_notes returns [] when do_request returns None."""
        with patch("britecore_sdk.api.api_calls.v2.notes.API_CLIENT") as mock:
            mock.do_request.return_value = None

            from britecore_sdk.api.api_calls.v2.notes import retrieve_notes

            result = retrieve_notes("entity-id-1")
            assert result == []


# ===========================================================================
# Reports
# ===========================================================================


class TestReportsEndpoints:
    """Tests for v2/reports.py endpoint wrappers."""

    @pytest.mark.integration
    def test_list_files_success(self):
        """list_files sends report_id and returns processed result."""
        with patch("britecore_sdk.api.api_calls.v2.reports.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.return_value = [{"file": "report_q1.pdf"}]

            from britecore_sdk.api.api_calls.v2.reports import list_files

            result = list_files("rpt-1")

            assert isinstance(result, list)
            call_args = mock.do_request.call_args
            # path may be passed as positional or keyword argument
            path_used = (
                call_args.args[0] if call_args.args else call_args.kwargs.get("path")
            )
            sent_json = call_args.kwargs.get("json") or (
                call_args.args[1] if len(call_args.args) > 1 else None
            )
            assert path_used == "/api/v2/reports/list_files"
            assert sent_json["report_id"] == "rpt-1"

    @pytest.mark.integration
    def test_list_files_error_propagates(self):
        """list_files propagates NoDataReturned from process_result."""
        from britecore_sdk.exceptions import BritecoreError

        with patch("britecore_sdk.api.api_calls.v2.reports.API_CLIENT") as mock:
            mock.do_request.return_value = MagicMock()
            mock.process_result.side_effect = BritecoreError.NoDataReturned(
                "Report not found"
            )

            from britecore_sdk.api.api_calls.v2.reports import list_files

            with pytest.raises(BritecoreError.NoDataReturned):
                list_files("missing-report")


# ===========================================================================
# Contacts (v1 API - no v2 equivalent)
# ===========================================================================


class TestContactsV1Endpoints:
    """Tests for v1/contacts.py endpoint wrappers."""

    @pytest.mark.integration
    def test_retrieve_contact_list(self):
        """retrieve_contact_list sends search name and returns raw JSON records."""
        import json as json_mod

        raw = json_mod.dumps({"records": [{"id": "cv1-1", "name": "John"}]}).encode()

        with patch("britecore_sdk.api.api_calls.v1.contacts.API_CLIENT") as mock:
            mock_resp = MagicMock()
            mock_resp.data = raw
            mock.do_request.return_value = mock_resp

            from britecore_sdk.api.api_calls.v1.contacts import (
                retrieve_contact_list,
            )

            result = retrieve_contact_list("John")

            assert result is not None
            mock.do_request.assert_called_once()


# ===========================================================================
# Cross-cutting: HTTP error handling in process_result
# ===========================================================================


class TestHTTPErrorHandling:
    """Verify process_result raises the correct exception type for each HTTP status."""

    def _get_client(self):
        """Create a minimal BritecoreAPIClient for testing."""
        from unittest.mock import MagicMock, patch

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = MagicMock(
                base_url="https://api.example.com",
                client_id="",
                client_secret="",
                api_key="test-key",
                web_timeout=5,
                web_timeout_long=50,
                web_retry=3,
            )
            mock_loader.return_value = mock_loader_instance
            client = BritecoreAPIClient("test_site")
            client.init_client()
        return client

    @pytest.mark.integration
    def test_401_raises_authentication_error(self):
        """process_result raises AuthenticationError on HTTP 401."""
        from britecore_sdk.exceptions import BritecoreError

        client = self._get_client()
        resp = MagicMock()
        resp.status = 401
        resp.reason = "Unauthorized"

        with pytest.raises(BritecoreError.AuthenticationError):
            client.process_result(resp)

    @pytest.mark.integration
    def test_403_raises_authentication_error(self):
        """process_result raises AuthenticationError on HTTP 403."""
        from britecore_sdk.exceptions import BritecoreError

        client = self._get_client()
        resp = MagicMock()
        resp.status = 403
        resp.reason = "Forbidden"

        with pytest.raises(BritecoreError.AuthenticationError):
            client.process_result(resp)

    @pytest.mark.integration
    def test_429_raises_rate_limit_error_with_retry_after(self):
        """process_result raises RateLimitError on HTTP 429, parsing Retry-After."""
        from britecore_sdk.exceptions import BritecoreError

        client = self._get_client()
        resp = MagicMock()
        resp.status = 429
        resp.reason = "Too Many Requests"
        resp.headers = {"Retry-After": "60"}

        with pytest.raises(BritecoreError.RateLimitError) as exc_info:
            client.process_result(resp)

        assert exc_info.value.retry_after == 60

    @pytest.mark.integration
    def test_500_raises_server_error(self):
        """process_result raises ServerError on HTTP 500."""
        from britecore_sdk.exceptions import BritecoreError

        client = self._get_client()
        resp = MagicMock()
        resp.status = 500
        resp.reason = "Internal Server Error"

        with pytest.raises(BritecoreError.ServerError):
            client.process_result(resp)

    @pytest.mark.integration
    def test_none_response_raises_no_data_returned(self):
        """process_result raises NoDataReturned when response is None."""
        from britecore_sdk.exceptions import BritecoreError

        client = self._get_client()

        with pytest.raises(BritecoreError.NoDataReturned):
            client.process_result(None)

    @pytest.mark.integration
    def test_success_false_body_raises_no_data_returned(self):
        """process_result raises NoDataReturned when success=false in body."""
        import json as json_mod

        from britecore_sdk.exceptions import BritecoreError

        client = self._get_client()
        resp = MagicMock()
        resp.status = 200
        resp.data = json_mod.dumps(
            {"success": False, "message": "Policy not found"}
        ).encode()

        with pytest.raises(BritecoreError.NoDataReturned, match="Policy not found"):
            client.process_result(resp)


# ===========================================================================
# Structured tracing (request_id + latency logging)
# ===========================================================================


class TestStructuredTracing:
    """Verify that do_request emits structured DEBUG log lines."""

    @pytest.mark.integration
    def test_do_request_logs_request_id_arrows(self):
        """do_request emits [<id>] → and [<id>] ← DEBUG log calls."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        client = BritecoreAPIClient.__new__(BritecoreAPIClient)
        client.use_api_key = True
        client.web_timeout = 5
        client.web_retry = 3
        client.base_url = "https://api.example.com"
        client.site_settings = MagicMock()
        client.site_settings.api_key = "test-key"

        ok_resp = MagicMock()
        ok_resp.status = 200
        client.http = MagicMock()
        client.http.request.return_value = ok_resp

        with patch("britecore_sdk.api.britecore_api_client.LOGGER") as mock_logger:
            client.do_request(path="/api/v2/test/endpoint", json={"x": 1})

        debug_calls = [str(call) for call in mock_logger.debug.call_args_list]
        log_text = " ".join(debug_calls)
        assert "→" in log_text, f"Expected '→' in debug calls: {debug_calls}"
        assert "←" in log_text, f"Expected '←' in debug calls: {debug_calls}"

    @pytest.mark.integration
    def test_do_request_logs_on_timeout(self):
        """do_request logs error with timeout info before re-raising."""
        from urllib3.exceptions import TimeoutError as Urllib3Timeout

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
        from britecore_sdk.exceptions import BritecoreError

        client = BritecoreAPIClient.__new__(BritecoreAPIClient)
        client.use_api_key = True
        client.web_timeout = 5
        client.web_retry = 3
        client.base_url = "https://api.example.com"
        client.site_settings = MagicMock()
        client.site_settings.api_key = "test-key"
        client.http = MagicMock()
        client.http.request.side_effect = Urllib3Timeout("timed out")

        with (
            patch("britecore_sdk.api.britecore_api_client.LOGGER") as mock_logger,
            pytest.raises(BritecoreError.RequestTimeoutError),
        ):
            client.do_request(path="/api/v2/test/slow", json={"x": 1})

        error_calls = [str(call) for call in list(mock_logger.error.call_args_list)]
        log_text = " ".join(error_calls)
        has_timeout = "timeout" in log_text.lower()
        assert has_timeout, f"Expected 'timeout' in error calls: {error_calls}"


# ===========================================================================
# Live sandbox tests (skipped unless BRITECORE_INTEGRATION_TESTS=true)
# ===========================================================================


@requires_sandbox
class TestLiveSandboxQuotes:
    """Live BriteCore sandbox tests — skipped unless sandbox env vars are set."""

    @pytest.mark.sandbox
    def test_live_client_initialises(self):
        """Verify the client can initialise against the sandbox URL."""
        import os

        from britecore_sdk.api.api_calls import init_api_client

        client = init_api_client(os.environ["BRITECORE_SANDBOX_URL"])
        assert client is not None

    @pytest.mark.sandbox
    def test_live_create_quote_round_trip(self):
        """Create a minimal quote and retrieve it back (requires sandbox data)."""
        pytest.skip(
            "Requires known sandbox policy type ID — configure before enabling."
        )
