"""Tests closing v2 endpoint coverage gaps.

Modules targeted (grouped by class):
  deliverables  – list_attachments, get_attachment, get_edeliverables
  inspections   – update_inspection_dates (property_id path & policy_number path)
  utils         – get_available_function_names, rebuild_search_index, get_release_info
  notes         – retrieve_notes happy path, None response, missing-records key
  policies      – create_policy, retrieve_policy_terms, rate_revision,
                  retrieve_revision_details, retrieve_risks, retrieve_risk_details,
                  update_rating_information, rate_risk, retrieve_billing_schedule_options,
                  new_revision_contact (two paths), create_risk, update_property_location,
                  new_mortgagee, store_mortgagee, retrieve_policy_snapshot, get_policies,
                  retrieve_policy_ids, retrieve_policy_list_from_user,
                  retrieve_policy_contact_info
  contacts      – add_contact_to_role (success + missing id), update_contact,
                  find_contact_by_params, get_contacts_by_ids, new_contact edge cases
  lines         – get_export_line_file (both return branches), get_all_effective_dates,
                  get_all_states (with / without date_id), get_all_lines, list_policy_types
  async_policies – aretrieve_policy, aadd_line_item, aretrieve_policy_ids,
                   acreate_policy, aretrieve_policy_terms, arate_revision,
                   aretrieve_revision_details, aretrieve_risks
"""

import asyncio
import json as _json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from urllib3 import BaseHTTPResponse

from britecore_sdk.exceptions import BritecoreError

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _resp(payload: bytes = b'{"success":true,"data":{"ok":true}}', status: int = 200):
    r = MagicMock(spec=BaseHTTPResponse)
    r.status = status
    r.reason = "OK" if status == 200 else "Error"
    r.data = payload
    return r


def _client(mock_settings):
    """Return a freshly-initialised API client backed by mock settings."""
    import sys

    api_calls = sys.modules["britecore_sdk.api.api_calls"]
    api_calls._api_client = None
    with patch("britecore_sdk.api.britecore_api_client.LoadClientSettings") as ml:
        ml.return_value.load_config.return_value = mock_settings
        api_calls.init_api_client(target_site="test_site")
        return api_calls.get_api_client()


# ===========================================================================
# DELIVERABLES
# ===========================================================================


class TestDeliverablesEndpoints:
    def test_list_attachments_by_policy_id(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import deliverables

        client = _client(mock_settings)
        # multiple_parameter_verification is on the mocked client → stub it
        client.multiple_parameter_verification.return_value = {"policy_id": "POL-1"}
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response) as mock_req,
            patch.object(
                client, "process_result", return_value={"attachments": []}
            ) as mock_pr,
        ):
            result = deliverables.list_attachments(policy_id="POL-1")

        assert result == {"attachments": []}
        call_kwargs = mock_req.call_args
        assert call_kwargs.kwargs["path"] == "/api/v2/deliverables/list_attachments"
        mock_pr.assert_called_once_with(
            response, endpoint="/api/v2/deliverables/list_attachments"
        )

    def test_list_attachments_by_revision_id(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import deliverables

        client = _client(mock_settings)
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response),
            patch.object(client, "process_result", return_value=[]) as mock_pr,
        ):
            deliverables.list_attachments(revision_id="REV-1")

        mock_pr.assert_called_once()

    def test_get_attachment(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import deliverables

        client = _client(mock_settings)
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response) as mock_req,
            patch.object(client, "process_result", return_value={"file_id": "F-1"}),
        ):
            deliverables.get_attachment("F-1")

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/deliverables/get_attachment"
        assert call.kwargs["json"] == {"file_id": "F-1"}

    def test_get_edeliverables(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import deliverables

        client = _client(mock_settings)
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response) as mock_req,
            patch.object(client, "process_result", return_value=[]),
        ):
            deliverables.get_edeliverables("2026-01-01", "2026-01-31")

        call = mock_req.call_args
        assert call.args[0] == "/api/v2/deliverables/get_edeliverables"
        sent = call.kwargs["json"]
        assert sent["date_from"] == "2026-01-01"
        assert sent["date_to"] == "2026-01-31"
        assert sent["unprocessed_only"] is True


# ===========================================================================
# INSPECTIONS
# ===========================================================================


