"""Unit tests for v2 endpoint wrappers.

This module provides comprehensive test coverage for BriteCore API v2 endpoint
wrapper functions, covering happy path and error scenarios.
"""

import importlib
from unittest.mock import MagicMock, patch

import pytest
from urllib3 import BaseHTTPResponse

from britecore_sdk.exceptions import BritecoreError


def _make_response(
    payload: bytes = b'{"success": true, "data": {"id": "test_id"}}',
    status: int = 200,
) -> MagicMock:
    """Helper to create mock HTTP responses."""
    response = MagicMock(spec=BaseHTTPResponse)
    response.status = status
    response.reason = "OK" if status == 200 else "Error"
    response.data = payload
    return response


def _get_initialized_client(mock_settings):
    """Return a lazily initialized API client backed by mocked settings.

    Uses ``sys.modules`` directly instead of ``import ... as`` so that the
    correct module object is retrieved even when a prior test temporarily
    replaced ``britecore_sdk.api.api_calls`` in sys.modules and the
    parent-package attribute has not yet been restored.
    """
    import sys

    api_calls = sys.modules["britecore_sdk.api.api_calls"]

    api_calls._api_client = None

    with patch(
        "britecore_sdk.api.britecore_api_client.LoadClientSettings"
    ) as mock_loader:
        mock_loader_instance = MagicMock()
        mock_loader_instance.load_config.return_value = mock_settings
        mock_loader.return_value = mock_loader_instance
        api_calls.init_api_client(target_site="test_site")
        return api_calls.get_api_client()


BILLING_ENDPOINT_CASES = [
    (
        "get_installments_preview",
        {
            "billing_schedule_ids": ["BS-1"],
            "effective_date": "2026-04-01",
            "premium": 123.45,
            "payment_method": "credit_card",
        },
        {
            "billing_schedule_ids": ["BS-1"],
            "effective_date": "2026-04-01",
            "premium": 123.45,
            "payment_method": "credit_card",
        },
        "/api/v2/billing/get_installments_preview",
    ),
    (
        "get_installments_preview_mid_term",
        {
            "billing_schedule_ids": ["BS-1", "BS-2"],
            "payment_method": "ach",
            "revision_effective_date": "2026-05-01",
            "prorated_premium": 67.89,
            "policy_id": "POL-1",
        },
        {
            "billing_schedule_ids": ["BS-1", "BS-2"],
            "payment_method": "ach",
            "revision_effective_date": "2026-05-01",
            "prorated_premium": 67.89,
            "policy_id": "POL-1",
        },
        "/api/v2/billing/get_installments_preview_mid_term",
    ),
    (
        "get_renewal_installments_preview",
        {
            "billing_schedule_ids": ["BS-3"],
            "effective_date": "2027-01-01",
            "premium": 222.22,
            "payment_method": "check",
        },
        {
            "billing_schedule_ids": ["BS-3"],
            "effective_date": "2027-01-01",
            "premium": 222.22,
            "payment_method": "check",
        },
        "/api/v2/billing/get_renewal_installments_preview",
    ),
    (
        "rating_factors",
        {"policy_id": "POL-2"},
        {"policy_id": "POL-2"},
        "/api/v2/billing/rating_factors",
    ),
]


