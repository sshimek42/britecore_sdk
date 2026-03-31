"""Unit tests for v2 endpoint wrappers.

This module provides comprehensive test coverage for BriteCore API v2 endpoint
wrapper functions, covering happy path and error scenarios.
"""
import json
from unittest.mock import MagicMock, patch
import pytest
from urllib3 import BaseHTTPResponse

from britecore_libraries.exceptions import BritecoreError


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


class TestQuotesEndpoints:
    """Tests for quote-related endpoint wrappers."""

    @pytest.mark.unit
    def test_get_quote_success(self, env_api_key, mock_settings):
        """Test successful quote retrieval."""
        from britecore_libraries.api.api_calls.v2 import quotes
        from britecore_libraries.api.api_calls import get_api_client
        
        mock_response = _make_response(b'{"success": true, "data": {"id": "Q123", "amount": 500}}')
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", return_value={"id": "Q123", "amount": 500}):
                    result = quotes.get_quote("Q123")
        
        assert result is not None
        assert result["id"] == "Q123"
        assert result["amount"] == 500

    @pytest.mark.unit
    def test_get_quote_no_response(self, env_api_key, mock_settings):
        """Test quote retrieval when API returns None."""
        from britecore_libraries.api.api_calls.v2 import quotes
        from britecore_libraries.api.api_calls import get_api_client
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=None):
                with patch.object(client, "process_result", side_effect=BritecoreError.NoDataReturned("No response")):
                    with pytest.raises(BritecoreError.NoDataReturned):
                        quotes.get_quote("Q123")

    @pytest.mark.unit
    def test_create_full_quote_success(self, env_api_key, mock_settings):
        """Test successful full quote creation."""
        from britecore_libraries.api.api_calls.v2 import quotes
        from britecore_libraries.api.api_calls import get_api_client
        
        quote_json = {"carrier": "ACME", "coverage": "Liability"}
        mock_response = _make_response(b'{"success": true, "data": {"id": "Q456", "carrier": "ACME"}}')
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", return_value={"id": "Q456", "carrier": "ACME"}):
                    result, quote_id = quotes.create_full_quote(quote_json)
        
        assert result is not None
        assert quote_id == "Q456"
        assert result["carrier"] == "ACME"

    @pytest.mark.unit
    def test_create_full_quote_no_data(self, env_api_key, mock_settings):
        """Test create_full_quote when API returns no data."""
        from britecore_libraries.api.api_calls.v2 import quotes
        from britecore_libraries.api.api_calls import get_api_client
        
        quote_json = {"carrier": "ACME"}
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=None):
                with patch.object(client, "process_result", return_value=None):
                    result, quote_id = quotes.create_full_quote(quote_json)
        
        assert result is None
        assert quote_id is None

    @pytest.mark.unit
    def test_create_full_quote_returns_tuple(self, env_api_key, mock_settings):
        """Test create_full_quote returns a tuple of (data, id)."""
        from britecore_libraries.api.api_calls.v2 import quotes
        from britecore_libraries.api.api_calls import get_api_client
        
        quote_json = {"carrier": "ACME"}
        mock_response = _make_response(b'{"success": true, "data": {"id": "Q789"}}')
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", return_value={"id": "Q789"}):
                    result = quotes.create_full_quote(quote_json)
        
        assert isinstance(result, tuple)
        assert len(result) == 2


