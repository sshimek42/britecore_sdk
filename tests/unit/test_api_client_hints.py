"""Tests for actionable hint text in API client exceptions."""

from unittest.mock import MagicMock, patch

import pytest
from urllib3.exceptions import TimeoutError as urlTimeoutError

from britecore_sdk.api.britecore_api_client import BritecoreAPIClient
from britecore_sdk.exceptions import BritecoreError


def _initialized_client(mock_settings):
    with patch("britecore_sdk.api.britecore_api_client.LoadClientSettings") as loader:
        loader_instance = MagicMock()
        loader_instance.load_config.return_value = mock_settings
        loader.return_value = loader_instance
        client = BritecoreAPIClient("test_site")
        client.init_client()
    return client


@pytest.mark.unit
def test_timeout_error_includes_hint(env_api_key, mock_settings):
    """Timeout errors include a short actionable hint for end users."""
    client = _initialized_client(mock_settings)
    with (
        patch.object(client.http, "request", side_effect=urlTimeoutError("timed out")),
        pytest.raises(BritecoreError.RequestTimeoutError) as exc_info,
    ):
        client.do_request("/api/v2/test")

    message = str(exc_info.value)
    assert "Hint:" in message
    assert "request_timeout" in message


@pytest.mark.unit
def test_process_result_no_response_includes_hint():
    """No-response error paths include a troubleshooting hint."""
    with pytest.raises(BritecoreError.NoDataReturned) as exc_info:
        BritecoreAPIClient.process_result(None, endpoint="/api/v2/test")

    message = str(exc_info.value)
    assert "Hint:" in message
    assert "network reachability" in message.lower()


@pytest.mark.unit
def test_authentication_error_includes_healthcheck_hint():
    """Authentication failures include healthcheck guidance."""
    response = MagicMock()
    response.status = 401
    response.reason = "Unauthorized"
    response.data = b'{"success": false, "message": "Unauthorized"}'
    response.headers = {}

    with pytest.raises(BritecoreError.AuthenticationError) as exc_info:
        BritecoreAPIClient.process_result(response, endpoint="/api/v2/test")

    message = str(exc_info.value)
    assert "Hint:" in message
    assert "healthcheck" in message.lower()
