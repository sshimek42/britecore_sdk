"""Shared pytest fixtures and configuration."""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

pytest_plugins = ["tests.fixtures.api_fixtures"]

# Add src to path at module load time
src_path = str(Path(__file__).parent.parent / "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)


@pytest.fixture
def default_system_env(monkeypatch):
    """Default system for tests that rely on map regex loading."""
    monkeypatch.setenv("system", "mips")
    yield


@pytest.fixture(autouse=True)
def _apply_default_system_env(default_system_env):
    """Autouse wrapper to apply default system unless a test overrides it."""
    yield


@pytest.fixture
def mock_settings():
    """Mock Dynaconf settings object."""
    settings = MagicMock()
    settings.base_url = "https://api.example.com"
    settings.client_id = ""
    settings.client_secret = ""
    settings.api_key = "test_api_key_12345"
    settings.web_timeout = 5
    settings.web_timeout_long = 50
    settings.web_retry = 5
    settings.write_policy = "allow"
    settings.write_allowlist = []
    settings.write_denylist = []
    settings.enable_audit_middleware = False
    settings.audit_only_writes = True
    settings.audit_log_level = "info"
    return settings


@pytest.fixture
def mock_settings_oauth():
    """Mock Dynaconf settings object with OAuth credentials."""
    settings = MagicMock()
    settings.base_url = "https://api.example.com"
    settings.client_id = "test_client_id"
    settings.client_secret = "test_client_secret"
    settings.web_timeout = 5
    settings.web_timeout_long = 50
    settings.web_retry = 5
    settings.write_policy = "allow"
    settings.write_allowlist = []
    settings.write_denylist = []
    settings.enable_audit_middleware = False
    settings.audit_only_writes = True
    settings.audit_log_level = "info"
    return settings


@pytest.fixture
def mock_http_response():
    """Mock successful HTTP response."""
    response = MagicMock()
    response.status = 200
    response.data = (
        b'{"success": true, "data": {"id": "test_id", "name": "test"}, "message": "OK"}'
    )
    response.reason = "OK"
    return response


@pytest.fixture
def mock_http_response_error():
    """Mock error HTTP response."""
    response = MagicMock()
    response.status = 400
    response.data = b'{"success": false, "message": "Bad Request"}'
    response.reason = "Bad Request"
    return response


@pytest.fixture
def mock_oauth_response():
    """Mock OAuth token response."""
    response = MagicMock()
    response.status = 200
    response.data = b'{"access_token": "test_token_xyz", "expires_in": 3600, "token_type": "Bearer"}'
    return response


@pytest.fixture
def mock_oauth_response_error():
    """Mock OAuth error response."""
    response = MagicMock()
    response.status = 401
    response.data = b'{"error": "invalid_client"}'
    return response


@pytest.fixture
def tmp_config_file(tmp_path):
    """Create a temporary TOML config file for testing."""
    config_content = """
[default]
base_url = "https://api.example.com"
web_timeout = 5
web_timeout_long = 50
web_retry = 3

[test_site]
base_url = "https://test_site.api.example.com"
client_id = "test_client"
client_secret = "test_secret"
api_key = "test_api_key"
"""
    config_file = tmp_path / "test_config.toml"
    config_file.write_text(config_content)
    return config_file


@pytest.fixture
def env_api_key(monkeypatch):
    """Set up environment with API key auth."""
    monkeypatch.setenv("target_site", "test_site")
    monkeypatch.setenv("system", "mips")
    yield
    monkeypatch.delenv("target_site", raising=False)
    monkeypatch.delenv("system", raising=False)


@pytest.fixture
def env_oauth(monkeypatch):
    """Set up environment with OAuth."""
    monkeypatch.setenv("target_site", "test_site")
    monkeypatch.setenv("system", "spectrum_v1")
    yield
    monkeypatch.delenv("target_site", raising=False)
    monkeypatch.delenv("system", raising=False)


@pytest.fixture
def env_no_system(monkeypatch):
    """Set up environment without system variable (load_regexes will raise ValueError)."""
    monkeypatch.delenv("system", raising=False)
    yield
    monkeypatch.delenv("system", raising=False)


@pytest.fixture(autouse=True)
def mock_api_client(monkeypatch):
    """
    Autouse fixture to mock Britecore API client initialization and singleton for all tests.
    Prevents ConfigurationError due to missing config and allows API calls to be intercepted.
    """
    # Reuse one client mock across tests so modules that cache API_CLIENT at
    # import-time keep pointing to the same object.
    if not hasattr(mock_api_client, "_shared_client"):
        mock_api_client._shared_client = MagicMock(name="api_client")

    shared_client = mock_api_client._shared_client
    shared_client.reset_mock()

    with patch(
        "britecore_sdk.api.api_calls.init_api_client", return_value=shared_client
    ):
        with patch("britecore_sdk.api.api_calls.api_client", new=shared_client):
            with patch(
                "britecore_sdk.api.api_calls.get_api_client",
                return_value=shared_client,
            ):
                yield shared_client