ACCOUNTING_ENDPOINT_CASES = [
    (
        "get_accounting_deliverable",
        {
            "account_history_id": "AH-1",
            "deliverable_date": "2026-03-31",
        },
        {
            "account_history_id": "AH-1",
            "deliverable_date": "2026-03-31",
        },
        "/api/v2/accounting/get_accounting_deliverable",
    ),
    (
        "get_invoices",
        {
            "policy_id": "POL-1",
            "bill_from_date": "2026-01-01",
            "bill_to_date": "2026-01-31",
            "due_from_date": "2026-02-01",
            "due_to_date": "2026-02-28",
            "sorting_order": "asc",
            "page_number": 2,
            "page_size": 50,
        },
        {
            "policy_id": "POL-1",
            "bill_from_date": "2026-01-01",
            "bill_to_date": "2026-01-31",
            "due_from_date": "2026-02-01",
            "due_to_date": "2026-02-28",
            "sorting_order": "asc",
            "page_number": 2,
            "page_size": 50,
        },
        "/api/v2/accounting/get_invoices",
    ),
    (
        "run_rescind_underwriting_cancellation_pending_logic",
        {
            "revision_id": "REV-1",
            "old_status": "cancellation_pending",
            "date_cursor": "2026-04-15",
        },
        {
            "revision_id": "REV-1",
            "old_status": "cancellation_pending",
            "date_cursor": "2026-04-15",
        },
        "/api/v2/accounting/run_rescind_underwriting_cancellation_pending_logic",
    ),
]


CLAIMS_ENDPOINT_CASES = [
    (
        "get_claim",
        {"claim_id": "CLM-1"},
        {"claim_id": "CLM-1"},
        "/api/v2/claims/get_claim",
    ),
    (
        "export_claim_payments",
        {"claim_ids": ["CLM-1", "CLM-2"]},
        {"claim_ids": ["CLM-1", "CLM-2"]},
        "/api/v2/claims/export_claim_payments",
    ),
    (
        "get_all_catastrophes",
        {},
        {},
        "/api/v2/claims/get_all_catastrophes",
    ),
    (
        "get_all_perils",
        {},
        {},
        "/api/v2/claims/get_all_perils",
    ),
    (
        "get_claim_contacts",
        {"claim_id": "CLM-9"},
        {"claim_id": "CLM-9"},
        "/api/v2/claims/get_claim_contacts",
    ),
    (
        "get_claim_payments",
        {"claim_id": "CLM-9"},
        {"claim_id": "CLM-9"},
        "/api/v2/claims/get_claim_payments",
    ),
    (
        "update_claim",
        {"claim_id": "CLM-9", "claim": {"status": "closed"}},
        {"claim_id": "CLM-9", "claim": {"status": "closed"}},
        "/api/v2/claims/update_claim",
    ),
]


COMMISSIONS_ENDPOINT_CASES = [
    (
        "delete_batch_payments",
        {"payment_ids": ["CP-1", "CP-2"]},
        {"payment_ids": ["CP-1", "CP-2"]},
        "/api/v2/commissions/delete_batch_payments",
    ),
    (
        "delete_payment",
        {"payment_id": "CP-1"},
        {"payment_id": "CP-1"},
        "/api/v2/commissions/delete_payment",
    ),
    (
        "get_commission_payees",
        {},
        {},
        "/api/v2/commissions/get_commission_payees",
    ),
    (
        "get_payment",
        {"commission_payment_id": "CP-9"},
        {"commission_payment_id": "CP-9"},
        "/api/v2/commissions/get_payment",
    ),
    (
        "get_unexported_commissions",
        {},
        {},
        "/api/v2/commissions/get_unexported_commissions",
    ),
    (
        "save_batch_payments",
        {"payments": [{"id": "CP-1", "amount": 19.99}]},
        {"payments": [{"id": "CP-1", "amount": 19.99}]},
        "/api/v2/commissions/save_batch_payments",
    ),
    (
        "save_batch_payments_csv",
        {"data": "agency_number,amount\nAG-1,19.99"},
        {"data": "agency_number,amount\nAG-1,19.99"},
        "/api/v2/commissions/save_batch_payments_csv",
    ),
    (
        "save_payment",
        {"amount": 45.67, "agency_number": "AG-1"},
        {"amount": 45.67, "agency_number": "AG-1"},
        "/api/v2/commissions/save_payment",
    ),
    (
        "update_commission_payments_complete",
        {"commission_payment_ids": ["CP-1"]},
        {"commission_payment_ids": ["CP-1"]},
        "/api/v2/commissions/update_commission_payments_complete",
    ),
]


