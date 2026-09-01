"""Unit tests for request middleware and write guard behavior."""

from json import loads
from unittest.mock import MagicMock, patch

import pytest

from britecore_sdk.api.middleware import (
    AuditMiddleware,
    Middleware,
    RequestContext,
    ResponseContext,
    WriteGuardMiddleware,
)
from britecore_sdk.exceptions import BritecoreError


class TestWriteGuardMiddleware:
    """Tests for write classification and policy enforcement."""

    @pytest.mark.unit
    def test_write_guard_classifies_post_endpoints(self):
        """POST endpoints are classified using path markers."""
        middleware = WriteGuardMiddleware(policy="block")

        assert (
            middleware.is_write_operation("POST", "/api/v2/contacts/new_contact")
            is True
        )
        assert (
            middleware.is_write_operation("POST", "/api/v2/quotes/retrieve_quote")
            is False
        )
        assert middleware.is_write_operation("PUT", "/api/v2/quotes/custom") is True

    @pytest.mark.unit
    def test_write_guard_warn_policy_emits_warning_and_callback(self):
        """Warn policy emits warnings without blocking requests."""
        events: list[dict[str, object]] = []

        def _warning_callback(event: dict[str, object]) -> None:
            events.append(event)

        middleware = WriteGuardMiddleware(
            policy="warn",
            warning_callback=_warning_callback,
        )

        ctx = RequestContext(method="POST", path="/api/v2/quotes/new_quote")
        with pytest.warns(UserWarning):
            returned = middleware.on_request(ctx)

        assert returned is ctx
        assert events
        assert events[0]["path"] == "/api/v2/quotes/new_quote"


class TestClientMiddlewareIntegration:
    """Tests for middleware execution in BritecoreAPIClient.do_request."""

    @staticmethod
    def _init_client(mock_settings, **kwargs):
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.return_value = mock_settings
            return BritecoreAPIClient("test_site").init_client(**kwargs)

    @pytest.mark.unit
    def test_init_client_write_policy_block_blocks_write_request(
        self, env_api_key, mock_settings
    ):
        """write_policy='block' raises before HTTP transport is called."""
        client = self._init_client(mock_settings, write_policy="block")
        mock_http = MagicMock()
        client.http = mock_http

        with pytest.raises(BritecoreError.ReadOnlyViolation):
            client.do_request(
                "/api/v2/contacts/new_contact",
                json={"name": "Alice"},
            )

        assert mock_http.request.call_count == 0

    @pytest.mark.unit
    def test_write_policy_warn_allows_dry_run(self, env_api_key, mock_settings):
        """write_policy='warn' allows execution but emits a warning."""
        events: list[dict[str, object]] = []

        def _warning_callback(event: dict[str, object]) -> None:
            events.append(event)

        client = self._init_client(
            mock_settings,
            write_policy="warn",
            write_warning_callback=_warning_callback,
        )

        with pytest.warns(UserWarning):
            response = client.do_request(
                "/api/v2/quotes/new_quote",
                json={"quote_number": "Q123"},
                dry_run=True,
            )

        assert response.status == 200
        assert events
        assert events[0]["method"] == "POST"

    @pytest.mark.unit
    def test_custom_middleware_mutates_dry_run_request(
        self, env_api_key, mock_settings
    ):
        """Middleware request mutations flow into the emitted dry-run envelope."""

        class HeaderMiddleware(Middleware):
            def __init__(self):
                self.seen_response = False

            def on_request(self, ctx: RequestContext) -> RequestContext:
                ctx.headers["X-Test-Middleware"] = "enabled"
                return ctx

            def on_response(self, ctx: ResponseContext) -> ResponseContext:
                self.seen_response = True
                return ctx

            def on_error(self, error: Exception, ctx: RequestContext) -> Exception:
                return error

        client = self._init_client(mock_settings)
        middleware = HeaderMiddleware()
        client.clear_middleware().add_middleware(middleware)

        response = client.do_request(
            "/api/v2/quotes/retrieve_quote",
            json={"quote_number": "Q123"},
            dry_run=True,
        )

        payload = loads(response.data.decode("utf-8"))
        assert payload["data"]["headers"]["X-Test-Middleware"] == "enabled"
        assert middleware.seen_response is True

    @pytest.mark.unit
    def test_write_allowlist_overrides_default_write_classification(
        self, env_api_key, mock_settings
    ):
        """Allowlisted POST endpoint bypasses write guard blocking."""
        client = self._init_client(
            mock_settings,
            write_policy="block",
            write_allowlist=["/api/v2/contacts/new_contact"],
        )

        response = client.do_request(
            "/api/v2/contacts/new_contact",
            json={"name": "Alice"},
            dry_run=True,
        )

        assert response.status == 200


class TestAuditMiddleware:
    """Tests for request audit behavior and init_client activation."""

    @staticmethod
    def _init_client(mock_settings, **kwargs):
        from britecore_sdk.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_sdk.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.return_value = mock_settings
            return BritecoreAPIClient("test_site").init_client(**kwargs)

    @pytest.mark.unit
    def test_audit_middleware_callback_receives_write_event(self):
        """Audit middleware emits structured callback events for write-like requests."""
        events: list[dict[str, object]] = []

        def _callback(event: dict[str, object]) -> None:
            events.append(event)

        middleware = AuditMiddleware(audit_callback=_callback)
        ctx = RequestContext(method="POST", path="/api/v2/contacts/new_contact")

        middleware.on_request(ctx)

        assert events
        assert events[0]["event"] == "sdk_request_audit"
        assert events[0]["write_operation"] is True

    @pytest.mark.unit
    def test_audit_middleware_skips_read_operation_by_default(self):
        """Audit middleware defaults to auditing writes only."""
        events: list[dict[str, object]] = []

        def _callback(event: dict[str, object]) -> None:
            events.append(event)

        middleware = AuditMiddleware(audit_callback=_callback)
        ctx = RequestContext(method="POST", path="/api/v2/quotes/retrieve_quote")

        middleware.on_request(ctx)

        assert events == []

    @pytest.mark.unit
    def test_init_client_enables_audit_middleware_from_settings(
        self, env_api_key, mock_settings
    ):
        """init_client can auto-register AuditMiddleware from site config."""
        mock_settings.enable_audit_middleware = True
        mock_settings.audit_only_writes = False
        mock_settings.audit_log_level = "debug"

        client = self._init_client(mock_settings)

        assert any(isinstance(item, AuditMiddleware) for item in client.middleware)
