"""Unit tests for API client and lazy initialization."""

import logging
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
            BritecoreAPIClient("")

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
    def test_init_client_can_enable_client_dry_run(self, env_api_key, mock_settings):
        """Test that init_client stores a client-level dry-run setting."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site")
            client.init_client(client_dry_run=True)

            assert client.client_dry_run is True

    @pytest.mark.unit
    def test_init_client_write_policy_loads_from_settings(
        self, env_api_key, mock_settings
    ):
        """init_client inherits write_policy from loaded site settings by default."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        mock_settings.write_policy = "block"
        mock_settings.write_allowlist = ["/api/v2/quotes/retrieve_quote"]
        mock_settings.write_denylist = ["/api/v2/quotes/new_quote"]

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site").init_client()

        assert client.write_policy == "block"

    @pytest.mark.unit
    def test_init_client_write_policy_kwarg_overrides_settings(
        self, env_api_key, mock_settings
    ):
        """Explicit write_policy kwarg takes precedence over site settings."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        mock_settings.write_policy = "block"

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site").init_client(write_policy="warn")

        assert client.write_policy == "warn"

    @pytest.mark.unit
    def test_init_client_audit_middleware_enabled_from_settings(
        self, env_api_key, mock_settings
    ):
        """init_client registers audit middleware when enabled in settings."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        mock_settings.enable_audit_middleware = True

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site").init_client()

        assert any(
            middleware.__class__.__name__ == "AuditMiddleware"
            for middleware in client.middleware
        )

    @pytest.mark.unit
    def test_init_client_audit_middleware_kwarg_overrides_settings(
        self, env_api_key, mock_settings
    ):
        """Explicit enable_audit_middleware=False disables configured audit middleware."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        mock_settings.enable_audit_middleware = True

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site").init_client(
                enable_audit_middleware=False
            )

        assert all(
            middleware.__class__.__name__ != "AuditMiddleware"
            for middleware in client.middleware
        )

    @pytest.mark.unit
    def test_init_client_preserves_custom_write_guard_subclass(
        self, env_api_key, mock_settings
    ):
        """Repeated init_client should not remove user custom guard subclasses."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
        from britecore_sdk.api.middleware import (
            RequestContext,
            ResponseContext,
            WriteGuardMiddleware,
        )

        class CustomWriteGuard(WriteGuardMiddleware):
            def on_request(self, ctx: RequestContext) -> RequestContext:
                return ctx

            def on_response(self, ctx: ResponseContext) -> ResponseContext:
                return ctx

            def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
                return error

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site")
            client.add_middleware(CustomWriteGuard(policy="allow"))

            client.init_client(write_policy="warn")
            client.init_client(write_policy="block")

        custom_guards = [
            m for m in client.middleware if isinstance(m, CustomWriteGuard)
        ]
        managed_guards = [
            m for m in client.middleware if type(m).__name__ == "WriteGuardMiddleware"
        ]
        assert len(custom_guards) == 1
        assert len(managed_guards) == 1
        assert managed_guards[0].policy == "block"

    @pytest.mark.unit
    def test_init_client_preserves_custom_audit_subclass(
        self, env_api_key, mock_settings
    ):
        """Repeated init_client should not remove user custom audit subclasses."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
        from britecore_sdk.api.middleware import (
            AuditMiddleware,
            RequestContext,
            ResponseContext,
        )

        class CustomAudit(AuditMiddleware):
            def on_request(self, ctx: RequestContext) -> RequestContext:
                return ctx

            def on_response(self, ctx: ResponseContext) -> ResponseContext:
                return ctx

            def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
                return error

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site")
            client.add_middleware(CustomAudit())

            client.init_client(enable_audit_middleware=True)
            client.init_client(enable_audit_middleware=True)

        custom_audits = [m for m in client.middleware if isinstance(m, CustomAudit)]
        managed_audits = [
            m for m in client.middleware if type(m).__name__ == "AuditMiddleware"
        ]
        assert len(custom_audits) == 1
        assert len(managed_audits) == 1


class TestBritecoreAPIClientProcessResult:
    """Tests for process_result method."""

    @pytest.mark.unit
    def test_process_result_success(self, mock_http_response):
        """Test successful result processing."""
        from unittest.mock import patch

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_settings:
            mock_instance = MagicMock()
            mock_instance.load_config.return_value = MagicMock(
                base_url="https://api.example.com",
                client_id="",
                client_secret="",
                api_key="test-key",
                web_timeout=30,
                web_timeout_long=300,
                web_retry=5,
            )
            mock_settings.return_value = mock_instance

            client = BritecoreAPIClient("test_site").init_client()
            result = client.process_result(mock_http_response)

            assert result is not None
            assert result["id"] == "test_id"

    @pytest.mark.unit
    def test_process_result_error_response_none(self):
        """Test process_result raises error when response is None."""
        from unittest.mock import patch

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_settings:
            mock_instance = MagicMock()
            mock_instance.load_config.return_value = MagicMock(
                base_url="https://api.example.com",
                client_id="",
                client_secret="",
                api_key="test-key",
                web_timeout=30,
                web_timeout_long=300,
                web_retry=5,
            )
            mock_settings.return_value = mock_instance

            client = BritecoreAPIClient("test_site").init_client()
            with pytest.raises(BritecoreError.NoDataReturned):
                client.process_result(None)

    @pytest.mark.unit
    def test_process_result_error_non_200_status(self, mock_http_response_error):
        """Test process_result raises error for non-200 status."""
        from unittest.mock import patch

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_settings:
            mock_instance = MagicMock()
            mock_instance.load_config.return_value = MagicMock(
                base_url="https://api.example.com",
                client_id="",
                client_secret="",
                api_key="test-key",
                web_timeout=30,
                web_timeout_long=300,
                web_retry=5,
            )
            mock_settings.return_value = mock_instance

            client = BritecoreAPIClient("test_site").init_client()
            with pytest.raises(BritecoreError.NoDataReturned):
                client.process_result(mock_http_response_error)

    @pytest.mark.unit
    def test_process_result_error_success_false(self):
        """Test process_result raises error when success is false."""
        from unittest.mock import patch

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        response = MagicMock()
        response.status = 200
        response.data = b'{"success": false, "message": "API Error"}'

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_settings:
            mock_instance = MagicMock()
            mock_instance.load_config.return_value = MagicMock(
                base_url="https://api.example.com",
                client_id="",
                client_secret="",
                api_key="test-key",
                web_timeout=30,
                web_timeout_long=300,
                web_retry=5,
            )
            mock_settings.return_value = mock_instance

            client = BritecoreAPIClient("test_site").init_client()
            with pytest.raises(BritecoreError.NoDataReturned):
                client.process_result(response)

    @pytest.mark.unit
    def test_process_result_accepts_single_quoted_payload(self):
        """Test process_result supports legacy Python-literal response payloads."""
        from unittest.mock import patch

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        response = MagicMock()
        response.status = 200
        response.data = b"{'success': True, 'data': {'id': 'legacy-id'}}"
        response.headers = {}

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_settings:
            mock_instance = MagicMock()
            mock_instance.load_config.return_value = MagicMock(
                base_url="https://api.example.com",
                client_id="",
                client_secret="",
                api_key="test-key",
                web_timeout=30,
                web_timeout_long=300,
                web_retry=5,
            )
            mock_settings.return_value = mock_instance

            client = BritecoreAPIClient("test_site").init_client()
            result = client.process_result(response)

            assert result == {"id": "legacy-id"}


class TestRequestContextAttachedToExceptions:
    """Integration tests: request_id and sanitized_body are propagated to raised exceptions."""

    def _make_client(self):
        """Return an initialized API-key client with a mocked HTTP pool."""
        from types import SimpleNamespace

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        client = BritecoreAPIClient("test_site")
        client.base_url = "https://api.example.com"
        client.use_api_key = True
        client.api_key = "test-key"
        client.client_dry_run = False
        client.debug_include_request_body = False
        client.token_class = None
        client.rate_limiter = None
        client.web_timeout = 30
        client.web_retry = 0
        client.site_settings = SimpleNamespace(api_key="test-key")
        return client

    # ------------------------------------------------------------------
    # do_request: timeout carries request_id + sanitized_body
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_do_request_timeout_carries_request_id(self):
        """RequestTimeoutError raised by do_request has request_id set."""
        from unittest.mock import MagicMock

        from urllib3.exceptions import TimeoutError as urlTimeoutError

        from britecore_sdk.exceptions import BritecoreError

        client = self._make_client()
        mock_http = MagicMock()
        mock_http.request.side_effect = urlTimeoutError("timed out")
        client.http = mock_http

        with pytest.raises(BritecoreError.RequestTimeoutError) as exc_info:
            client.do_request("/api/v2/policies", json={"filter": "all"})

        err = exc_info.value
        assert err.request_id is not None
        assert len(err.request_id) == 8  # hex[:8]

    @pytest.mark.unit
    def test_do_request_timeout_carries_sanitized_body(self):
        """RequestTimeoutError has sanitized (api_key redacted) body attached."""
        from unittest.mock import MagicMock

        from urllib3.exceptions import TimeoutError as urlTimeoutError

        from britecore_sdk.exceptions import BritecoreError

        client = self._make_client()
        mock_http = MagicMock()
        mock_http.request.side_effect = urlTimeoutError("timed out")
        client.http = mock_http

        with pytest.raises(BritecoreError.RequestTimeoutError) as exc_info:
            client.do_request("/api/v2/policies", json={"policy_number": "P123"})

        body = exc_info.value.sanitized_body
        assert isinstance(body, dict)
        assert body.get("api_key") == "***redacted***"
        assert body.get("policy_number") == "P123"

    @pytest.mark.unit
    def test_do_request_network_error_carries_request_id(self):
        """NoDataReturned from a network error has request_id set."""
        from unittest.mock import MagicMock

        from urllib3.exceptions import ProtocolError

        from britecore_sdk.exceptions import BritecoreError

        client = self._make_client()
        mock_http = MagicMock()
        mock_http.request.side_effect = ProtocolError("connection reset")
        client.http = mock_http

        with pytest.raises(BritecoreError.NoDataReturned) as exc_info:
            client.do_request("/api/v2/test", json={"x": 1})

        assert exc_info.value.request_id is not None

    @pytest.mark.unit
    def test_do_request_debug_mode_stores_unredacted_body(self):
        """With debug_include_request_body=True the raw body is attached to the exception."""
        from unittest.mock import MagicMock

        from urllib3.exceptions import TimeoutError as urlTimeoutError

        from britecore_sdk.exceptions import BritecoreError

        client = self._make_client()
        client.debug_include_request_body = True
        mock_http = MagicMock()
        mock_http.request.side_effect = urlTimeoutError("timed out")
        client.http = mock_http

        with pytest.raises(BritecoreError.RequestTimeoutError) as exc_info:
            client.do_request("/api/v2/policies", json={"policy_number": "P123"})

        body = exc_info.value.sanitized_body
        # In debug mode the api_key is NOT redacted
        assert body.get("api_key") == "test-key"

    # ------------------------------------------------------------------
    # process_result: request_id extracted from dry-run response headers
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_process_result_extracts_request_id_from_response_headers(self):
        """process_result picks up request_id from X-SDK-Request-ID response header."""
        import urllib3

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
        from britecore_sdk.exceptions import BritecoreError

        response = urllib3.HTTPResponse(
            body=b'{"success": false, "message": "API Error"}',
            status=200,
            reason="OK",
            headers={
                "Content-Type": "application/json",
                "X-SDK-Request-ID": "abcd1234",
            },
            preload_content=True,
        )

        client = BritecoreAPIClient.__new__(BritecoreAPIClient)
        client.rate_limiter = None

        with pytest.raises(BritecoreError.NoDataReturned) as exc_info:
            client.process_result(response)

        assert exc_info.value.request_id == "abcd1234"

    @pytest.mark.unit
    def test_process_result_caller_supplied_request_id_takes_precedence(self):
        """Explicit request_id kwarg overrides any header value."""
        import urllib3

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
        from britecore_sdk.exceptions import BritecoreError

        response = urllib3.HTTPResponse(
            body=b'{"success": false, "message": "err"}',
            status=200,
            reason="OK",
            headers={
                "Content-Type": "application/json",
                "X-SDK-Request-ID": "from-header",
            },
            preload_content=True,
        )

        client = BritecoreAPIClient.__new__(BritecoreAPIClient)
        client.rate_limiter = None

        with pytest.raises(BritecoreError.NoDataReturned) as exc_info:
            client.process_result(response, request_id="caller-supplied")

        assert exc_info.value.request_id == "caller-supplied"

    @pytest.mark.unit
    def test_process_result_none_response_carries_request_id(self):
        """NoDataReturned from a None response carries the supplied request_id."""
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
        from britecore_sdk.exceptions import BritecoreError

        client = BritecoreAPIClient.__new__(BritecoreAPIClient)
        client.rate_limiter = None

        with pytest.raises(BritecoreError.NoDataReturned) as exc_info:
            client.process_result(None, request_id="none-req")

        assert exc_info.value.request_id == "none-req"

    @pytest.mark.unit
    def test_process_result_http_error_carries_request_id_and_body(self):
        """HTTP 400 response passes request_id and sanitized_body to the raised exception."""
        from unittest.mock import MagicMock

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
        from britecore_sdk.exceptions import BritecoreError

        response = MagicMock()
        response.status = 400
        response.reason = "Bad Request"
        response.headers = {}

        client = BritecoreAPIClient.__new__(BritecoreAPIClient)
        client.rate_limiter = None

        with pytest.raises(BritecoreError.ValidationError) as exc_info:
            client.process_result(
                response,
                request_id="req-400",
                sanitized_body={"field": "value"},
            )

        err = exc_info.value
        assert err.request_id == "req-400"
        assert err.sanitized_body == {"field": "value"}

    # ------------------------------------------------------------------
    # init_client: debug_include_request_body flag
    # ------------------------------------------------------------------

    @pytest.mark.unit
    def test_init_client_debug_flag_defaults_false(self, env_api_key, mock_settings):
        """debug_include_request_body defaults to False after init_client."""
        from unittest.mock import patch

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.return_value = mock_settings
            client = BritecoreAPIClient("test_site").init_client()

        assert client.debug_include_request_body is False

    @pytest.mark.unit
    def test_init_client_debug_flag_can_be_enabled(self, env_api_key, mock_settings):
        """debug_include_request_body=True is stored on the client."""
        from unittest.mock import patch

        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.return_value = mock_settings
            client = BritecoreAPIClient("test_site").init_client(
                debug_include_request_body=True
            )

        assert client.debug_include_request_body is True

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


@pytest.mark.unit
def test_dry_run_logging_omits_sensitive_body_values(
    env_api_key, mock_settings, caplog
):
    """Dry-run logs include only summary metadata for payloads."""
    from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

    sdk_logger = logging.getLogger("britecore_sdk")
    original_propagate = sdk_logger.propagate
    sdk_logger.propagate = True

    try:
        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance

            client = BritecoreAPIClient("test_site").init_client()
            caplog.set_level("INFO", logger="britecore_sdk")
            client.do_request(
                "/api/v2/quotes",
                json={"password": "super-secret", "nested": {"token": "abc123"}},
                dry_run=True,
            )
    finally:
        sdk_logger.propagate = original_propagate

    assert "body_summary=" in caplog.text
    assert "super-secret" not in caplog.text
    assert "abc123" not in caplog.text


@pytest.mark.unit
def test_dry_run_body_summary_empty_dict():
    """Body summary for empty dict returns dict with zero keys."""
    from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

    result = BritecoreAPIClient._dry_run_body_summary({})
    assert result["type"] == "dict"
    assert result["key_count"] == 0
    assert result["keys"] == []


@pytest.mark.unit
def test_dry_run_body_summary_list():
    """Body summary for list returns type and length."""
    from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

    result = BritecoreAPIClient._dry_run_body_summary([1, 2, 3])
    assert result["type"] == "list"
    assert result["length"] == 3


@pytest.mark.unit
def test_dry_run_body_summary_empty_list():
    """Body summary for empty list returns zero length."""
    from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

    result = BritecoreAPIClient._dry_run_body_summary([])
    assert result["type"] == "list"
    assert result["length"] == 0


@pytest.mark.unit
def test_dry_run_body_summary_tuple():
    """Body summary for tuple returns type and length."""
    from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

    result = BritecoreAPIClient._dry_run_body_summary((1, 2, 3, 4))
    assert result["type"] == "tuple"
    assert result["length"] == 4


@pytest.mark.unit
def test_dry_run_body_summary_none():
    """Body summary for None returns none type."""
    from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

    result = BritecoreAPIClient._dry_run_body_summary(None)
    assert result["type"] == "none"


@pytest.mark.unit
def test_dry_run_body_summary_string():
    """Body summary for string returns string type."""
    from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

    result = BritecoreAPIClient._dry_run_body_summary("test string")
    assert result["type"] == "str"


@pytest.mark.unit
def test_dry_run_body_summary_many_keys_truncated():
    """Body summary truncates key list at 20 keys to avoid log bloat."""
    from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

    large_dict = {f"key_{i}": i for i in range(50)}
    result = BritecoreAPIClient._dry_run_body_summary(large_dict)
    assert result["type"] == "dict"
    assert result["key_count"] == 50
    assert len(result["keys"]) <= 20
    assert result["keys"] == sorted(result["keys"])  # Keys are sorted