PAYMENTS_ENDPOINT_CASES = [
    (
        "add_payment_method",
        {
            "card_expires_mm": "04",
            "card_expires_yy": "2030",
            "card_cvv2": "123",
            "card_name_on": "Jane Doe",
            "contact_id": "C-1",
            "card_type": "visa",
            "payment_method_type": "card",
            "card_number": "4111111111111111",
            "address": {"street": "123 Main"},
        },
        {
            "card_expires_mm": "04",
            "card_cvv2": "123",
            "card_name_on": "Jane Doe",
            "contact_id": "C-1",
            "card_type": "visa",
            "card_expires_yy": "2030",
            "type": "card",
            "card_number": "4111111111111111",
            "address": {"street": "123 Main"},
        },
        "/api/v2/payments/add_payment_method",
    ),
    (
        "apply_selected_payments",
        {"payment_ids": [], "print_deposit_receipt": False},
        {"print_deposit_receipt": False, "payment_ids": []},
        "/api/v2/payments/apply_selected_payments",
    ),
    (
        "change_payment_method",
        {
            "auto_payment_method_id": "PM-1",
            "auto_pay_days_before": 7,
            "contact_id": "C-1",
            "policy_list": ["POL-1", "POL-2"],
        },
        {
            "auto_payment_method_id": "PM-1",
            "auto_pay_days_before": 7,
            "contact_id": "C-1",
            "policy_list": ["POL-1", "POL-2"],
        },
        "/api/v2/payments/change_payment_method",
    ),
    (
        "change_payment_method_single",
        {
            "auto_pay_days_before": 3,
            "contact_id": "C-1",
            "policy_term_id": "TERM-1",
            "auto_payment_method_id": "PM-2",
            "override_propagation": False,
            "policy_id": "POL-9",
        },
        {
            "auto_pay_days_before": 3,
            "contact_id": "C-1",
            "policy_term_id": "TERM-1",
            "auto_payment_method_id": "PM-2",
            "override_propagation": False,
            "policy_id": "POL-9",
        },
        "/api/v2/payments/change_payment_method_single",
    ),
    (
        "create_payment_batch",
        {"data": {"name": "batch-1"}},
        {"data": {"name": "batch-1"}},
        "/api/v2/payments/create_payment_batch",
    ),
    (
        "create_payment_entries",
        {"entries": [{"invoice_number": "INV-1", "amount": 25.0}]},
        {"entries": [{"invoice_number": "INV-1", "amount": 25.0}]},
        "/api/v2/payments/create_payment_entries",
    ),
    (
        "delete_payment_batch",
        {"batch_id": "BATCH-1"},
        {"batch_id": "BATCH-1"},
        "/api/v2/payments/delete_payment_batch",
    ),
    (
        "delete_payment_entries",
        {"entry_ids": ["ENTRY-1", "ENTRY-2"]},
        {"entry_ids": ["ENTRY-1", "ENTRY-2"]},
        "/api/v2/payments/delete_payment_entries",
    ),
    (
        "get_payment_method_info",
        {"payment_method_id": "PM-9"},
        {"payment_method_id": "PM-9"},
        "/api/v2/payments/get_payment_method_info",
    ),
    (
        "get_unpaid_invoices_by_date",
        {"due_date": "2026-04-15", "bill_date": "2026-04-01"},
        {"due_date": "2026-04-15", "bill_date": "2026-04-01"},
        "/api/v2/payments/get_unpaid_invoices_by_date",
    ),
    (
        "import_payment_entries",
        {"entry_ids": ["ENTRY-3"], "bypass_duplicates_check": False},
        {"entry_ids": ["ENTRY-3"], "bypass_duplicates_check": False},
        "/api/v2/payments/import_payment_entries",
    ),
    (
        "make_payment_by_contact_and_payment_method",
        {
            "policy_id": "POL-3",
            "payment_amount": 88.0,
            "contact_id": "C-3",
            "payment_method_id": "PM-3",
        },
        {
            "policy_id": "POL-3",
            "payment_amount": 88.0,
            "contact_id": "C-3",
            "payment_method_id": "PM-3",
        },
        "/api/v2/payments/make_payment_by_contact_and_payment_method",
    ),
    (
        "make_payment_by_invoice_or_policy",
        {
            "payment_date": "2026-04-10",
            "policy_number": "POL-4",
            "amount": 91.5,
            "meta": {"source": "portal"},
            "payment_transaction_id": "TX-1",
            "source_id": "SRC-1",
            "invoice_number": "INV-4",
        },
        {
            "payment_date": "2026-04-10",
            "policy_number": "POL-4",
            "amount": 91.5,
            "meta": {"source": "portal"},
            "payment_transaction_id": "TX-1",
            "source_id": "SRC-1",
            "invoice_number": "INV-4",
        },
        "/api/v2/payments/make_payment_by_invoice_or_policy",
    ),
    (
        "mark_payment_nsf",
        {
            "payment_date": "2026-04-11",
            "confirmation_number": "CONF-1",
            "policy_number": "POL-5",
            "amount": 42.25,
            "disable_auto_pay": False,
            "invoice_number": "INV-5",
        },
        {
            "payment_date": "2026-04-11",
            "confirmation_number": "CONF-1",
            "policy_number": "POL-5",
            "amount": 42.25,
            "disable_auto_pay": False,
            "invoice_number": "INV-5",
        },
        "/api/v2/payments/mark_payment_nsf",
    ),
    (
        "remove_payment_method",
        {"payment_method_id": "PM-10"},
        {"payment_method_id": "PM-10"},
        "/api/v2/payments/remove_payment_method",
    ),
    (
        "retrieve_account_payoff_amount",
        {"policy_number": "POL-6"},
        {"policy_number": "POL-6"},
        "/api/v2/payments/retrieve_account_payoff_amount",
    ),
    (
        "retrieve_convenience_fee",
        {"payment_amount": 11.25, "account_type": "checking"},
        {"payment_amount": 11.25, "account_type": "checking"},
        "/api/v2/payments/retrieve_convenience_fee",
    ),
    (
        "retrieve_payment",
        {"payment_id": "PAY-1"},
        {"payment_id": "PAY-1"},
        "/api/v2/payments/retrieve_payment",
    ),
    (
        "retrieve_payment_batch_entries",
        {"batch_id": "BATCH-2"},
        {"batch_id": "BATCH-2"},
        "/api/v2/payments/retrieve_payment_batch_entries",
    ),
    (
        "retrieve_payment_batches",
        {"load_entries": False},
        {"load_entries": False},
        "/api/v2/payments/retrieve_payment_batches",
    ),
    (
        "retrieve_payment_entries",
        {"entry_ids": ["ENTRY-9"]},
        {"entry_ids": ["ENTRY-9"]},
        "/api/v2/payments/retrieve_payment_entries",
    ),
    (
        "retrieve_payment_methods",
        {"contact_ids": ["C-7"], "exp_less_than": "2026-12"},
        {"contact_ids": ["C-7"], "exp_less_than": "2026-12"},
        "/api/v2/payments/retrieve_payment_methods",
    ),
    (
        "retrieve_policy_billing_information",
        {
            "policy_term_id": "TERM-9",
            "billing_only": False,
            "policy_id": "POL-9",
        },
        {
            "policy_term_id": "TERM-9",
            "billing_only": False,
            "policy_id": "POL-9",
        },
        "/api/v2/payments/retrieve_policy_billing_information",
    ),
    (
        "retrieve_sweep_payment_list",
        {"procdate": "2026-04-30"},
        {"procdate": "2026-04-30"},
        "/api/v2/payments/retrieve_sweep_payment_list",
    ),
    (
        "retrieve_updated_invoice_balance",
        {"invoice_id": "INV-8"},
        {"invoice_id": "INV-8"},
        "/api/v2/payments/retrieve_updated_invoice_balance",
    ),
    (
        "update_payment_batch",
        {"batch_id": "BATCH-3", "data": {"status": "ready"}},
        {"batch_id": "BATCH-3", "data": {"status": "ready"}},
        "/api/v2/payments/update_payment_batch",
    ),
    (
        "update_payment_entries",
        {"entries": [{"id": "ENTRY-10", "amount": 30.0}]},
        {"entries": [{"id": "ENTRY-10", "amount": 30.0}]},
        "/api/v2/payments/update_payment_entries",
    ),
    (
        "update_sweep_payments_complete",
        {"procdate": "2026-05-01", "payment_ids": ["PAY-7", "PAY-8"]},
        {"procdate": "2026-05-01", "payment_ids": ["PAY-7", "PAY-8"]},
        "/api/v2/payments/update_sweep_payments_complete",
    ),
]


