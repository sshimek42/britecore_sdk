"""Integration-test fixtures and sandbox detection.

Live-API tests are skipped automatically when the required environment
variables are not present.  Set the following to run the live suite:

    BRITECORE_INTEGRATION_TESTS=true
    BRITECORE_SANDBOX_URL=https://<your-sandbox>.britecore.com
    BRITECORE_SANDBOX_API_KEY=<key>          # API-key auth
    # OR
    BRITECORE_SANDBOX_CLIENT_ID=<id>         # OAuth auth
    BRITECORE_SANDBOX_CLIENT_SECRET=<secret>
"""

import os
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Sandbox availability helpers
# ---------------------------------------------------------------------------

def _sandbox_available() -> bool:
    """Return True when all required env vars for live tests are present."""
    return bool(
        os.environ.get("BRITECORE_INTEGRATION_TESTS", "").lower() == "true"
        and os.environ.get("BRITECORE_SANDBOX_URL")
        and (
            os.environ.get("BRITECORE_SANDBOX_API_KEY")
            or (
                os.environ.get("BRITECORE_SANDBOX_CLIENT_ID")
                and os.environ.get("BRITECORE_SANDBOX_CLIENT_SECRET")
            )
        )
    )


requires_sandbox = pytest.mark.skipif(
    not _sandbox_available(),
    reason=(
        "Live integration tests require BRITECORE_INTEGRATION_TESTS=true and "
        "BRITECORE_SANDBOX_URL + auth credentials to be set."
    ),
)


# ---------------------------------------------------------------------------
# Mock response factories
# ---------------------------------------------------------------------------

def _mock_response(data: dict, status: int = 200) -> MagicMock:
    """Build a mock HTTP response wrapping *data* in the standard envelope."""
    import json

    envelope = {"success": True, "data": data, "message": "OK"}
    resp = MagicMock()
    resp.status = status
    resp.reason = "OK"
    resp.data = json.dumps(envelope).encode()
    return resp


def _mock_error_response(message: str = "Not found", status: int = 400) -> MagicMock:
    import json

    envelope = {"success": False, "message": message, "data": {}}
    resp = MagicMock()
    resp.status = status
    resp.reason = message
    resp.data = json.dumps(envelope).encode()
    return resp


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def ok_response():
    """Generic successful response with a simple data payload."""
    return _mock_response({"id": "test-id-001", "status": "active"})


@pytest.fixture
def error_response():
    """Generic 400 error response."""
    return _mock_error_response()


@pytest.fixture
def server_error_response():
    """HTTP 500 response."""
    resp = MagicMock()
    resp.status = 500
    resp.reason = "Internal Server Error"
    resp.data = b'{"success": false, "message": "Internal Server Error"}'
    return resp


@pytest.fixture
def rate_limit_response():
    """HTTP 429 response with Retry-After header."""
    resp = MagicMock()
    resp.status = 429
    resp.reason = "Too Many Requests"
    resp.headers = {"Retry-After": "30"}
    resp.data = b'{"success": false, "message": "Too Many Requests"}'
    return resp

