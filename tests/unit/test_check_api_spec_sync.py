"""Unit tests for utils/check_api_spec_sync.py.

Covers:
  - check_spec_exists_and_fresh(): file missing, stale, and fresh
  - main(): success, missing-file exit, stale-file exit
"""

from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from britecore_sdk.utils.check_api_spec_sync import (
    SPEC_PATH,
    check_spec_exists_and_fresh,
    main,
)

# ---------------------------------------------------------------------------
# check_spec_exists_and_fresh
# ---------------------------------------------------------------------------


class TestCheckSpecExistsAndFresh:
    def test_returns_false_when_file_missing(self, capsys):
        with patch.object(Path, "exists", return_value=False):
            result = check_spec_exists_and_fresh()

        assert result is False
        assert "missing" in capsys.readouterr().out

    def test_returns_true_when_file_is_recent(self):
        fresh_stat = MagicMock()
        fresh_stat.st_mtime = (datetime.now() - timedelta(days=5)).timestamp()

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "stat", return_value=fresh_stat),
        ):
            result = check_spec_exists_and_fresh()

        assert result is True

    def test_returns_false_when_file_is_stale(self, capsys):
        stale_stat = MagicMock()
        stale_stat.st_mtime = (datetime.now() - timedelta(days=45)).timestamp()

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "stat", return_value=stale_stat),
        ):
            result = check_spec_exists_and_fresh()

        assert result is False
        assert "older than 30 days" in capsys.readouterr().out

    def test_exactly_31_days_old_is_stale(self, capsys):
        """31-day-old file → age_days > 30 → stale."""
        border_stat = MagicMock()
        border_stat.st_mtime = (datetime.now() - timedelta(days=31)).timestamp()

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "stat", return_value=border_stat),
        ):
            result = check_spec_exists_and_fresh()

        assert result is False

    def test_fresh_file_produces_no_warning(self, capsys):
        fresh_stat = MagicMock()
        fresh_stat.st_mtime = (datetime.now() - timedelta(days=1)).timestamp()

        with (
            patch.object(Path, "exists", return_value=True),
            patch.object(Path, "stat", return_value=fresh_stat),
        ):
            check_spec_exists_and_fresh()

        assert capsys.readouterr().out == ""


# ---------------------------------------------------------------------------
# main()
# ---------------------------------------------------------------------------


class TestMain:
    def test_exits_zero_and_prints_success_when_fresh(self, capsys):
        with patch(
            "britecore_sdk.utils.check_api_spec_sync.check_spec_exists_and_fresh",
            return_value=True,
        ):
            main()  # should NOT raise SystemExit

        out = capsys.readouterr().out
        assert "recent" in out or "exists" in out

    def test_exits_one_when_file_missing(self):
        with (
            patch(
                "britecore_sdk.utils.check_api_spec_sync.check_spec_exists_and_fresh",
                return_value=False,
            ),
            pytest.raises(SystemExit) as exc,
        ):
            main()

        assert exc.value.code == 1

    def test_prints_update_message_on_failure(self, capsys):
        with (
            patch(
                "britecore_sdk.utils.check_api_spec_sync.check_spec_exists_and_fresh",
                return_value=False,
            ),
            pytest.raises(SystemExit),
        ):
            main()

        out = capsys.readouterr().out
        assert "update" in out.lower() or "britecore.json" in out

    def test_prints_checking_message(self, capsys):
        with patch(
            "britecore_sdk.utils.check_api_spec_sync.check_spec_exists_and_fresh",
            return_value=True,
        ):
            main()

        assert "Checking" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Spec path constant sanity check
# ---------------------------------------------------------------------------


def test_spec_path_points_to_expected_location():
    """SPEC_PATH should resolve inside api_specs/current/."""
    assert "api_specs" in str(SPEC_PATH)
    assert SPEC_PATH.name == "britecore.json"