class TestQuotesEndpoints:
    """Tests for quote-related endpoint wrappers."""

    @pytest.mark.unit
    def test_get_quote_success(self, env_api_key, mock_settings):
        """Test successful quote retrieval."""
        from britecore_sdk.api.api_calls import get_api_client, init_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        mock_response = _make_response(
            b'{"success": true, "data": {"id": "Q123", "amount": 500}}'
        )

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            init_api_client(target_site="test_site")
            client = get_api_client()

            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(
                    client, "process_result", return_value={"id": "Q123", "amount": 500}
                ),
            ):
                result = quotes.get_quote("Q123")

        assert result is not None
        assert result["id"] == "Q123"
        assert result["amount"] == 500

    @pytest.mark.unit
    def test_get_quote_no_response(self, env_api_key, mock_settings):
        """Test quote retrieval when API returns None."""
        from britecore_sdk.api.api_calls import get_api_client, init_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            init_api_client(target_site="test_site")
            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=None),
                patch.object(
                    client,
                    "process_result",
                    side_effect=BritecoreError.NoDataReturned("No response"),
                ),
                pytest.raises(BritecoreError.NoDataReturned),
            ):
                quotes.get_quote("Q123")

    @pytest.mark.unit
    def test_create_full_quote_success(self, env_api_key, mock_settings):
        """Test successful full quote creation."""
        from britecore_sdk.api.api_calls import get_api_client, init_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        quote_json = {"carrier": "ACME", "coverage": "Liability"}
        mock_response = _make_response(
            b'{"success": true, "data": {"id": "Q456", "carrier": "ACME"}}'
        )

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            init_api_client(target_site="test_site")
            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(
                    client,
                    "process_result",
                    return_value={"id": "Q456", "carrier": "ACME"},
                ),
            ):
                result, quote_id = quotes.create_full_quote(quote_json)

        assert result is not None
        assert quote_id == "Q456"
        assert result["carrier"] == "ACME"

    @pytest.mark.unit
    def test_create_full_quote_no_data(self, env_api_key, mock_settings):
        """Test create_full_quote when API returns no data."""
        from britecore_sdk.api.api_calls import get_api_client, init_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        quote_json = {"carrier": "ACME"}

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            init_api_client(target_site="test_site")
            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=None),
                patch.object(client, "process_result", return_value=None),
            ):
                result, quote_id = quotes.create_full_quote(quote_json)

        assert result is None
        assert quote_id is None

    @pytest.mark.unit
    def test_create_full_quote_returns_tuple(self, env_api_key, mock_settings):
        """Test create_full_quote returns a tuple of (data, id)."""
        from britecore_sdk.api.api_calls import get_api_client, init_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        quote_json = {"carrier": "ACME"}
        mock_response = _make_response(b'{"success": true, "data": {"id": "Q789"}}')

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            init_api_client(target_site="test_site")
            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(client, "process_result", return_value={"id": "Q789"}),
            ):
                result = quotes.create_full_quote(quote_json)

        assert isinstance(result, tuple)
        assert len(result) == 2


