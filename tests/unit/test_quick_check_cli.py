"""Unit tests for the britecore-quick-check CLI modes."""

from unittest.mock import patch

import pytest

from britecore_sdk.cli.quick_check import main


@pytest.mark.unit
def test_main_defaults_to_full_mode(capsys):
    """CLI defaults to full mode when no mode flag is provided."""
    with patch(
        "britecore_sdk.cli.quick_check._check_full_health",
        return_value=(True, ["ok-full"]),
    ) as mock_full:
        code = main([])

    assert code == 0
    mock_full.assert_called_once_with()
    assert "ok-full" in capsys.readouterr().out


@pytest.mark.unit
def test_main_syntax_mode_dispatch(capsys):
    """CLI dispatches to syntax checks when --syntax is passed."""
    with patch(
        "britecore_sdk.cli.quick_check._check_syntax",
        return_value=(True, ["ok-syntax"]),
    ) as mock_syntax:
        code = main(["--syntax"])

    assert code == 0
    mock_syntax.assert_called_once_with()
    assert "ok-syntax" in capsys.readouterr().out


@pytest.mark.unit
def test_main_connectivity_mode_dispatch(capsys):
    """CLI dispatches to connectivity checks when --connectivity is passed."""
    with patch(
        "britecore_sdk.cli.quick_check._check_connectivity",
        return_value=(True, ["ok-connectivity"]),
    ) as mock_connectivity:
        code = main(["--connectivity"])

    assert code == 0
    mock_connectivity.assert_called_once_with()
    assert "ok-connectivity" in capsys.readouterr().out


@pytest.mark.unit
def test_main_full_mode_dispatch(capsys):
    """CLI dispatches to full health checks when --full is passed."""
    with patch(
        "britecore_sdk.cli.quick_check._check_full_health",
        return_value=(True, ["ok-full"]),
    ) as mock_full:
        code = main(["--full"])

    assert code == 0
    mock_full.assert_called_once_with()
    assert "ok-full" in capsys.readouterr().out


@pytest.mark.unit
def test_main_returns_nonzero_when_check_fails(capsys):
    """CLI returns non-zero and prints failure output when selected check fails."""
    with patch(
        "britecore_sdk.cli.quick_check._check_connectivity",
        return_value=(False, ["failed-connectivity"]),
    ):
        code = main(["--connectivity"])

    assert code == 1
    assert "failed-connectivity" in capsys.readouterr().out


@pytest.mark.unit
def test_main_handles_runtime_exception_and_returns_nonzero(capsys):
    """CLI catches runtime errors in check execution and reports a user-facing message."""
    with patch(
        "britecore_sdk.cli.quick_check._check_syntax",
        side_effect=RuntimeError("boom"),
    ):
        code = main(["--syntax"])

    assert code == 1
    assert "Unexpected error: boom" in capsys.readouterr().out


@pytest.mark.unit
def test_main_verbose_logs_exception():
    """Verbose mode logs the exception traceback when check execution fails."""
    with (
        patch(
            "britecore_sdk.cli.quick_check._check_syntax",
            side_effect=RuntimeError("boom"),
        ),
        patch("britecore_sdk.cli.quick_check.logger.exception") as mock_log,
    ):
        code = main(["--syntax", "--verbose"])

    assert code == 1
    mock_log.assert_called_once_with("Quick check failed with exception")


@pytest.mark.unit
def test_mode_flags_are_mutually_exclusive():
    """CLI rejects conflicting mode flags so dispatch behavior is unambiguous."""
    with pytest.raises(SystemExit) as exc:
        main(["--syntax", "--connectivity"])

    assert exc.value.code == 2
