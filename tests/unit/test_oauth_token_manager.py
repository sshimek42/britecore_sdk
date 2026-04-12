"""Unit tests for OAuth token manager."""

from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

from britecore_sdk.api.britecore_oauth_token_manager import OAuthToken
from britecore_sdk.exceptions import BritecoreError


class TestOAuthTokenInit:
    """Tests for OAuthToken initialization."""

    @pytest.mark.unit
    def test_init_with_full_url(self):
        """Test OAuthToken initialization with full URL."""
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")

        assert token.client_id == "client_id"
        assert token.client_secret == "client_secret"
        assert "https://api.example.com" in token.url
        assert "/api/auth/oauth2/token" in token.url

    @pytest.mark.unit
    def test_init_with_bare_host(self):
        """Test OAuthToken initialization with bare host."""
        token = OAuthToken("client_id", "client_secret", "api.example.com")

        assert token.client_id == "client_id"
        assert "api.example.com" in token.url

    @pytest.mark.unit
    def test_init_defaults(self):
        """Test OAuthToken default values."""
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")

        assert token.token == ""
        assert token.token_time == datetime(1970, 1, 1)


class TestOAuthTokenExpiration:
    """Tests for token expiration logic."""

    @pytest.mark.unit
    def test_is_token_expired_with_empty_token(self):
        """Test token expiration check with empty token."""
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")

        assert token._is_token_expired()

    @pytest.mark.unit
    def test_is_token_expired_with_past_time(self):
        """Test token expiration check with past expiration time."""
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token.token = "test_token"
        token.token_time = datetime(1970, 1, 1)

        assert token._is_token_expired()

    @pytest.mark.unit
    def test_is_token_expired_with_future_time(self):
        """Test token expiration check with future expiration time."""
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token.token = "test_token"
        token.token_time = datetime.now() + timedelta(hours=1)

        assert not token._is_token_expired()


class TestOAuthTokenRequest:
    """Tests for token request and refresh."""

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    def test_request_new_token_success(self, mock_http, mock_oauth_response):
        """Test successful new token request."""
        mock_http.request.return_value = mock_oauth_response

        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token._request_new_token()

        assert token.token == "test_token_xyz"
        assert token.token_time > datetime.now()

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    def test_request_new_token_failure_no_existing_token(
        self, mock_http, mock_oauth_response_error
    ):
        """Test token request failure when no existing token."""
        mock_http.request.return_value = mock_oauth_response_error

        token = OAuthToken("client_id", "client_secret", "https://api.example.com")

        with pytest.raises(BritecoreError.NoTokenReturned):
            token._request_new_token()

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    def test_request_new_token_failure_with_existing_token(
        self, mock_http, mock_oauth_response_error
    ):
        """Test token request failure doesn't raise if existing token is present."""
        mock_http.request.return_value = mock_oauth_response_error

        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token.token = "existing_token"

        # Should not raise because token already exists
        token._request_new_token()
        # Token remains unchanged
        assert token.token == "existing_token"


class TestOAuthTokenHeaders:
    """Tests for authorization header building."""

    @pytest.mark.unit
    def test_build_auth_headers(self):
        """Test authorization header construction."""
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token.token = "test_token_xyz"

        headers = token._build_auth_headers()

        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token_xyz"
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    def test_get_authorization_headers_triggers_refresh(
        self, mock_http, mock_oauth_response
    ):
        """Test that get_authorization_headers triggers refresh when expired."""
        mock_http.request.return_value = mock_oauth_response

        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        headers = token.get_authorization_headers()

        assert "Authorization" in headers
        assert "Bearer" in headers["Authorization"]
        mock_http.request.assert_called_once()

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    def test_get_authorization_headers_no_refresh_if_valid(self, mock_http):
        """Test that get_authorization_headers doesn't refresh valid token."""
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token.token = "test_token"
        token.token_time = datetime.now() + timedelta(hours=1)

        headers = token.get_authorization_headers()

        assert "Authorization" in headers
        mock_http.request.assert_not_called()
