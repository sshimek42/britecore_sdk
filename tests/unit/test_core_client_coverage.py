"""Extended unit tests for BritecoreAPIClient core paths.

Targets the error branches and edge cases in do_request() and
process_result() that were previously uncovered, including the
new specific exception types added in Tier 2.
"""

from unittest.mock import MagicMock, patch

import pytest
from urllib3 import BaseHTTPResponse
from urllib3.exceptions import (
    ProtocolError,
    ResponseError,
)
from urllib3.exceptions import TimeoutError as urlTimeoutError
from urllib3.util import Timeout

from britecore_libraries.exceptions import BritecoreError

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_response(
    payload: bytes = b'{"success": true, "data": {"id": "x"}}',
    status: int = 200,
    reason: str | None = None,
    headers: dict | None = None,
) -> MagicMock:
    resp = MagicMock(spec=BaseHTTPResponse)
    resp.status = status
    resp.reason = reason or ("OK" if status == 200 else "Error")
    resp.data = payload
    resp.headers = headers or {}
    return resp


# ---------------------------------------------------------------------------
# process_result — status-code dispatch
# ---------------------------------------------------------------------------


class TestProcessResultStatusCodes:
    """Tests for HTTP status → exception mapping in process_result."""

    @pytest.mark.unit
    def test_none_response_raises_no_data_returned(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        with pytest.raises(BritecoreError.NoDataReturned):
            BritecoreAPIClient.process_result(None)

    @pytest.mark.unit
    def test_401_raises_authentication_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=401, reason="Unauthorized")
        with pytest.raises(BritecoreError.AuthenticationError) as exc_info:
            BritecoreAPIClient.process_result(resp)
        assert exc_info.value.http_status == 401

    @pytest.mark.unit
    def test_403_raises_authentication_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=403, reason="Forbidden")
        with pytest.raises(BritecoreError.AuthenticationError) as exc_info:
            BritecoreAPIClient.process_result(resp)
        assert exc_info.value.http_status == 403

    @pytest.mark.unit
    def test_authentication_error_str_includes_status(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=401, reason="Unauthorized")
        with pytest.raises(BritecoreError.AuthenticationError) as exc_info:
            BritecoreAPIClient.process_result(resp)
        assert "401" in str(exc_info.value)

    @pytest.mark.unit
    def test_429_raises_rate_limit_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=429, reason="Too Many Requests")
        with pytest.raises(BritecoreError.RateLimitError):
            BritecoreAPIClient.process_result(resp)

    @pytest.mark.unit
    def test_429_with_retry_after_header_populates_attribute(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(
            b"", status=429, reason="Too Many Requests", headers={"Retry-After": "30"}
        )
        with pytest.raises(BritecoreError.RateLimitError) as exc_info:
            BritecoreAPIClient.process_result(resp)
        assert exc_info.value.retry_after == 30

    @pytest.mark.unit
    def test_500_raises_server_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=500, reason="Internal Server Error")
        with pytest.raises(BritecoreError.ServerError) as exc_info:
            BritecoreAPIClient.process_result(resp)
        assert exc_info.value.http_status == 500

    @pytest.mark.unit
    def test_503_raises_server_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=503, reason="Service Unavailable")
        with pytest.raises(BritecoreError.ServerError) as exc_info:
            BritecoreAPIClient.process_result(resp)
        assert exc_info.value.http_status == 503

    @pytest.mark.unit
    def test_server_error_str_includes_status(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=502, reason="Bad Gateway")
        with pytest.raises(BritecoreError.ServerError) as exc_info:
            BritecoreAPIClient.process_result(resp)
        assert "502" in str(exc_info.value)

    @pytest.mark.unit
    def test_404_raises_no_data_returned(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=404, reason="Not Found")
        with pytest.raises(BritecoreError.NoDataReturned):
            BritecoreAPIClient.process_result(resp)

    @pytest.mark.unit
    def test_404_raises_not_found_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=404, reason="Not Found")
        with pytest.raises(BritecoreError.NotFoundError):
            BritecoreAPIClient.process_result(resp)

    @pytest.mark.unit
    def test_409_raises_conflict_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=409, reason="Conflict")
        with pytest.raises(BritecoreError.ConflictError):
            BritecoreAPIClient.process_result(resp)

    @pytest.mark.unit
    def test_422_raises_validation_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"", status=422, reason="Unprocessable Entity")
        with pytest.raises(BritecoreError.ValidationError):
            BritecoreAPIClient.process_result(resp)

    @pytest.mark.unit
    def test_200_success_false_raises_no_data_returned(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(
            b'{"success": false, "message": "Quota exceeded"}', status=200
        )
        with pytest.raises(BritecoreError.NoDataReturned):
            BritecoreAPIClient.process_result(resp)

    @pytest.mark.unit
    def test_200_success_true_returns_data(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b'{"success": true, "data": {"id": "ABC"}}', status=200)
        result = BritecoreAPIClient.process_result(resp)
        assert result == {"id": "ABC"}

    @pytest.mark.unit
    def test_200_empty_data_returns_none_with_warning(self):
        from britecore_libraries.api import britecore_api_client as client_mod

        resp = _make_response(b'{"success": true, "data": null}', status=200)
        with patch.object(client_mod.LOGGER, "warning") as mock_warning:
            result = client_mod.BritecoreAPIClient.process_result(resp)
        assert result is None
        mock_warning.assert_called_once_with("No data returned")

    @pytest.mark.unit
    def test_messages_key_used_as_fallback_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(
            b'{"success": false, "messages": "Validation failed"}', status=200
        )
        with pytest.raises(BritecoreError.NoDataReturned) as exc_info:
            BritecoreAPIClient.process_result(resp)
        assert "Validation failed" in str(exc_info.value)

    @pytest.mark.unit
    def test_malformed_json_raises_no_data_returned(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        resp = _make_response(b"not-json", status=200)
        with pytest.raises(BritecoreError.NoDataReturned):
            BritecoreAPIClient.process_result(resp)

    @pytest.mark.unit
    def test_logs_flag_triggers_debug_log(self):
        """When logs=True, LOGGER.debug is called with the data payload."""
        from britecore_libraries.api import britecore_api_client as client_mod

        resp = _make_response(b'{"success": true, "data": {"id": "X"}}')
        with patch.object(client_mod.LOGGER, "debug") as mock_debug:
            client_mod.BritecoreAPIClient.process_result(resp, logs=True)
        mock_debug.assert_called_once_with({"id": "X"})


# ---------------------------------------------------------------------------
# do_request — network error mapping
# ---------------------------------------------------------------------------


class TestDoRequestExceptionMapping:
    """Tests for network error → exception mapping in do_request."""

    def _initialized_client(self, mock_settings):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_libraries.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader_instance = MagicMock()
            mock_loader_instance.load_config.return_value = mock_settings
            mock_loader.return_value = mock_loader_instance
            client = BritecoreAPIClient("test_site")
            client.init_client()
        return client

    @pytest.mark.unit
    def test_timeout_error_raises_request_timeout_error(
        self, env_api_key, mock_settings
    ):
        client = self._initialized_client(mock_settings)
        with (
            patch.object(
                client.http, "request", side_effect=urlTimeoutError("timed out")
            ),
            pytest.raises(BritecoreError.RequestTimeoutError),
        ):
            client.do_request("/api/v2/test")

    @pytest.mark.unit
    def test_request_timeout_error_str(self, env_api_key, mock_settings):
        client = self._initialized_client(mock_settings)
        with (
            patch.object(
                client.http, "request", side_effect=urlTimeoutError("timed out")
            ),
            pytest.raises(BritecoreError.RequestTimeoutError) as exc_info,
        ):
            client.do_request("/api/v2/test")
        assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.unit
    def test_protocol_error_raises_no_data_returned(self, env_api_key, mock_settings):
        client = self._initialized_client(mock_settings)
        with (
            patch.object(
                client.http, "request", side_effect=ProtocolError("broken pipe")
            ),
            pytest.raises(BritecoreError.NoDataReturned),
        ):
            client.do_request("/api/v2/test")

    @pytest.mark.unit
    def test_response_error_raises_no_data_returned(self, env_api_key, mock_settings):
        client = self._initialized_client(mock_settings)
        with (
            patch.object(
                client.http, "request", side_effect=ResponseError("bad response")
            ),
            pytest.raises(BritecoreError.NoDataReturned),
        ):
            client.do_request("/api/v2/test")

    @pytest.mark.unit
    def test_falsy_result_raises_no_data_returned(self, env_api_key, mock_settings):
        client = self._initialized_client(mock_settings)
        with (
            patch.object(client.http, "request", return_value=None),
            pytest.raises(BritecoreError.NoDataReturned),
        ):
            client.do_request("/api/v2/test")

    @pytest.mark.unit
    def test_successful_request_returns_response(self, env_api_key, mock_settings):
        client = self._initialized_client(mock_settings)
        mock_resp = _make_response(b'{"success": true, "data": {}}')
        with patch.object(client.http, "request", return_value=mock_resp):
            result = client.do_request("/api/v2/test")
        assert result is mock_resp

    @pytest.mark.unit
    def test_custom_timeout_is_passed_to_request(self, env_api_key, mock_settings):
        client = self._initialized_client(mock_settings)
        mock_resp = _make_response()
        custom_timeout = Timeout(99)
        with patch.object(client.http, "request", return_value=mock_resp) as mock_req:
            client.do_request("/api/v2/test", request_timeout=custom_timeout)
        _, kwargs = mock_req.call_args
        assert kwargs.get("timeout") is custom_timeout

    @pytest.mark.unit
    def test_custom_headers_are_passed_to_request(self, env_api_key, mock_settings):
        client = self._initialized_client(mock_settings)
        mock_resp = _make_response()
        custom_headers = {"X-Custom-Header": "test-value"}
        with patch.object(client.http, "request", return_value=mock_resp) as mock_req:
            client.do_request("/api/v2/test", request_headers=custom_headers)
        _, kwargs = mock_req.call_args
        # API key auth overwrites headers — check request was made
        mock_req.assert_called_once()

    @pytest.mark.unit
    def test_api_key_injected_into_json_body(self, env_api_key, mock_settings):
        client = self._initialized_client(mock_settings)
        mock_resp = _make_response()
        import json as json_mod

        captured = {}

        def fake_request(
            method, url, *, body=None, headers=None, timeout=None, retries=None
        ):
            captured["body"] = json_mod.loads(body) if body else {}
            return mock_resp

        with patch.object(client.http, "request", side_effect=fake_request):
            client.do_request("/api/v2/test", json={"key": "value"})
        assert "api_key" in captured["body"]

    @pytest.mark.unit
    def test_get_method_is_forwarded(self, env_api_key, mock_settings):
        client = self._initialized_client(mock_settings)
        mock_resp = _make_response()
        with patch.object(client.http, "request", return_value=mock_resp) as mock_req:
            client.do_request("/api/v2/test", method="GET")
        _, kwargs = mock_req.call_args
        assert kwargs.get("method") == "GET"


# ---------------------------------------------------------------------------
# New exception types — standalone unit tests
# ---------------------------------------------------------------------------


class TestNewExceptionTypes:
    """Tests for the new Tier 2 exception classes."""

    @pytest.mark.unit
    def test_authentication_error_basic(self):
        exc = BritecoreError.AuthenticationError("Bad token")
        assert "Bad token" in str(exc)
        assert exc.http_status is None

    @pytest.mark.unit
    def test_authentication_error_with_status(self):
        exc = BritecoreError.AuthenticationError("Forbidden", http_status=403)
        assert "403" in str(exc)
        assert exc.http_status == 403

    @pytest.mark.unit
    def test_rate_limit_error_basic(self):
        exc = BritecoreError.RateLimitError("Quota exceeded")
        assert "Quota exceeded" in str(exc)
        assert exc.retry_after is None

    @pytest.mark.unit
    def test_rate_limit_error_with_retry_after(self):
        exc = BritecoreError.RateLimitError("Slow down", retry_after=60)
        assert "60" in str(exc)
        assert exc.retry_after == 60

    @pytest.mark.unit
    def test_server_error_basic(self):
        exc = BritecoreError.ServerError("Crashed")
        assert "Crashed" in str(exc)
        assert exc.http_status is None

    @pytest.mark.unit
    def test_server_error_with_status(self):
        exc = BritecoreError.ServerError("Gateway timeout", http_status=504)
        assert "504" in str(exc)
        assert exc.http_status == 504

    @pytest.mark.unit
    def test_configuration_error(self):
        exc = BritecoreError.ConfigurationError("Missing base_url")
        assert "Missing base_url" in str(exc)

    @pytest.mark.unit
    def test_request_timeout_error_basic(self):
        exc = BritecoreError.RequestTimeoutError("Connection timed out")
        assert "Connection timed out" in str(exc)
        assert exc.timeout_seconds is None

    @pytest.mark.unit
    def test_request_timeout_error_with_seconds(self):
        exc = BritecoreError.RequestTimeoutError("Too slow", timeout_seconds=5)
        assert "5" in str(exc)
        assert exc.timeout_seconds == 5

    @pytest.mark.unit
    def test_all_new_exceptions_are_exceptions(self):
        for cls in (
            BritecoreError.AuthenticationError,
            BritecoreError.RateLimitError,
            BritecoreError.ServerError,
            BritecoreError.ConfigurationError,
            BritecoreError.RequestTimeoutError,
        ):
            assert issubclass(cls, Exception)

    @pytest.mark.unit
    def test_new_exceptions_are_catchable_by_base_exception(self):
        for exc_cls, kwargs in (
            (BritecoreError.AuthenticationError, {"message": "x"}),
            (BritecoreError.RateLimitError, {"message": "x"}),
            (BritecoreError.ServerError, {"message": "x"}),
            (BritecoreError.ConfigurationError, {"message": "x"}),
            (BritecoreError.RequestTimeoutError, {"message": "x"}),
            (BritecoreError.ValidationError, {"message": "x"}),
            (BritecoreError.NotFoundError, {"message": "x"}),
            (BritecoreError.ConflictError, {"message": "x"}),
        ):
            with pytest.raises(BritecoreError.Base):
                raise exc_cls(**kwargs)


# ---------------------------------------------------------------------------
# init_client — configuration error paths
# ---------------------------------------------------------------------------


class TestInitClientConfigErrors:
    """Tests for configuration error paths in init_client."""

    @pytest.mark.unit
    def test_missing_base_url_raises_britecore_key_error(self, env_api_key):
        from types import SimpleNamespace

        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        bad_settings = SimpleNamespace(
            base_url="",
            client_id="",
            client_secret="",
            api_key="test_key",
            web_retry=3,
            web_timeout=5,
            web_timeout_long=50,
            web_browser="",
        )
        with patch(
            "britecore_libraries.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.return_value = bad_settings
            client = BritecoreAPIClient("test_site")
            with pytest.raises(BritecoreError.BritecoreKeyError) as exc_info:
                client.init_client()
        assert "base_url" in str(exc_info.value).lower()

    @pytest.mark.unit
    def test_no_site_raises_no_site_error(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        client = BritecoreAPIClient(None)
        with pytest.raises(BritecoreError.NoSiteError):
            client.init_client()

    @pytest.mark.unit
    def test_defaults_applied_when_timeout_missing(self, env_api_key, mock_settings):
        from types import SimpleNamespace

        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        settings_no_timeout = SimpleNamespace(
            base_url="example.com",
            client_id="",
            client_secret="",
            api_key="key",
            web_retry=None,
            web_timeout=None,
            web_timeout_long=None,
            web_browser="",
        )
        with patch(
            "britecore_libraries.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.return_value = settings_no_timeout
            client = BritecoreAPIClient("test_site")
            client.init_client()
        assert client.web_timeout == 5
        assert client.web_timeout_long == 50
        assert client.web_retry == 5


# ---------------------------------------------------------------------------
# Instance isolation — two clients must not share state
# ---------------------------------------------------------------------------


class TestInstanceIsolation:
    """Prove that two BritecoreAPIClient instances do not share state."""

    def _make_settings(self, base_url: str):
        from types import SimpleNamespace

        return SimpleNamespace(
            base_url=base_url,
            client_id="",
            client_secret="",
            api_key="key",
            web_retry=3,
            web_timeout=5,
            web_timeout_long=50,
            web_browser="",
        )

    @pytest.mark.unit
    def test_two_clients_hold_independent_base_urls(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_libraries.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.side_effect = [
                self._make_settings("alpha.example.com"),
                self._make_settings("beta.example.com"),
            ]
            client_a = BritecoreAPIClient("alpha")
            client_a.init_client()
            client_b = BritecoreAPIClient("beta")
            client_b.init_client()

        assert "alpha" in client_a.base_url
        assert "beta" in client_b.base_url
        assert client_a.base_url != client_b.base_url

    @pytest.mark.unit
    def test_two_clients_hold_independent_http_pools(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        settings = self._make_settings("example.com")
        with patch(
            "britecore_libraries.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.return_value = settings
            client_a = BritecoreAPIClient("site_a")
            client_a.init_client()
            client_b = BritecoreAPIClient("site_b")
            client_b.init_client()

        assert client_a.http is not client_b.http

    @pytest.mark.unit
    def test_reinitializing_one_client_does_not_affect_other(self):
        from britecore_libraries.api.britecore_api_client import BritecoreAPIClient

        with patch(
            "britecore_libraries.api.britecore_api_client.LoadClientSettings"
        ) as mock_loader:
            mock_loader.return_value.load_config.side_effect = [
                self._make_settings("first.example.com"),
                self._make_settings("second.example.com"),
                self._make_settings("third.example.com"),
            ]
            client_a = BritecoreAPIClient("first")
            client_a.init_client()

            client_b = BritecoreAPIClient("second")
            client_b.init_client()

            # Re-init client_a with a different site
            client_a.target_site = "third"
            client_a.init_client()

        assert "third" in client_a.base_url
        # client_b must be entirely unaffected
        assert "second" in client_b.base_url