class TestPoliciesEndpoints:
    """Tests for policy-related endpoint wrappers."""

    @pytest.mark.unit
    def test_retrieve_policy_by_number(self, env_api_key, mock_settings):
        """Test policy retrieval by policy number."""
        from britecore_sdk.api.api_calls import get_api_client
        from britecore_sdk.api.api_calls.v2 import policies

        mock_response = _make_response(
            b'{"success": true, "data": {"id": "P123", "policy_number": "POL001"}}'
        )

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(
                    client,
                    "process_result",
                    return_value={"id": "P123", "policy_number": "POL001"},
                ),
            ):
                result = policies.retrieve_policy(policy_number="POL001")

        assert result is not None
        assert result["policy_number"] == "POL001"

    @pytest.mark.unit
    def test_retrieve_policy_by_id(self, env_api_key, mock_settings):
        """Test policy retrieval by policy ID."""
        from britecore_sdk.api.api_calls import get_api_client
        from britecore_sdk.api.api_calls.v2 import policies

        mock_response = _make_response(
            b'{"success": true, "data": {"id": "P456", "policy_number": "POL002"}}'
        )

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(
                    client,
                    "process_result",
                    return_value={"id": "P456", "policy_number": "POL002"},
                ),
            ):
                result = policies.retrieve_policy(policy_id="P456")

        assert result is not None
        assert result["id"] == "P456"

    @pytest.mark.unit
    def test_add_line_item_success(self, env_api_key, mock_settings):
        """Test successful line item addition."""
        from britecore_sdk.api.api_calls import get_api_client
        from britecore_sdk.api.api_calls.v2 import policies

        mock_response = _make_response(
            b'{"success": true, "data": {"added_items": ["item1"]}}'
        )

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(
                    client, "process_result", return_value={"added_items": ["item1"]}
                ),
            ):
                result = policies.add_line_item(revision_id="REV123", item_id="ITEM456")

        assert result is True