class TestInspectionsEndpoints:
    def test_update_via_property_id(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import inspections

        client = _client(mock_settings)
        client.multiple_parameter_verification.return_value = {"property_id": "PROP-1"}
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response) as mock_req,
            patch.object(client, "process_result", return_value={"ok": True}),
        ):
            inspections.update_inspection_dates(
                property_id="PROP-1",
                next_inspection_date="2026-06-01",
            )

        path = mock_req.call_args.kwargs["path"]
        assert path == "/api/v2/inspections/update_inspection_dates"

    def test_update_via_policy_number(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import inspections

        client = _client(mock_settings)
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response),
            patch.object(
                client, "process_result", return_value={"ok": True}
            ) as mock_pr,
        ):
            inspections.update_inspection_dates(policy_number="POL-1")

        mock_pr.assert_called_once()


# ===========================================================================
# UTILS
# ===========================================================================


class TestUtilsEndpoints:
    def test_get_available_function_names(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import utils

        client = _client(mock_settings)
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response) as mock_req,
            patch.object(client, "process_result", return_value=["fn1", "fn2"]),
        ):
            result = utils.get_available_function_names()

        assert result == ["fn1", "fn2"]
        assert (
            mock_req.call_args.kwargs["path"]
            == "/api/v2/utils/get_available_function_names"
        )

    def test_rebuild_search_index(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import utils

        client = _client(mock_settings)
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response) as mock_req,
            patch.object(client, "process_result", return_value=True),
        ):
            utils.rebuild_search_index(only_build=["policies"])

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/utils/rebuild_search_index"
        assert call.kwargs["json"] == {"only_build": ["policies"]}

    def test_get_release_info(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import utils

        client = _client(mock_settings)
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response) as mock_req,
            patch.object(client, "process_result", return_value={"version": "1.2.3"}),
        ):
            result = utils.get_release_info()

        assert result["version"] == "1.2.3"
        assert mock_req.call_args.kwargs["path"] == "/api/v2/utils/get_release_info"


# ===========================================================================
# NOTES – retrieve_notes edge cases
# ===========================================================================


