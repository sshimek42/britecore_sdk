"""Unit tests for async v2 API wrapper modules."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from urllib3.util import Timeout


class TestAsyncQuotesEndpoints:
    """Tests for async quote wrappers."""

    @pytest.mark.unit
    def test_aget_quote_applies_cache_defaults(self):
        """Quote reads should enable short-lived cache defaults."""
        response = MagicMock()
        with patch(
            "britecore_sdk.api.api_calls.v2.async_quotes.API_CLIENT"
        ) as mock_client:
            mock_client.ado_request = AsyncMock(return_value=response)
            mock_client.aprocess_result = AsyncMock(return_value={"id": "quote_123"})

            from britecore_sdk.api.api_calls.v2.async_quotes import aget_quote

            result = asyncio.run(aget_quote("quote_123"))

        assert result["id"] == "quote_123"
        mock_client.ado_request.assert_awaited_once()
        call = mock_client.ado_request.await_args
        assert call.kwargs["path"] == "/api/v2/quotes/get_quote"
        assert call.kwargs["json"] == {"id": "quote_123"}
        assert call.kwargs["cache_enabled"] is True
        assert call.kwargs["cache_namespace"] == "quotes"
        assert call.kwargs["cache_ttl_seconds"] == 60
        assert call.kwargs["cache_key_parts"] == ["quote:quote_123"]

    @pytest.mark.unit
    def test_acreate_full_quote_invalidates_quote_cache(self):
        """Quote creation should invalidate cached quote reads."""
        response = MagicMock()
        with patch(
            "britecore_sdk.api.api_calls.v2.async_quotes.API_CLIENT"
        ) as mock_client:
            mock_client.ado_request = AsyncMock(return_value=response)
            mock_client.aprocess_result = AsyncMock(
                return_value={"id": "quote_123", "number": "Q001"}
            )

            from britecore_sdk.api.api_calls.v2.async_quotes import (
                acreate_full_quote,
            )

            quote_json, quote_id = asyncio.run(
                acreate_full_quote({"number": "Q001", "policy_type_id": "type_1"})
            )

        assert quote_id == "quote_123"
        assert quote_json is not None
        assert mock_client.ado_request.await_args.kwargs[
            "cache_invalidate_on_success"
        ] == ["quotes"]


class TestAsyncContactsEndpoints:
    """Tests for async contact wrappers."""

    @pytest.mark.unit
    def test_aget_contact_applies_cache_defaults(self):
        """Contact reads should enable short-lived cache defaults."""
        response = MagicMock()
        with patch(
            "britecore_sdk.api.api_calls.v2.async_contacts.API_CLIENT"
        ) as mock_client:
            mock_client.ado_request = AsyncMock(return_value=response)
            mock_client.aprocess_result = AsyncMock(
                return_value={"contact_id": "c_123"}
            )

            from britecore_sdk.api.api_calls.v2.async_contacts import aget_contact

            result = asyncio.run(aget_contact("c_123"))

        assert result["contact_id"] == "c_123"
        call = mock_client.ado_request.await_args
        assert call.kwargs["path"] == "/api/v2/contacts/get_contact"
        assert call.kwargs["cache_enabled"] is True
        assert call.kwargs["cache_namespace"] == "contacts"
        assert call.kwargs["cache_key_parts"] == ["contact:c_123"]

    @pytest.mark.unit
    def test_anew_contact_invalidates_contact_cache(self):
        """Contact creation should invalidate cached contact reads."""
        response = MagicMock()
        with patch(
            "britecore_sdk.api.api_calls.v2.async_contacts.API_CLIENT"
        ) as mock_client:
            mock_client.ado_request = AsyncMock(return_value=response)
            mock_client.aprocess_result = AsyncMock(
                return_value={"contact_id": "c_123", "name": "Jane Doe"}
            )

            from britecore_sdk.api.api_calls.v2.async_contacts import anew_contact

            contact_json, contact_id = asyncio.run(
                anew_contact(
                    "Jane Doe",
                    [{"address_line1": "1 Main St", "address_city": "Madison"}],
                )
            )

        assert contact_id == "c_123"
        assert contact_json is not None
        assert mock_client.ado_request.await_args.kwargs[
            "cache_invalidate_on_success"
        ] == ["contacts"]


class TestAsyncPoliciesEndpoints:
    """Tests for async policy wrappers."""

    @pytest.mark.unit
    def test_aretrieve_policy_applies_long_timeout_and_cache_defaults(self):
        """Policy retrieval should use long timeout and cache defaults when omitted."""
        response = MagicMock()
        mock_sync_client = MagicMock()
        mock_sync_client.web_timeout_long = 99
        mock_sync_client.multiple_parameter_verification.return_value = {
            "policy_id": "policy_123"
        }

        with patch(
            "britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT"
        ) as mock_client:
            mock_client.aget_client = AsyncMock(return_value=mock_sync_client)
            mock_client.ado_request = AsyncMock(return_value=response)
            mock_client.aprocess_result = AsyncMock(return_value={"id": "policy_123"})

            from britecore_sdk.api.api_calls.v2.async_policies import (
                aretrieve_policy,
            )

            result = asyncio.run(aretrieve_policy(policy_id="policy_123"))

        assert result["id"] == "policy_123"
        mock_sync_client.multiple_parameter_verification.assert_called_once_with(
            [{"policy_number": None}, {"policy_id": "policy_123"}],
            ["policy_id", "policy_number"],
        )
        call = mock_client.ado_request.await_args
        assert call.kwargs["path"] == "/api/v2/policies/retrieve_policy"
        assert call.kwargs["cache_enabled"] is True
        assert call.kwargs["cache_namespace"] == "policies"
        assert call.kwargs["cache_key_parts"] == ["policy_id:policy_123"]
        assert isinstance(call.kwargs["request_timeout"], Timeout)

    @pytest.mark.unit
    def test_acreate_policy_invalidates_policy_cache(self):
        """Policy creation should invalidate cached policy reads."""
        response = MagicMock()
        with patch(
            "britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT"
        ) as mock_client:
            mock_client.ado_request = AsyncMock(return_value=response)
            mock_client.aprocess_result = AsyncMock(
                return_value={"revision_id": "rev_123", "policy_id": "policy_123"}
            )

            from britecore_sdk.api.api_calls.v2.async_policies import (
                acreate_policy,
            )

            policy_json, revision_id = asyncio.run(
                acreate_policy(policy_number="POL001", policy_type_id="type_1")
            )

        assert revision_id == "rev_123"
        assert policy_json["policy_id"] == "policy_123"
        assert mock_client.ado_request.await_args.kwargs[
            "cache_invalidate_on_success"
        ] == ["policies"]

    @pytest.mark.unit
    def test_aretrieve_policy_snapshot_applies_cache_defaults(self):
        """Policy snapshot retrieval should use cache defaults and stable key parts."""
        response = MagicMock()
        with patch(
            "britecore_sdk.api.api_calls.v2.async_policies.API_CLIENT"
        ) as mock_client:
            mock_client.ado_request = AsyncMock(return_value=response)
            mock_client.aprocess_result = AsyncMock(return_value={"snapshot": True})

            from britecore_sdk.api.api_calls.v2.async_policies import (
                aretrieve_policy_snapshot,
            )

            result = asyncio.run(aretrieve_policy_snapshot("POL001", "2026-01-01"))

        assert result["snapshot"] is True
        call = mock_client.ado_request.await_args
        assert call.kwargs["cache_enabled"] is True
        assert call.kwargs["cache_namespace"] == "policies"
        assert call.kwargs["cache_key_parts"] == [
            "policy_number:POL001",
            "snapshot_date:2026-01-01",
            "snapshot",
        ]


class TestAsyncV2Exports:
    """Tests for async v2 package exports."""

    @pytest.mark.unit
    def test_async_v2_exports_are_available(self):
        """The new async wrapper functions should be exported from the v2 package."""
        from britecore_sdk.api.api_calls.v2 import (
            acreate_full_quote,
            acreate_policy,
            aget_contact,
            aget_quote,
            aretrieve_policy,
        )

        assert aget_quote is not None
        assert acreate_full_quote is not None
        assert aget_contact is not None
        assert aretrieve_policy is not None
        assert acreate_policy is not None
