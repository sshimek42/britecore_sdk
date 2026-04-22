"""Unit tests for API client and lazy initialization."""

from unittest.mock import MagicMock, patch

import pytest

from britecore_sdk.exceptions import BritecoreError


class TestLazyAPIClientInitialization:
    """Tests for lazy API client proxy pattern."""

    @pytest.mark.unit
    def test_api_calls_module_imports_without_init(self):
        """Test that api_calls module can be imported without client initialization."""
        # This should not raise even without config/env setup
        from britecore_sdk.api.api_calls import (
            api_client,
            get_api_client,
            init_api_client,
        )

        assert api_client is not None
        assert get_api_client is not None
        assert init_api_client is not None

    @pytest.mark.unit
    def test_get_api_client_returns_client(
        self, env_api_key, mock_settings, monkeypatch
    ):
        """Test that get_api_client returns initialized client after explicit init."""
        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            from britecore_sdk.api.api_calls import (
                get_api_client,
                init_api_client,
            )

            init_api_client(target_site="test_site")
            client = get_api_client()

            assert client is not None
            assert hasattr(client, "base_url")

    @pytest.mark.unit
    def test_lazy_proxy_delegates_to_client(self, env_api_key, mock_settings):
        """Test that lazy proxy delegates attribute access to initialized client after explicit init."""
        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            # Reset the module to test fresh
            import importlib

            import britecore_sdk.api.api_calls

            importlib.reload(britecore_sdk.api.api_calls)

            from britecore_sdk.api.api_calls import api_client, init_api_client

            init_api_client(target_site="test_site")
            # Access an attribute on the proxy (should trigger init)
            assert hasattr(api_client, "base_url")


class TestBritecoreAPIClientInit:
    """Tests for BritecoreAPIClient initialization."""

    @pytest.mark.unit
    def test_init_with_api_key_auth(self, env_api_key, mock_settings):
        """Test API client initialization with API key authentication."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site")
            client.init_client()

            assert client.use_api_key is True
            assert client.api_key == "test_api_key_12345"
            assert client.token_class is None

    @pytest.mark.unit
    def test_init_with_oauth_auth(self, env_oauth, mock_settings_oauth):
        """Test API client initialization with OAuth authentication."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings_oauth
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site")
            client.init_client()

            assert client.use_api_key is False
            assert client.token_class is not None

    @pytest.mark.unit
    def test_init_raises_error_without_site(self):
        """Test that BritecoreAPIClient raises error without target_site."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with pytest.raises(ValueError):
            BritecoreAPIClient(None)

    @pytest.mark.unit
    def test_init_sets_timeouts(self, env_api_key, mock_settings):
        """Test that init_client configures timeouts."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site")
            client.init_client()

            assert client.web_timeout == 5
            assert client.web_timeout_long == 50

    @pytest.mark.unit
    def test_init_client_can_enable_default_dry_run(self, env_api_key, mock_settings):
        """Test that init_client stores a client-level default dry-run setting."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site")
            client.init_client(default_dry_run=True)

            assert client.default_dry_run is True


class TestBritecoreAPIClientProcessResult:
    """Tests for process_result method."""

    @pytest.mark.unit
    def test_process_result_success(self, mock_http_response):
        """Test successful result processing."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        result = BritecoreAPIClient.process_result(mock_http_response)

        assert result is not None
        assert result["id"] == "test_id"

    @pytest.mark.unit
    def test_process_result_error_response_none(self):
        """Test process_result raises error when response is None."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with pytest.raises(BritecoreError.NoDataReturned):
            BritecoreAPIClient.process_result(None)

    @pytest.mark.unit
    def test_process_result_error_non_200_status(self, mock_http_response_error):
        """Test process_result raises error for non-200 status."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with pytest.raises(BritecoreError.NoDataReturned):
            BritecoreAPIClient.process_result(mock_http_response_error)

    @pytest.mark.unit
    def test_process_result_error_success_false(self):
        """Test process_result raises error when success is false."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        response = MagicMock()
        response.status = 200
        response.data = b'{"success": false, "message": "API Error"}'

        with pytest.raises(BritecoreError.NoDataReturned):
            BritecoreAPIClient.process_result(response)


class TestMultipleParameterVerification:
    """Tests for parameter conflict resolution."""

    @pytest.mark.unit
    def test_multiple_parameter_verification_single_param(self):
        """Test parameter verification with single parameter."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        parameters = [{"policy_number": "POL123"}]
        priority = ["policy_number"]

        result = BritecoreAPIClient.multiple_parameter_verification(
            parameters, priority
        )

        assert "policy_number" in result
        assert result["policy_number"] == "POL123"

    @pytest.mark.unit
    def test_multiple_parameter_verification_multiple_params(self):
        """Test parameter verification with multiple parameters."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        parameters = [
            {"policy_number": "POL123"},
            {"policy_id": "12345"},
            {"revision_id": "REV999"},
        ]
        priority = ["revision_id", "policy_id", "policy_number"]

        result = BritecoreAPIClient.multiple_parameter_verification(
            parameters, priority
        )

        # Should select highest priority (revision_id)
        assert "revision_id" in result
        assert result["revision_id"] == "REV999"

    @pytest.mark.unit
    def test_multiple_parameter_verification_empty_params(self):
        """Test parameter verification with no parameters provided."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        parameters = [
            {"policy_number": None},
            {"policy_id": None},
        ]
        priority = ["policy_id", "policy_number"]

        result = BritecoreAPIClient.multiple_parameter_verification(
            parameters, priority
        )

        assert result is not None