class TestNotesRetrieveNotes:
    def test_returns_records_list_on_success(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import notes

        records = [{"note_id": "N-1", "text": "hello"}]
        raw_bytes = _json.dumps({"records": records}).encode()
        response = MagicMock(spec=BaseHTTPResponse)
        response.data = raw_bytes

        client = _client(mock_settings)
        with patch.object(client, "do_request", return_value=response):
            result = notes.retrieve_notes(id="POL-1")

        assert result == records

    def test_returns_empty_list_when_response_is_none(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import notes

        client = _client(mock_settings)
        with patch.object(client, "do_request", return_value=None):
            result = notes.retrieve_notes(id="POL-1")

        assert result == []

    def test_returns_empty_list_when_records_key_missing(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import notes

        raw_bytes = _json.dumps({"data": "something"}).encode()
        response = MagicMock(spec=BaseHTTPResponse)
        response.data = raw_bytes

        client = _client(mock_settings)
        with patch.object(client, "do_request", return_value=response):
            result = notes.retrieve_notes(id="POL-1")

        assert result == []

    def test_path_and_id_forwarded(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import notes

        response = MagicMock(spec=BaseHTTPResponse)
        response.data = _json.dumps({"records": []}).encode()

        client = _client(mock_settings)
        with patch.object(client, "do_request", return_value=response) as mock_req:
            notes.retrieve_notes(id="ENTITY-1")

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/notes/retrieveNotes"
        assert call.kwargs["json"]["id"] == "ENTITY-1"


# ===========================================================================
# POLICIES – missing endpoint coverage
# ===========================================================================


class TestPoliciesSimpleEndpoints:
    """Endpoints that follow the standard request-then-process_result pattern."""

    @pytest.mark.parametrize(
        ("fn_name", "kwargs", "expected_json", "expected_path"),
        [
            (
                "rate_revision",
                {"revision_id": "REV-1"},
                {"revision_id": "REV-1"},
                "/api/v2/policies/rate_revision",
            ),
            (
                "retrieve_risk_details",
                {"risk_id": "RISK-1"},
                {"risk_id": "RISK-1"},
                "/api/v2/policies/retrieve_risk_details",
            ),
            (
                "rate_risk",
                {"risk_id": "RISK-1"},
                {"risk_id": "RISK-1"},
                "/api/v2/policies/rate_risk",
            ),
            (
                "new_mortgagee",
                {"property_id": "PROP-1"},
                {"property_id": "PROP-1"},
                "/api/v2/policies/new_mortgagee",
            ),
            (
                "store_mortgagee",
                {"property_contact_id": "XP-1", "mortgagee_contact_id": "MC-1"},
                {
                    "x_properties_contact_id": "XP-1",
                    "mortgagee_contact_id": "MC-1",
                },
                "/api/v2/policies/store_mortgagee",
            ),
            (
                "retrieve_policy_snapshot",
                {"policy_number": "POL-1", "snapshot_date": "2026-01-01"},
                {"policy_number": "POL-1", "snapshot_date": "2026-01-01"},
                "/api/v2/policies/retrieve_policy_snapshot",
            ),
        ],
    )
    def test_simple_policy_endpoints(
        self,
        env_api_key,
        mock_settings,
        fn_name,
        kwargs,
        expected_json,
        expected_path,
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        response = _resp()
        with (
            patch.object(client, "do_request", return_value=response) as mock_req,
            patch.object(client, "process_result", return_value={"ok": True}),
        ):
            getattr(policies, fn_name)(**kwargs)

        call = mock_req.call_args
        # path may be positional or keyword depending on function
        actual_path = call.args[0] if call.args else call.kwargs.get("path")
        assert actual_path == expected_path
        actual_json = call.kwargs.get("json", {})
        for k, v in expected_json.items():
            assert actual_json.get(k) == v, f"json[{k!r}] mismatch"


class TestPoliciesComplexEndpoints:
    """Endpoints with non-trivial branching or return shapes."""

    def test_retrieve_policy_ids_returns_revision_and_property(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        policy_payload = {
            "active_revision": {
                "id": "REV-99",
                "primary_property_id": "PROP-99",
            }
        }
        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value=policy_payload),
        ):
            rev_id, prop_id = policies.retrieve_policy_ids("POL-1")

        assert rev_id == "REV-99"
        assert prop_id == "PROP-99"

    def test_retrieve_policy_ids_raises_on_empty_policy_number(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        _client(mock_settings)
        with pytest.raises(BritecoreError.MissingParameter):
            policies.retrieve_policy_ids("")

    def test_retrieve_policy_contact_info(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import policies

        policy_payload = {
            "active_revision": {
                "named_insureds": [{"contact_id": "C-1", "name": "Alice"}]
            }
        }
        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value=policy_payload),
        ):
            result = policies.retrieve_policy_contact_info("POL-1")

        assert result[0]["contact_id"] == "C-1"

    def test_retrieve_policy_list_from_user_check_name_true(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        search_result = {
            "records": [
                {"policyNumber": "P-100", "namedInsured": "alice smith, bob jones"},
                {"policyNumber": "P-200", "namedInsured": "carol white"},
            ]
        }
        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value=search_result),
        ):
            result = policies.retrieve_policy_list_from_user(
                "alice smith", check_name=True
            )

        assert result == ["P-100"]

    def test_retrieve_policy_list_from_user_check_name_false(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        search_result = {
            "records": [
                {"policyNumber": "P-100", "namedInsured": "alice smith"},
                {"policyNumber": "P-200", "namedInsured": "carol white"},
            ]
        }
        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value=search_result),
        ):
            result = policies.retrieve_policy_list_from_user("anyone", check_name=False)

        assert set(result) == {"P-100", "P-200"}

    def test_create_policy_returns_tuple(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import policies

        policy_data = {"policy_id": "POL-NEW", "revision_id": "REV-NEW"}
        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value=policy_data),
        ):
            result_data, revision_id = policies.create_policy(
                policy_number="POL-NEW",
                policy_type_id="PT-1",
                inception_date="2026-01-01",
            )

        assert revision_id == "REV-NEW"
        assert result_data["policy_id"] == "POL-NEW"

    def test_retrieve_policy_terms_by_policy_id(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        client.multiple_parameter_verification.return_value = {"policy_id": "POL-ID-1"}
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value={"terms": []}),
        ):
            policies.retrieve_policy_terms(policy_id="POL-ID-1")

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/policies/retrieve_policy_terms"

    def test_retrieve_revision_details(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(
                client, "process_result", return_value={"revision_id": "REV-5"}
            ),
        ):
            policies.retrieve_revision_details("REV-5")

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/policies/retrieve_revision_details"
        assert call.kwargs["json"]["revision_id"] == "REV-5"

    def test_retrieve_risks(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        client.json_dict_builder.return_value = {
            "revision_id": "REV-1",
            "page_size": 10,
        }
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value=[]),
        ):
            policies.retrieve_risks("REV-1")

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/policies/retrieve_risks"

    def test_update_rating_information(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        client.json_dict_builder.return_value = {
            "property_id": "PROP-1",
            "reset_premium": True,
        }
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value={}),
        ):
            policies.update_rating_information(property_id="PROP-1")

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/policies/update_rating_information"

    def test_retrieve_billing_schedule_options_by_policy_number(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value={}),
        ):
            policies.retrieve_billing_schedule_options(policy_number="POL-1")

        assert (
            mock_req.call_args.kwargs["path"]
            == "/api/v2/policies/retrieve_billing_schedule_options"
        )

    def test_new_revision_contact_creates_then_updates(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        new_contact_resp = _resp()
        update_contact_resp = _resp()

        client = _client(mock_settings)

        call_responses = [new_contact_resp, update_contact_resp]

        def _do_req(**kwargs):
            return call_responses.pop(0)

        with (
            patch.object(client, "do_request", side_effect=_do_req),
            patch.object(
                client,
                "process_result",
                side_effect=[
                    {"x_revisions_contact_id": "XRC-1"},  # new_revision_contact
                    {"ok": True},  # update_revision_contact
                ],
            ),
        ):
            policies.new_revision_contact(revision_id="REV-1", contact_id="C-1")

    def test_new_revision_contact_skips_create_when_x_id_provided(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value={"ok": True}),
        ):
            policies.new_revision_contact(
                revision_id="REV-1", contact_id="C-1", x_id="XRC-99"
            )

        # Only one request → the update_revision_contact one
        assert mock_req.call_count == 1
        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/policies/update_revision_contact"

    def test_create_risk(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(
                client, "process_result", return_value={"risk_id": "RISK-NEW"}
            ),
        ):
            result = policies.create_risk(revision_id="REV-1")

        assert result["risk_id"] == "RISK-NEW"
        assert mock_req.call_args.kwargs["path"] == "/api/v2/policies/create_risk"

    def test_update_property_location(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value={}),
        ):
            policies.update_property_location({"zip": "90210", "city": "BH"})

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/policies/update_property_location"
        # location key must be present in json
        assert "location" in call.kwargs["json"]

    def test_get_policies_all_optional_params(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        client.json_dict_builder.return_value = {
            "contact_id": "C-1",
            "from_date": "2026-01-01",
            "page_number": 1,
            "page_size": 50,
        }
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value={"policies": []}),
        ):
            policies.get_policies(
                contact_id="C-1",
                from_date="2026-01-01",
                to_date="2026-12-31",
                page_number=1,
                page_size=50,
            )

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/policies/get_policies"

    def test_add_line_item_returns_false_when_added_items_empty(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value={"added_items": []}),
        ):
            result = policies.add_line_item(revision_id="REV-1", item_id="ITEM-1")

        assert result is False

    def test_add_line_item_returns_false_when_process_result_none(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import policies

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value=None),
        ):
            result = policies.add_line_item(revision_id="REV-1", item_id="ITEM-1")

        assert result is False


