import csv
import logging
from dataclasses import dataclass
from logging import Logger
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    logger: logging.Logger
else:
    from britecore_libraries import logger

LOGGER: Logger = logger

import_file: Path = Path(Path(__file__).parent / "../resources" / "zip_codes.csv")


@dataclass(frozen=True)
class ZipRecord:
    """Normalized ZIP code row used by address validation lookups."""

    postal_code: str
    place_name: str
    admin_code1: str
    admin_name2: str


class ZipCodeLookup:
    """In-memory ZIP index optimized for exact ZIP and city/state lookups."""

    def __init__(self, rows: list[dict[str, str]]) -> None:
        self._records_by_zip: dict[str, ZipRecord] = {}
        self._zip_by_state_city: dict[tuple[str, str], str] = {}

        for row in rows:
            record = ZipRecord(
                postal_code=(row.get("postal code") or "").strip(),
                place_name=(row.get("place name") or "").strip(),
                admin_code1=(row.get("admin code1") or "").strip().upper(),
                admin_name2=(row.get("admin name2") or "").strip(),
            )

            if not record.postal_code:
                continue

            self._records_by_zip.setdefault(record.postal_code, record)

            state_city_key = (record.admin_code1, record.place_name.title())
            self._zip_by_state_city.setdefault(state_city_key, record.postal_code)

    def get_record_by_zip(self, zipcode: str) -> ZipRecord | None:
        """Return the first matching record for a 5-digit ZIP code."""
        return self._records_by_zip.get((zipcode or "")[:5])

    def get_zip_by_state_city(self, state: str, city: str) -> str | None:
        """Return a ZIP code for a state/city pair when exact ZIP is missing."""
        key = ((state or "").strip().upper(), (city or "").strip().title())
        return self._zip_by_state_city.get(key)


def load_zip_codes() -> ZipCodeLookup:
    """
    Load ZIP code data from CSV into an in-memory lookup.

    Returns
    -------
    ZipCodeLookup
        Lookup object containing normalized ZIP records.

    Raises
    ------
    FileNotFoundError
        If the specified CSV file is not found at the given path.
    """
    try:
        with import_file.open("r", encoding="utf-8", newline="") as csv_file:
            loaded_zip_codes = list(csv.DictReader(csv_file))
    except FileNotFoundError:
        LOGGER.error("Zip Code lookup file is missing")
        raise

    return ZipCodeLookup(loaded_zip_codes)


zip_codes = load_zip_codes()
