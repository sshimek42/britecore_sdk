"""Unit tests for check_test_data utility script."""

from pathlib import Path

import pytest

from britecore_libraries.utils import check_test_data


@pytest.mark.unit
def test_check_test_data_files_returns_true_when_data_dir_missing(monkeypatch, capsys):
    """Missing tests/data directory is treated as a no-op success."""
    monkeypatch.setattr(check_test_data.os.path, "exists", lambda _path: False)

    assert check_test_data.check_test_data_files() is True
    assert "No test data directory found" in capsys.readouterr().out


@pytest.mark.unit
def test_check_test_data_files_returns_false_on_parse_error(monkeypatch, capsys):
    """Parsing/open failures are reported and produce a failed status."""
    monkeypatch.setattr(check_test_data.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(check_test_data.glob, "glob", lambda _path: ["broken.csv"])

    def fake_open(*_args, **_kwargs):
        raise OSError("boom")

    monkeypatch.setattr("builtins.open", fake_open)

    assert check_test_data.check_test_data_files() is False
    assert "ERROR: Could not parse broken.csv" in capsys.readouterr().out


@pytest.mark.unit
def test_check_test_data_files_success_for_valid_csv(
    monkeypatch, tmp_path: Path, capsys
):
    """A valid CSV list is parsed and reported as successful."""
    csv_file = tmp_path / "ok.csv"
    csv_file.write_text("a,b\n1,2\n", encoding="utf-8")

    monkeypatch.setattr(check_test_data.os.path, "exists", lambda _path: True)
    monkeypatch.setattr(check_test_data.glob, "glob", lambda _path: [str(csv_file)])

    assert check_test_data.check_test_data_files() is True
    assert "All test data files are present and parseable." in capsys.readouterr().out


@pytest.mark.unit
def test_main_exits_non_zero_when_validation_fails(monkeypatch):
    """main exits with code 1 when check_test_data_files reports failure."""
    monkeypatch.setattr(check_test_data, "check_test_data_files", lambda: False)

    with pytest.raises(SystemExit) as exc:
        check_test_data.main()

    assert exc.value.code == 1


@pytest.mark.unit
def test_main_returns_normally_when_validation_passes(monkeypatch):
    """main does not exit when check_test_data_files succeeds."""
    monkeypatch.setattr(check_test_data, "check_test_data_files", lambda: True)

    check_test_data.main()