class TestPoliciesEndpoints:
    """Tests for policy-related endpoint wrappers."""

    @pytest.mark.unit
    def test_retrieve_policy_by_number(self, env_api_key, mock_settings):
        """Test policy retrieval by policy number."""
        from britecore_libraries.api.api_calls.v2 import policies
        from britecore_libraries.api.api_calls import get_api_client
        
        mock_response = _make_response(b'{"success": true, "data": {"id": "P123", "policy_number": "POL001"}}')
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", return_value={"id": "P123", "policy_number": "POL001"}):
                    result = policies.retrieve_policy(policy_number="POL001")
        
        assert result is not None
        assert result["policy_number"] == "POL001"

    @pytest.mark.unit
    def test_retrieve_policy_by_id(self, env_api_key, mock_settings):
        """Test policy retrieval by policy ID."""
        from britecore_libraries.api.api_calls.v2 import policies
        from britecore_libraries.api.api_calls import get_api_client
        
        mock_response = _make_response(b'{"success": true, "data": {"id": "P456", "policy_number": "POL002"}}')
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", return_value={"id": "P456", "policy_number": "POL002"}):
                    result = policies.retrieve_policy(policy_id="P456")
        
        assert result is not None
        assert result["id"] == "P456"

    @pytest.mark.unit
    def test_add_line_item_success(self, env_api_key, mock_settings):
        """Test successful line item addition."""
        from britecore_libraries.api.api_calls.v2 import policies
        from britecore_libraries.api.api_calls import get_api_client
        
        mock_response = _make_response(b'{"success": true, "data": {"added_items": ["item1"]}}')
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", return_value={"added_items": ["item1"]}):
                    result = policies.add_line_item(revision_id="REV123", item_id="ITEM456")
        
        assert result is True


class TestContactsEndpoints:
    """Tests for contact-related endpoint wrappers."""

    @pytest.mark.unit
    def test_get_contact_success(self, env_api_key, mock_settings):
        """Test successful contact retrieval."""
        from britecore_libraries.api.api_calls.v2 import contacts
        from britecore_libraries.api.api_calls import get_api_client
        
        mock_response = _make_response(b'{"success": true, "data": {"id": "C123", "name": "John Doe"}}')
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", return_value={"id": "C123", "name": "John Doe"}):
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
        from britecore_libraries.api.api_calls.v2 import contacts
        from britecore_libraries.api.api_calls import get_api_client

        contact_data = {"contact_id": "C456", "name": "Jane Smith"}
        mock_response = _make_response(
            b'{"success": true, "data": {"contact_id": "C456", "name": "Jane Smith"}}'
        )

        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", return_value=contact_data):
                    result, contact_id = contacts.new_contact(
                        name="Jane Smith",
                        address=[{"street": "123 Main", "city": "Anytown", "state": "CA", "zip": "12345"}],
                    )

        assert result is not None
        assert result["contact_id"] == "C456"
        assert contact_id == "C456"


class TestEndpointErrorHandling:
    """Tests for error handling across endpoints."""

    @pytest.mark.unit
    def test_endpoint_handles_api_error_response(self, env_api_key, mock_settings):
        """Test that endpoints handle API error responses correctly."""
        from britecore_libraries.api.api_calls.v2 import quotes
        from britecore_libraries.api.api_calls import get_api_client
        
        mock_response = _make_response(
            b'{"success": false, "message": "API Error"}',
            status=200
        )
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", side_effect=BritecoreError.NoDataReturned("API Error")):
                    with pytest.raises(BritecoreError.NoDataReturned):
                        quotes.get_quote("Q123")

    @pytest.mark.unit
    def test_endpoint_handles_http_500(self, env_api_key, mock_settings):
        """Test that endpoints handle HTTP 500 errors."""
        from britecore_libraries.api.api_calls.v2 import quotes
        from britecore_libraries.api.api_calls import get_api_client
        
        mock_response = _make_response(
            b'{"success": false, "message": "Internal Server Error"}',
            status=500
        )
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", return_value=mock_response):
                with patch.object(client, "process_result", side_effect=BritecoreError.NoDataReturned("Error - 500")):
                    with pytest.raises(BritecoreError.NoDataReturned):
                        quotes.get_quote("Q123")

    @pytest.mark.unit
    def test_endpoint_handles_connection_error(self, env_api_key, mock_settings):
        """Test that endpoints handle connection errors."""
        from britecore_libraries.api.api_calls.v2 import quotes
        from britecore_libraries.api.api_calls import get_api_client
        
        with patch("britecore_libraries.api.britecore_api_client.LoadClientSettings") as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            
            client = get_api_client()
            with patch.object(client, "do_request", side_effect=BritecoreError.NoDataReturned("Connection error")):
                with pytest.raises(BritecoreError.NoDataReturned):
                    quotes.get_quote("Q123")


__all__ = ["TestQuotesEndpoints", "TestPoliciesEndpoints", "TestContactsEndpoints", "TestEndpointErrorHandling"]

