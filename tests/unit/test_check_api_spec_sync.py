"""Unit tests for utils/check_api_spec_sync.py."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from britecore_sdk.utils.check_api_spec_sync import (
    SPEC_PATH,
    check_spec_exists_and_fresh,
    get_local_spec_version,
    get_remote_spec_version,
    has_newer_remote_spec,
    is_newer_version,
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
        with (
            patch(
                "britecore_sdk.utils.check_api_spec_sync.check_spec_exists_and_fresh",
                return_value=True,
            ),
            patch(
                "britecore_sdk.utils.check_api_spec_sync.has_newer_remote_spec",
                return_value=(False, "2.0.0", "2.0.0"),
            ),
        ):
            main()  # should NOT raise SystemExit

        out = capsys.readouterr().out
        assert "matches upstream" in out

    def test_exits_one_when_file_missing(self):
        with (
            patch(
                "britecore_sdk.utils.check_api_spec_sync.check_spec_exists_and_fresh",
                return_value=False,
            ),
            patch(
                "britecore_sdk.utils.check_api_spec_sync.has_newer_remote_spec",
                return_value=(False, "2.0.0", "2.0.0"),
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
            patch(
                "britecore_sdk.utils.check_api_spec_sync.has_newer_remote_spec",
                return_value=(False, "2.0.0", "2.0.0"),
            ),
            pytest.raises(SystemExit),
        ):
            main()

        out = capsys.readouterr().out
        assert "update" in out.lower() or "britecore.json" in out

    def test_prints_checking_message(self, capsys):
        with (
            patch(
                "britecore_sdk.utils.check_api_spec_sync.check_spec_exists_and_fresh",
                return_value=True,
            ),
            patch(
                "britecore_sdk.utils.check_api_spec_sync.has_newer_remote_spec",
                return_value=(False, "2.0.0", "2.0.0"),
            ),
        ):
            main()

        assert "Checking" in capsys.readouterr().out

    def test_exits_one_when_newer_remote_spec_exists(self, capsys):
        with (
            patch(
                "britecore_sdk.utils.check_api_spec_sync.check_spec_exists_and_fresh",
                return_value=True,
            ),
            patch(
                "britecore_sdk.utils.check_api_spec_sync.has_newer_remote_spec",
                return_value=(True, "2.0.0", "2.1.0"),
            ),
            pytest.raises(SystemExit) as exc,
        ):
            main()

        out = capsys.readouterr().out
        assert exc.value.code == 1
        assert "newer upstream API spec is available" in out
        assert "2.0.0 -> 2.1.0" in out

    def test_warns_when_remote_version_unavailable(self, capsys):
        with (
            patch(
                "britecore_sdk.utils.check_api_spec_sync.check_spec_exists_and_fresh",
                return_value=True,
            ),
            patch(
                "britecore_sdk.utils.check_api_spec_sync.has_newer_remote_spec",
                return_value=(False, "2.0.0", None),
            ),
        ):
            main()

        out = capsys.readouterr().out
        assert "Could not fetch upstream API spec version" in out


# ---------------------------------------------------------------------------
# Spec path constant sanity check
# ---------------------------------------------------------------------------


def test_spec_path_points_to_expected_location():
    """SPEC_PATH should resolve inside api_specs/current/."""
    assert "api_specs" in str(SPEC_PATH)
    assert SPEC_PATH.name == "britecore.json"


def test_is_newer_version_semverish_compare():
    assert is_newer_version("2.0.0", "2.0.1") is True
    assert is_newer_version("2.0.0", "2.0.0") is False
    assert is_newer_version("2.1", "2.0.9") is False
    assert is_newer_version("v2.0.0", "2.0.1-beta1") is True
    assert is_newer_version("unknown", "2.0.1") is False


def test_get_local_spec_version_reads_info_version(tmp_path: Path):
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps({"info": {"version": "2.0.7"}}), encoding="utf-8")
    assert get_local_spec_version(spec_file) == "2.0.7"


def test_get_remote_spec_version_reads_info_version():
    class _DummyResponse:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b'{"info": {"version": "2.3.0"}}'

    with patch(
        "britecore_sdk.utils.check_api_spec_sync.urlopen",
        return_value=_DummyResponse(),
    ):
        assert get_remote_spec_version("https://example.com/spec.json") == "2.3.0"


def test_has_newer_remote_spec_true(monkeypatch, tmp_path: Path):
    spec_file = tmp_path / "spec.json"
    spec_file.write_text(json.dumps({"info": {"version": "2.0.0"}}), encoding="utf-8")

    monkeypatch.setattr(
        "britecore_sdk.utils.check_api_spec_sync.get_remote_spec_version",
        lambda spec_url, timeout_seconds=10.0: "2.1.0",
    )

    has_newer, local_version, remote_version = has_newer_remote_spec(
        spec_path=spec_file,
        spec_url="https://example.com/spec.json",
    )
    assert has_newer is True
    assert local_version == "2.0.0"
    assert remote_version == "2.1.0"