class TestContactsEndpoints:
    """Tests for contact-related endpoint wrappers."""

    @pytest.mark.unit
    def test_get_contact_success(self, env_api_key, mock_settings):
        """Test successful contact retrieval."""
        from britecore_sdk.api.api_calls import get_api_client
        from britecore_sdk.api.api_calls.v2 import contacts

        mock_response = _make_response(
            b'{"success": true, "data": {"id": "C123", "name": "John Doe"}}'
        )

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(
                    client,
                    "process_result",
                    return_value={"id": "C123", "name": "John Doe"},
                ),
            ):
                result = contacts.get_contact("C123")

        assert result is not None
        assert result["name"] == "John Doe"

    @pytest.mark.unit
    def test_new_contact_success(self, env_api_key, mock_settings):
        """Test successful new contact creation.

        new_contact() calls process_result() which returns contact_json,
        then extracts contact_json.get("contact_id") as the ID.
        It returns (contact_json, contact_id).
        """
        from britecore_sdk.api.api_calls import get_api_client
        from britecore_sdk.api.api_calls.v2 import contacts

        contact_data = {"contact_id": "C456", "name": "Jane Smith"}
        mock_response = _make_response(
            b'{"success": true, "data": {"contact_id": "C456", "name": "Jane Smith"}}'
        )

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(client, "process_result", return_value=contact_data),
            ):
                result, contact_id = contacts.new_contact(
                    name="Jane Smith",
                    address=[
                        {
                            "street": "123 Main",
                            "city": "Anytown",
                            "state": "CA",
                            "zip": "12345",
                        }
                    ],
                )

        assert result is not None
        assert isinstance(result, dict)
        assert result["contact_id"] == "C456"
        assert contact_id == "C456"


