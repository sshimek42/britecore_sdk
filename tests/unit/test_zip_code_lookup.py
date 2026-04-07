"""Unit tests for ZIP code lookup utilities."""

from pathlib import Path

import pytest

from britecore_libraries.utils import zip_code_lookup
from britecore_libraries.utils.zip_code_lookup import ZipCodeLookup, load_zip_codes


@pytest.mark.unit
def test_load_zip_codes_from_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Load a small CSV fixture and verify state/city and ZIP lookups."""
    csv_file = tmp_path / "zip_codes.csv"
    csv_file.write_text(
        "country code,postal code,place name,admin name1,admin code1,admin name2,admin code2,latitude,longitude\n"
        "US,62701,Springfield,Illinois,IL,Sangamon,,39.8,-89.6\n"
        "US,53202,Milwaukee,Wisconsin,WI,Milwaukee,,43.0,-87.9\n",
        encoding="utf-8",
    )

    monkeypatch.setattr(zip_code_lookup, "import_file", csv_file)

    lookup = load_zip_codes()

    assert isinstance(lookup, ZipCodeLookup)
    assert lookup.get_zip_by_state_city("IL", "Springfield") == "62701"
    assert lookup.get_record_by_zip("53202").admin_name2 == "Milwaukee"


@pytest.mark.unit
def test_load_zip_codes_missing_file_logs_and_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Missing ZIP CSV should raise and emit an error log."""
    missing_csv = tmp_path / "does_not_exist.csv"
    monkeypatch.setattr(zip_code_lookup, "import_file", missing_csv)

    with pytest.raises(FileNotFoundError):
        load_zip_codes()

    assert "Zip Code lookup file is missing" in caplog.text

