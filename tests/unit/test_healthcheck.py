"""Unit tests for healthcheck utility."""

from unittest.mock import patch

import pytest

from britecore_libraries.exceptions import BritecoreError
from britecore_libraries.utils.healthcheck import (
    HealthcheckResult,
    _format_result,
    main,
    run_healthcheck,
)


@pytest.mark.unit
def test_run_healthcheck_config_failure() -> None:
    """Healthcheck returns a failed result when client init fails."""
    with patch(
        "britecore_libraries.utils.healthcheck.init_api_client",
        side_effect=BritecoreError.ConfigurationError("bad config"),
    ):
        result = run_healthcheck("demo-site")

    assert isinstance(result, HealthcheckResult)
    assert result.ok is False
    assert result.config_ok is False
    assert result.api_ok is False
    assert result.auth_mode == "unknown"
    assert "bad config" in result.message


@pytest.mark.unit
def test_run_healthcheck_skip_ping_success() -> None:
    """Healthcheck can validate config-only mode without API ping."""
    with patch("britecore_libraries.utils.healthcheck.init_api_client") as mock_init:
        client = mock_init.return_value
        client.use_api_key = True
        result = run_healthcheck("demo-site", ping=False)

    assert result.ok is True
    assert result.config_ok is True
    assert result.api_ok is True
    assert result.auth_mode == "api_key"


@pytest.mark.unit
def test_run_healthcheck_ping_failure() -> None:
    """Healthcheck reports API failure when ping call raises SDK error."""
    with (
        patch("britecore_libraries.utils.healthcheck.init_api_client") as mock_init,
        patch(
            "britecore_libraries.utils.healthcheck.v2_utils.get_release_info",
            side_effect=BritecoreError.AuthenticationError("unauthorized"),
        ),
    ):
        client = mock_init.return_value
        client.use_api_key = False
        result = run_healthcheck("demo-site")

    assert result.ok is False
    assert result.config_ok is True
    assert result.api_ok is False
    assert result.auth_mode == "oauth"
    assert "unauthorized" in result.message.lower()


@pytest.mark.unit
def test_run_healthcheck_ping_success_calls_expected_endpoint() -> None:
    """Healthcheck calls the expected safe endpoint for API ping."""
    with (
        patch("britecore_libraries.utils.healthcheck.init_api_client") as mock_init,
        patch(
            "britecore_libraries.utils.healthcheck.v2_utils.get_release_info",
            return_value={"ok": True},
        ) as mock_get_release_info,
    ):
        client = mock_init.return_value
        client.use_api_key = True
        result = run_healthcheck("demo-site")

    assert result.ok is True
    mock_get_release_info.assert_called_once_with()


@pytest.mark.unit
def test_main_returns_nonzero_on_failure() -> None:
    """CLI entrypoint returns 1 for failed healthcheck runs."""
    with patch(
        "britecore_libraries.utils.healthcheck.run_healthcheck",
        return_value=HealthcheckResult(
            ok=False,
            site="demo-site",
            auth_mode="unknown",
            config_ok=False,
            api_ok=False,
            message="failure",
        ),
    ):
        code = main(["--site", "demo-site"])

    assert code == 1


@pytest.mark.unit
def test_format_result_contains_sections() -> None:
    """Formatted output includes all key status sections."""
    text = _format_result(
        HealthcheckResult(
            ok=True,
            site="demo-site",
            auth_mode="api_key",
            config_ok=True,
            api_ok=True,
            message="ok",
        )
    )
    assert "Healthcheck: OK" in text
    assert "Site: demo-site" in text
    assert "Auth mode: api_key" in text
    assert "Config: OK" in text
    assert "API ping: OK" in text