class TestBillingEndpoints:
    """Tests for billing-related endpoint wrappers."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        BILLING_ENDPOINT_CASES,
    )
    def test_billing_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        module = importlib.import_module("britecore_sdk.api.api_calls.v2.billing")
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


class TestAccountingEndpoints:
    """Tests for accounting-related endpoint wrappers."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        ACCOUNTING_ENDPOINT_CASES,
    )
    def test_accounting_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        module = importlib.import_module("britecore_sdk.api.api_calls.v2.accounting")
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


class TestCommissionsEndpoints:
    """Tests for commission-related endpoint wrappers."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        COMMISSIONS_ENDPOINT_CASES,
    )
    def test_commissions_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        module = importlib.import_module("britecore_sdk.api.api_calls.v2.commissions")
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


class TestClaimsEndpoints:
    """Tests for claims-related endpoint wrappers."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        CLAIMS_ENDPOINT_CASES,
    )
    def test_claims_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        module = importlib.import_module("britecore_sdk.api.api_calls.v2.claims")
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


class TestPaymentsEndpoints:
    """Tests for payment-related endpoint wrappers."""

    @pytest.mark.unit
    @pytest.mark.parametrize(
        ("function_name", "call_kwargs", "expected_json", "expected_path"),
        PAYMENTS_ENDPOINT_CASES,
    )
    def test_payments_wrapper_requests(
        self,
        env_api_key,
        mock_settings,
        function_name,
        call_kwargs,
        expected_json,
        expected_path,
    ):
        module = importlib.import_module("britecore_sdk.api.api_calls.v2.payments")
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


class TestEndpointErrorHandling:
    """Tests for error handling across endpoints."""

    @pytest.mark.unit
    def test_endpoint_handles_api_error_response(self, env_api_key, mock_settings):
        """Test that endpoints handle API error responses correctly."""
        from britecore_sdk.api.api_calls import get_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        mock_response = _make_response(
            b'{"success": false, "message": "API Error"}', status=200
        )

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(
                    client,
                    "process_result",
                    side_effect=BritecoreError.NoDataReturned("API Error"),
                ),
                pytest.raises(BritecoreError.NoDataReturned),
            ):
                quotes.get_quote("Q123")

    @pytest.mark.unit
    def test_endpoint_handles_http_500(self, env_api_key, mock_settings):
        """Test that endpoints handle HTTP 500 errors."""
        from britecore_sdk.api.api_calls import get_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        mock_response = _make_response(
            b'{"success": false, "message": "Internal Server Error"}', status=500
        )

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = get_api_client()
            with (
                patch.object(client, "do_request", return_value=mock_response),
                patch.object(
                    client,
                    "process_result",
                    side_effect=BritecoreError.NoDataReturned("Error - 500"),
                ),
                pytest.raises(BritecoreError.NoDataReturned),
            ):
                quotes.get_quote("Q123")

    @pytest.mark.unit
    def test_endpoint_handles_connection_error(self, env_api_key, mock_settings):
        """Test that endpoints handle connection errors."""
        from britecore_sdk.api.api_calls import get_api_client
        from britecore_sdk.api.api_calls.v2 import quotes

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = get_api_client()
            with (
                patch.object(
                    client,
                    "do_request",
                    side_effect=BritecoreError.NoDataReturned("Connection error"),
                ),
                pytest.raises(BritecoreError.NoDataReturned),
            ):
                quotes.get_quote("Q123")


__all__ = [
    "TestQuotesEndpoints",
    "TestPoliciesEndpoints",
    "TestContactsEndpoints",
    "TestAccountingEndpoints",
    "TestBillingEndpoints",
    "TestCommissionsEndpoints",
    "TestClaimsEndpoints",
    "TestPaymentsEndpoints",
    "TestEndpointErrorHandling",
]
