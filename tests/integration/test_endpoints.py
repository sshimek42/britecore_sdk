"""Integration tests for API endpoint wrappers."""

from unittest.mock import MagicMock, patch

import pytest


class TestQuotesEndpoints:
    """Tests for quotes endpoint wrappers."""

    @pytest.mark.integration
    def test_create_full_quote(self, mock_http_response):
        """Test create_full_quote endpoint."""
        with patch("britecore_libraries.api.api_calls.v2.quotes.API_CLIENT") as mock_client:
            mock_client.do_request.return_value = mock_http_response
            mock_client.process_result.return_value = {"id": "quote_123", "number": "Q001"}
            
            from britecore_libraries.api.api_calls.v2.quotes import create_full_quote
            
            quote_data = {"number": "Q001", "policy_type_id": "type_1"}
            result, quote_id = create_full_quote(quote_data)
            
            assert result is not None
            assert quote_id == "quote_123"
            mock_client.do_request.assert_called_once()

    @pytest.mark.integration
    def test_get_quote(self, mock_http_response):
        """Test get_quote endpoint."""
        with patch("britecore_libraries.api.api_calls.v2.quotes.API_CLIENT") as mock_client:
            mock_client.do_request.return_value = mock_http_response
            mock_client.process_result.return_value = {"id": "quote_123", "number": "Q001"}
            
            from britecore_libraries.api.api_calls.v2.quotes import get_quote
            
            result = get_quote("quote_123")
            
            assert result is not None
            assert result["id"] == "quote_123"
            mock_client.do_request.assert_called_once()


class TestPoliciesEndpoints:
    """Tests for policies endpoint wrappers."""

    @pytest.mark.integration
    def test_retrieve_policy_by_number(self, mock_http_response):
        """Test retrieve_policy with policy number."""
        with patch("britecore_libraries.api.api_calls.v2.policies.API_CLIENT") as mock_client:
            mock_client.do_request.return_value = mock_http_response
            mock_client.process_result.return_value = {
                "id": "policy_123",
                "policy_number": "POL001",
            }
            mock_client.multiple_parameter_verification.return_value = {
                "policy_number": "POL001"
            }
            
            from britecore_libraries.api.api_calls.v2.policies import retrieve_policy
            
            result = retrieve_policy(policy_number="POL001")
            
            assert result is not None
            assert result["policy_number"] == "POL001"

    @pytest.mark.integration
    def test_retrieve_policy_by_id(self, mock_http_response):
        """Test retrieve_policy with policy ID."""
        with patch("britecore_libraries.api.api_calls.v2.policies.API_CLIENT") as mock_client:
            mock_client.do_request.return_value = mock_http_response
            mock_client.process_result.return_value = {"id": "policy_123"}
            mock_client.multiple_parameter_verification.return_value = {
                "policy_id": "policy_123"
            }
            
            from britecore_libraries.api.api_calls.v2.policies import retrieve_policy
            
            result = retrieve_policy(policy_id="policy_123")
            
            assert result is not None

    @pytest.mark.integration
    def test_add_line_item(self, mock_http_response):
        """Test add_line_item endpoint."""
        response_with_items = MagicMock()
        response_with_items.status = 200
        response_with_items.data = b'{"success": true, "data": {"added_items": ["item_1"]}, "message": "OK"}'
        
        with patch("britecore_libraries.api.api_calls.v2.policies.API_CLIENT") as mock_client:
            mock_client.do_request.return_value = response_with_items
            mock_client.process_result.return_value = {"added_items": ["item_1"]}
            mock_client.json_dict_builder.return_value = {
                "revision_id": "rev_123",
                "item_id": "item_1",
            }
            
            from britecore_libraries.api.api_calls.v2.policies import add_line_item
            
            result = add_line_item("rev_123", "item_1")
            
            assert result is True

    @pytest.mark.integration
    def test_retrieve_policy_ids(self, mock_http_response):
        """Test retrieve_policy_ids helper."""
        with patch("britecore_libraries.api.api_calls.v2.policies.retrieve_policy") as mock_retrieve:
            mock_retrieve.return_value = {
                "active_revision": {
                    "id": "rev_123",
                    "primary_property_id": "prop_123",
                }
            }
            
            from britecore_libraries.api.api_calls.v2.policies import retrieve_policy_ids
            
            revision_id, property_id = retrieve_policy_ids("POL001")
            
            assert revision_id == "rev_123"
            assert property_id == "prop_123"


class TestContactsEndpoints:
    """Tests for contacts endpoint wrappers (v1)."""

    @pytest.mark.integration
    def test_retrieve_contact_list(self, mock_http_response):
        """Test retrieve_contact_list endpoint."""
        with patch("britecore_libraries.api.api_calls.v1.contacts.API_CLIENT") as mock_client:
            mock_response = MagicMock()
            mock_response.data = b'{"records": [{"id": "c1", "name": "John"}]}'
            
            mock_client.do_request.return_value = mock_response
            
            from britecore_libraries.api.api_calls.v1.contacts import retrieve_contact_list
            
            result = retrieve_contact_list("John")
            
            assert result is not None
            mock_client.do_request.assert_called_once()