# ===========================================================================
# CONTACTS – missing paths
# ===========================================================================


class TestContactsMissingPaths:
    def test_new_contact_raises_on_empty_name(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        _client(mock_settings)
        with pytest.raises(BritecoreError.MissingParameter):
            contacts.new_contact(name="", address=[{"street": "1 Way"}])

    def test_new_contact_raises_on_empty_address(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        _client(mock_settings)
        with pytest.raises(BritecoreError.MissingParameter):
            contacts.new_contact(name="Alice", address=[])

    def test_new_contact_returns_none_when_contact_id_missing(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import contacts

        client = _client(mock_settings)
        # process_result returns a dict without "contact_id"
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value={"name": "Alice"}),
        ):
            result, cid = contacts.new_contact(
                name="Alice", address=[{"street": "1 Way"}]
            )

        assert result is None
        assert cid is None

    def test_new_contact_returns_none_when_process_result_not_dict(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import contacts

        client = _client(mock_settings)
        # process_result returns non-dict → AttributeError path
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value=None),
        ):
            result, cid = contacts.new_contact(
                name="Bob", address=[{"street": "2 Lane"}]
            )

        assert result is None
        assert cid is None

    def test_new_contact_with_email_and_phone(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(
                client,
                "process_result",
                return_value={"contact_id": "C-NEW"},
            ),
        ):
            contacts.new_contact(
                name="Alice",
                address=[{"street": "1 Way"}],
                phone=[{"phone_number": "555-0000"}],
                email=[{"email_address": "a@b.com"}],
            )

        json_body = mock_req.call_args.kwargs["json"]
        assert "phones" in json_body
        assert "emails" in json_body

    def test_add_contact_to_role_raises_on_empty_id(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        _client(mock_settings)
        with pytest.raises(BritecoreError.MissingParameter):
            contacts.add_contact_to_role(contact_id="")

    def test_add_contact_to_role_success(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value={"ok": True}),
        ):
            contacts.add_contact_to_role(contact_id="C-1", role="Named Insured")

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/contacts/add_contact_to_role"
        assert call.kwargs["json"]["contact_id"] == "C-1"

    def test_update_contact(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value={}),
        ):
            contacts.update_contact({"contact_id": "C-1", "first_name": "Bob"})

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/contacts/update_contact"
        assert "contact" in call.kwargs["json"]

    def test_find_contact_by_params(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value=[]),
        ):
            contacts.find_contact_by_params(name="Alice", role_name="Named Insured")

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/contacts/find_contact_by_params"
        assert call.kwargs["json"]["name"] == "Alice"

    def test_get_contact_raises_on_empty_id(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        _client(mock_settings)
        with pytest.raises(BritecoreError.MissingParameter):
            contacts.get_contact(contact_id="")

    def test_get_contacts_by_ids_raises_on_invalid_input(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import contacts

        _client(mock_settings)
        with pytest.raises(BritecoreError.MissingParameter):
            contacts.get_contacts_by_ids([])  # empty list

    def test_get_contacts_by_ids_raises_on_non_list(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        _client(mock_settings)
        with pytest.raises(BritecoreError.MissingParameter):
            contacts.get_contacts_by_ids("C-1")  # type: ignore[arg-type]

    def test_get_contacts_by_ids_success(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import contacts

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value={"contacts": {}}),
        ):
            contacts.get_contacts_by_ids(["C-1", "C-2"])

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/contacts/get_contacts_by_ids"
        assert call.kwargs["json"]["contact_id_list"] == "C-1,C-2"


# ===========================================================================
# LINES – missing paths
# ===========================================================================


class TestLinesMissingPaths:
    def test_get_export_line_file_returns_parsed_json(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import lines

        parsed = {"items": ["a", "b"]}
        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value=_json.dumps(parsed)),
        ):
            result = lines.get_export_line_file(line=("ED-1", "STATE-1", "LINE-1"))

        assert result == parsed

    def test_get_export_line_file_returns_raw_response_when_processed_none(
        self, env_api_key, mock_settings
    ):
        from britecore_sdk.api.api_calls.v2 import lines

        raw = _resp()
        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=raw),
            patch.object(client, "process_result", return_value=None),
        ):
            result = lines.get_export_line_file(line=("ED-1", "STATE-1", "LINE-1"))

        assert result is raw

    def test_get_all_effective_dates(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import lines

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value=[]),
        ):
            lines.get_all_effective_dates()

        assert (
            mock_req.call_args.kwargs["path"] == "/api/v2/lines/get_all_effective_dates"
        )

    def test_get_all_states_without_date(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import lines

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value=[]),
        ):
            lines.get_all_states()

        call = mock_req.call_args
        assert call.kwargs["path"] == "/api/v2/lines/get_all_states"
        assert call.kwargs.get("json") == {}

    def test_get_all_states_with_date_id(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import lines

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value=[]),
        ):
            lines.get_all_states(effective_date_id="ED-1")

        assert mock_req.call_args.kwargs["json"] == {"effective_date_id": "ED-1"}

    def test_get_all_lines_without_location(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import lines

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value=[]),
        ):
            lines.get_all_lines(effective_date_id="ED-1")

        sent = mock_req.call_args.kwargs["json"]
        assert sent == {"effective_date_id": "ED-1"}

    def test_get_all_lines_with_location(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import lines

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()) as mock_req,
            patch.object(client, "process_result", return_value=[]),
        ):
            lines.get_all_lines(effective_date_id="ED-1", location_id="LOC-1")

        sent = mock_req.call_args.kwargs["json"]
        assert sent.get("location_id") == "LOC-1"

    def test_list_policy_types_with_effective_date_id(self, env_api_key, mock_settings):
        from britecore_sdk.api.api_calls.v2 import lines

        client = _client(mock_settings)
        with (
            patch.object(client, "do_request", return_value=_resp()),
            patch.object(client, "process_result", return_value=[]),
        ):
            lines.list_policy_types(location_id="LOC-1", effective_date_id="ED-1")

    def test_effective_date_payload_uses_date_when_no_id(self):
        """_effective_date_payload falls back to effective_date when no ID given."""
        from britecore_sdk.api.api_calls.v2.lines import _effective_date_payload

        result = _effective_date_payload(effective_date="2026-01-01")
        assert result == {"effective_date": "2026-01-01"}

    def test_effective_date_payload_returns_empty_when_neither(self):
        from britecore_sdk.api.api_calls.v2.lines import _effective_date_payload

        result = _effective_date_payload()
        assert result == {}


