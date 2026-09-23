"""Unit tests for OAuth token manager."""

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from threading import Barrier
from time import sleep
from unittest.mock import patch
from urllib.parse import urlparse

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
        assert urlparse(token.url).hostname == "api.example.com"
        assert "/api/auth/oauth2/token" in token.url

    @pytest.mark.unit
    def test_init_with_bare_host(self):
        """Test OAuthToken initialization with bare host."""
        token = OAuthToken("client_id", "client_secret", "api.example.com")

        assert token.client_id == "client_id"
        assert token.url == "https://api.example.com/api/auth/oauth2/token"

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

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    @patch("britecore_sdk.api.britecore_oauth_token_manager.log_with_category")
    def test_request_new_token_missing_access_token_without_fallback_raises(
        self, mock_log_with_category, mock_http
    ):
        """A token response without access_token should fail if no fallback token exists."""
        mock_http.request.return_value = type(
            "Resp",
            (),
            {"status": 200, "data": b'{"expires_in": 3600}'},
        )()

        token = OAuthToken("client_id", "client_secret", "https://api.example.com")

        with pytest.raises(BritecoreError.NoTokenReturned):
            token._request_new_token()

        events = [
            call.kwargs.get("event") for call in mock_log_with_category.call_args_list
        ]
        assert "oauth_token_missing_access_token" in events

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    @patch("britecore_sdk.api.britecore_oauth_token_manager.log_with_category")
    def test_request_new_token_missing_access_token_with_fallback_reuses(
        self, mock_log_with_category, mock_http
    ):
        """A refresh response without access_token should reuse an existing token."""
        mock_http.request.return_value = type(
            "Resp",
            (),
            {"status": 200, "data": b'{"expires_in": 3600}'},
        )()

        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token.token = "existing_token"

        token._request_new_token()

        assert token.token == "existing_token"
        events = [
            call.kwargs.get("event") for call in mock_log_with_category.call_args_list
        ]
        assert "oauth_token_refresh_missing_access_token_reused" in events


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


class TestOAuthTokenConcurrency:
    """Concurrency tests for token refresh and header retrieval."""

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    def test_concurrent_header_requests_only_refresh_once(
        self, mock_http, mock_oauth_response
    ):
        """Parallel callers should converge on a single token refresh."""

        def slow_request(*args, **kwargs):
            sleep(0.02)
            return mock_oauth_response

        mock_http.request.side_effect = slow_request
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        barrier = Barrier(8)

        def worker() -> str:
            barrier.wait()
            headers = token.get_authorization_headers()
            return headers["Authorization"]

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(lambda _: worker(), range(8)))

        assert results == ["Bearer test_token_xyz"] * 8
        assert mock_http.request.call_count == 1

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    def test_concurrent_header_requests_with_valid_token_skip_refresh(self, mock_http):
        """Parallel callers with a valid token should not trigger refresh."""
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token.token = "test_token"
        token.token_time = datetime.now() + timedelta(hours=1)
        barrier = Barrier(8)

        def worker() -> str:
            barrier.wait()
            headers = token.get_authorization_headers()
            return headers["Authorization"]

        with ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(lambda _: worker(), range(8)))

        assert results == ["Bearer test_token"] * 8
        mock_http.request.assert_not_called()


class TestOAuthTokenStructuredLogging:
    """Structured AUTH logging coverage for token manager flows."""

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    @patch("britecore_sdk.api.britecore_oauth_token_manager.log_with_category")
    def test_request_new_token_emits_success_event(
        self, mock_log_with_category, mock_http, mock_oauth_response
    ):
        """Successful token refresh emits oauth_token_refresh_success."""
        mock_http.request.return_value = mock_oauth_response

        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token._request_new_token()

        events = [
            call.kwargs.get("event") for call in mock_log_with_category.call_args_list
        ]
        assert "oauth_token_request_start" in events
        assert "oauth_token_refresh_success" in events

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.http")
    @patch("britecore_sdk.api.britecore_oauth_token_manager.log_with_category")
    def test_request_new_token_failure_emits_failure_event(
        self, mock_log_with_category, mock_http, mock_oauth_response_error
    ):
        """Token fetch failure without fallback token emits failure event."""
        mock_http.request.return_value = mock_oauth_response_error

        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        with pytest.raises(BritecoreError.NoTokenReturned):
            token._request_new_token()

        events = [
            call.kwargs.get("event") for call in mock_log_with_category.call_args_list
        ]
        assert "oauth_token_request_failed" in events

    @pytest.mark.unit
    @patch("britecore_sdk.api.britecore_oauth_token_manager.log_with_category")
    def test_get_authorization_headers_emits_reuse_event_for_valid_token(
        self, mock_log_with_category
    ):
        """Valid token path emits oauth_token_reused without refresh attempt."""
        token = OAuthToken("client_id", "client_secret", "https://api.example.com")
        token.token = "test_token"
        token.token_time = datetime.now() + timedelta(hours=1)

        headers = token.get_authorization_headers()
        assert headers["Authorization"] == "Bearer test_token"

        events = [
            call.kwargs.get("event") for call in mock_log_with_category.call_args_list
        ]
        assert "oauth_token_reused" in events
