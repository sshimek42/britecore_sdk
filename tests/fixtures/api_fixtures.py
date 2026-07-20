"""Test fixtures for BriteCore SDK testing.

Provides reusable fixtures for mocking API responses and client behavior.
"""

import pytest
from unittest.mock import MagicMock, Mock, patch
from typing import Any, Generator

from britecore_sdk.api.britecore_api_client import BritecoreAPIClient


@pytest.fixture
def mock_policy_response() -> dict[str, Any]:
    """Standard policy response for testing.

    Returns a typical successful API response for a policy.
    """
    return {
        "success": True,
        "data": {
            "policy_id": "12345",
            "policy_number": "POL-123-456",
            "status": "active",
            "account_id": "acct_001",
            "inception_date": "2024-01-01",
            "expiration_date": "2025-01-01",
            "type_code": "HO",
            "premium": 1250.00,
            "company_id": "comp_001",
        },
        "message": "Policy retrieved successfully"
    }


@pytest.fixture
def mock_contact_response() -> dict[str, Any]:
    """Standard contact response for testing.

    Returns a typical successful API response for a contact.
    """
    return {
        "success": True,
        "data": {
            "contact_id": "con_001",
            "name": "John Doe",
            "contact_type": "individual",
            "email": [{"email": "john@example.com", "email_type": "work"}],
            "phone": [{"phone": "555-1234", "phone_type": "work"}],
            "address": [{"address": "123 Main St", "city": "Anytown", "state": "CA", "zip": "12345"}],
        },
        "message": "Contact retrieved successfully"
    }


@pytest.fixture
def mock_quote_response() -> dict[str, Any]:
    """Standard quote response for testing.

    Returns a typical successful API response for a quote.
    """
    return {
        "success": True,
        "data": {
            "quote_id": "quote_001",
            "policy_number": "POL-123-456",
            "status": "pending",
            "total_premium": 1250.00,
            "effective_date": "2024-02-01",
            "expiration_date": "2024-05-01",
            "line_items": [
                {
                    "line_id": 1,
                    "coverage": "dwelling",
                    "premium": 800.00,
                }
            ],
        },
        "message": "Quote created successfully"
    }


@pytest.fixture
def mock_error_response() -> dict[str, Any]:
    """Standard error response for testing.

    Returns a typical error API response.
    """
    return {
        "success": False,
        "message": "The resource was not found",
        "messages": ["Policy not found"],
    }


@pytest.fixture
def mock_rate_limit_response() -> dict[str, Any]:
    """Rate limit error response for testing.

    Simulates a rate limit (429) error response.
    """
    return {
        "success": False,
        "message": "Too many requests. Rate limit exceeded.",
        "messages": ["Rate limit exceeded. Retry-After: 60"],
    }


@pytest.fixture
def mock_api_client() -> Generator[MagicMock, None, None]:
    """Pre-configured mock API client for testing.

    Automatically mocks common methods and returns realistic responses.

    Yields:
        A MagicMock configured as an API client.
    """
    client = MagicMock(spec=BritecoreAPIClient)
    client.do_request = MagicMock()
    client.process_result = MagicMock()
    client.base_url = "https://api.example.com"
    client.api_key = "test_key_123"
    client.target_site = "test"
    client.client_dry_run = False

    yield client


@pytest.fixture
def mock_api_client_with_policy(mock_api_client, mock_policy_response) -> MagicMock:
    """Mock API client pre-configured to return a policy response."""
    mock_api_client.do_request.return_value = mock_policy_response
    mock_api_client.process_result.return_value = mock_policy_response
    return mock_api_client


@pytest.fixture
def mock_api_client_with_contact(mock_api_client, mock_contact_response) -> MagicMock:
    """Mock API client pre-configured to return a contact response."""
    mock_api_client.do_request.return_value = mock_contact_response
    mock_api_client.process_result.return_value = mock_contact_response
    return mock_api_client


@pytest.fixture
def mock_api_client_with_quote(mock_api_client, mock_quote_response) -> MagicMock:
    """Mock API client pre-configured to return a quote response."""
    mock_api_client.do_request.return_value = mock_quote_response
    mock_api_client.process_result.return_value = mock_quote_response
    return mock_api_client


@pytest.fixture
def mock_rate_limit_scenario(mock_api_client, mock_rate_limit_response) -> MagicMock:
    """Mock API client configured to simulate rate limit conditions.

    Pre-configured to return rate limit errors.
    """
    mock_api_client.do_request.return_value = mock_rate_limit_response
    mock_api_client.process_result.return_value = mock_rate_limit_response
    return mock_api_client


@pytest.fixture
def mock_error_scenario(mock_api_client, mock_error_response) -> MagicMock:
    """Mock API client configured to simulate error conditions."""
    mock_api_client.do_request.return_value = mock_error_response
    mock_api_client.process_result.return_value = mock_error_response
    return mock_api_client


@pytest.fixture
def patched_get_api_client(mock_api_client) -> Generator[Mock, None, None]:
    """Patch get_api_client to return a mock client.

    Useful for testing functions that use get_api_client internally.

    Yields:
        A mock for get_api_client.
    """
    with patch("britecore_sdk.api.api_calls.get_api_client") as mock_get:
        mock_get.return_value = mock_api_client
        yield mock_get


@pytest.fixture
def patched_init_api_client(mock_api_client) -> Generator[Mock, None, None]:
    """Patch init_api_client to return a mock client.

    Yields:
        A mock for init_api_client.
    """
    with patch("britecore_sdk.api.api_calls.init_api_client") as mock_init:
        mock_init.return_value = mock_api_client
        yield mock_init


@pytest.fixture
def sample_policy_data() -> dict[str, Any]:
    """Sample policy data for creating policies in tests."""
    return {
        "policy_number": "TEST-POL-001",
        "inception_date": "2024-01-01",
        "expiration_date": "2024-12-31",
        "type_code": "HO",
        "account_id": "test_account_001",
        "company_id": "test_company_001",
    }


@pytest.fixture
def sample_contact_data() -> dict[str, Any]:
    """Sample contact data for creating contacts in tests."""
    return {
        "name": "John Doe",
        "contact_type": "individual",
        "email": [{"email": "john@example.com", "email_type": "work"}],
        "phone": [{"phone": "555-1234", "phone_type": "work"}],
        "address": [
            {
                "address": "123 Main St",
                "address_type": "mailing",
                "city": "Anytown",
                "state": "CA",
                "zip": "12345",
            }
        ],
    }


@pytest.fixture
def sample_quote_data() -> dict[str, Any]:
    """Sample quote data for creating quotes in tests."""
    return {
        "policy_number": "TEST-POL-001",
        "effective_date": "2024-02-01",
        "expiration_date": "2024-05-01",
        "line_items": [
            {
                "line_id": 1,
                "coverage": "dwelling",
                "premium": 800.00,
            }
        ],
    }


__all__ = [
    "mock_policy_response",
    "mock_contact_response",
    "mock_quote_response",
    "mock_error_response",
    "mock_rate_limit_response",
    "mock_api_client",
    "mock_api_client_with_policy",
    "mock_api_client_with_contact",
    "mock_api_client_with_quote",
    "mock_rate_limit_scenario",
    "mock_error_scenario",
    "patched_get_api_client",
    "patched_init_api_client",
    "sample_policy_data",
    "sample_contact_data",
    "sample_quote_data",
]