# ===========================================================================
# ASYNC POLICIES
# ===========================================================================


class TestAsyncPoliciesEndpoints:
    """Tests for async policy wrapper functions using asyncio.run()."""

    def _fake_sync_client(self):
        """Return a MagicMock sync client with a real web_timeout_long."""
        c = MagicMock()
        c.web_timeout_long = 50
        c.multiple_parameter_verification = MagicMock(
            return_value={"policy_number": "POL-1"}
        )
        return c

    def test_aretrieve_policy_by_number(self):
        response = MagicMock()
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.aget_client = AsyncMock(return_value=self._fake_sync_client())
            mc.ado_request = AsyncMock(return_value=response)
            mc.aprocess_result = AsyncMock(
                return_value={"policy_id": "P-1", "active_revision": {"id": "R-1"}}
            )

            from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_policy

            result = asyncio.run(aretrieve_policy(policy_number="POL-1"))

        assert result["policy_id"] == "P-1"
        mc.ado_request.assert_awaited_once()
        call = mc.ado_request.await_args.kwargs
        assert call["path"] == "/api/v2/policies/retrieve_policy"
        assert call["cache_enabled"] is True
        assert call["cache_namespace"] == "policies"

    def test_aadd_line_item_returns_bool_true(self):
        response = MagicMock()
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.ado_request = AsyncMock(return_value=response)
            mc.aprocess_result = AsyncMock(return_value={"added_items": ["item1"]})

            from britecore_sdk.api.api_calls.v2.async_policies import aadd_line_item

            result = asyncio.run(aadd_line_item(revision_id="REV-1", item_id="ITEM-1"))

        assert result is True
        call = mc.ado_request.await_args.kwargs
        assert call["path"] == "/api/v2/policies/add_line_item"
        assert "cache_invalidate_on_success" in call

    def test_aadd_line_item_returns_false_when_empty(self):
        response = MagicMock()
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.ado_request = AsyncMock(return_value=response)
            mc.aprocess_result = AsyncMock(return_value={"added_items": []})

            from britecore_sdk.api.api_calls.v2.async_policies import aadd_line_item

            result = asyncio.run(aadd_line_item(revision_id="REV-1", item_id="ITEM-1"))

        assert result is False

    def test_aretrieve_policy_ids(self):
        response = MagicMock()
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.aget_client = AsyncMock(return_value=self._fake_sync_client())
            mc.ado_request = AsyncMock(return_value=response)
            mc.aprocess_result = AsyncMock(
                return_value={
                    "active_revision": {
                        "id": "REV-ASYNC",
                        "primary_property_id": "PROP-ASYNC",
                    }
                }
            )

            from britecore_sdk.api.api_calls.v2.async_policies import (
                aretrieve_policy_ids,
            )

            rev_id, prop_id = asyncio.run(aretrieve_policy_ids("POL-1"))

        assert rev_id == "REV-ASYNC"
        assert prop_id == "PROP-ASYNC"

    def test_acreate_policy_returns_tuple(self):
        response = MagicMock()
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.ado_request = AsyncMock(return_value=response)
            mc.aprocess_result = AsyncMock(
                return_value={"policy_id": "NEW-P", "revision_id": "NEW-REV"}
            )

            from britecore_sdk.api.api_calls.v2.async_policies import acreate_policy

            policy_json, rev_id = asyncio.run(
                acreate_policy(policy_number="NEW-P", policy_type_id="PT-1")
            )

        assert rev_id == "NEW-REV"
        call = mc.ado_request.await_args.kwargs
        assert call["path"] == "/api/v2/policies/create_policy"
        assert "cache_invalidate_on_success" in call

    def test_acreate_policy_raises_on_custom_without_expiration(self):
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT"):
            from britecore_sdk.api.api_calls.v2.async_policies import acreate_policy

            with pytest.raises(BritecoreError.MissingParameter):
                asyncio.run(acreate_policy(term_type="Custom", expiration_date=""))

    def test_aretrieve_policy_terms_raises_without_identifiers(self):
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.aget_client = AsyncMock(return_value=self._fake_sync_client())
            from britecore_sdk.api.api_calls.v2.async_policies import (
                aretrieve_policy_terms,
            )

            with pytest.raises(BritecoreError.MissingParameter):
                asyncio.run(aretrieve_policy_terms())

    def test_aretrieve_policy_terms_enables_cache(self):
        response = MagicMock()
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.aget_client = AsyncMock(return_value=self._fake_sync_client())
            mc.ado_request = AsyncMock(return_value=response)
            mc.aprocess_result = AsyncMock(return_value={"terms": []})

            from britecore_sdk.api.api_calls.v2.async_policies import (
                aretrieve_policy_terms,
            )

            asyncio.run(aretrieve_policy_terms(policy_id="POL-ID-1"))

        call = mc.ado_request.await_args.kwargs
        assert call["cache_enabled"] is True
        assert call["path"] == "/api/v2/policies/retrieve_policy_terms"

    def test_arate_revision_invalidates_cache(self):
        response = MagicMock()
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.ado_request = AsyncMock(return_value=response)
            mc.aprocess_result = AsyncMock(return_value={})

            from britecore_sdk.api.api_calls.v2.async_policies import arate_revision

            asyncio.run(arate_revision("REV-1"))

        call = mc.ado_request.await_args.kwargs
        assert call["path"] == "/api/v2/policies/rate_revision"
        assert "cache_invalidate_on_success" in call

    def test_aretrieve_revision_details_enables_cache(self):
        response = MagicMock()
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.aget_client = AsyncMock(return_value=self._fake_sync_client())
            mc.ado_request = AsyncMock(return_value=response)
            mc.aprocess_result = AsyncMock(return_value={})

            from britecore_sdk.api.api_calls.v2.async_policies import (
                aretrieve_revision_details,
            )

            asyncio.run(aretrieve_revision_details("REV-1"))

        call = mc.ado_request.await_args.kwargs
        assert call["path"] == "/api/v2/policies/retrieve_revision_details"
        assert call["cache_enabled"] is True

    def test_aretrieve_risks_enables_cache(self):
        response = MagicMock()
        with patch("britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT") as mc:
            mc.ado_request = AsyncMock(return_value=response)
            mc.aprocess_result = AsyncMock(return_value=[])

            from britecore_sdk.api.api_calls.v2.async_policies import aretrieve_risks

            asyncio.run(aretrieve_risks("REV-1"))

        call = mc.ado_request.await_args.kwargs
        assert call["path"] == "/api/v2/policies/retrieve_risks"
        assert call["cache_enabled"] is True
        assert call["json"]["revision_id"] == "REV-1"
