"""Map loading with runtime fallback for local/private map files.

Built-in defaults are used when private ``*_map.py`` files are absent.
Drop a private ``*_map.py`` file alongside this ``__init__.py`` to
override any of the built-in maps without touching library source.

Fallback resolution order (for each symbol):
  1. Import from the matching local ``*_map.py`` on ``sys.path``
  2. Built-in default (empty dict / inline reference implementation)
"""

import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Built-in regex / naming-group implementation
# (mirrors the reference britecore_policy_name_map.py; used when that file
#  is absent from the local environment)
# ---------------------------------------------------------------------------


def _builtin_load_regexes() -> (
    tuple[dict[str | Any, re.Pattern[str] | Any], dict[str, dict[str, int]]]
):
    """Built-in fallback implementation of load_regexes.

    Returns the same tuple as the private ``britecore_policy_name_map``
    module: ``(compiled_regexes, name_groups)``.
    """
    mutual_system = os.environ.get("system", "")
    if not mutual_system or mutual_system not in ("mips", "spectrum_v1", "spectrum_v2"):
        mutual_system = "mips"

    common: dict[str | Any, re.Pattern[str] | Any] = {
        "search_name_mult": re.compile(
            r"^(\w*\W\w?\W|\w*\W)(\w*\s?\w)?\s(&)\s(\w*\W\w?\W|\w*\W?\w*)?(r\W*\w*)?"
        ),
        "search_name_single": re.compile(r"^(\w*\W\w|\w*\W*)(\W\w*|\w*\W\w*)(\W\w*)?"),
        "search_email": re.compile(r"[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,64}"),
        "reg_name_c": re.compile(r"[^0-9a-zA-Z\s#+&',/-]+"),
        "reg_and_or": re.compile(r"\W(&/or|and/or|and|or)\W", re.IGNORECASE),
        "reg_address": re.compile(r"[^0-9a-zA-Z\s#,/-]+"),
        "reg_address2": re.compile(r"c/o|dba|inc|att|co\W|trust", re.IGNORECASE),
        "reg_city_state": re.compile(r"[^0-9a-zA-Z\s]+"),
        "reg_zip": re.compile(r"[^0-9a-zA-Z]+"),
        "reg_phone": re.compile(r"-|\(|\)|\s"),
        "reg_email": re.compile(
            r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7})\b"
        ),
        "reg_name": re.compile(r"[^0-9a-zA-Z\s#+&'/-]+"),
        "reg_small_name": re.compile(r"\s(Du|Des)\s"),
        "reg_business_name": re.compile(r"\s(llc|llp|dba|inc)(?:\s|$)", re.IGNORECASE),
        "reg_double_apostrophe": re.compile(r"'\w"),
        "street_name_replacement": {
            re.compile(r"Hwy\b"): "Highway",
            re.compile(r"Cty\b"): "County",
            re.compile(r"Rd\b"): " Road",
            re.compile(r"Ave\b"): "Avenue",
            re.compile(r"St\b"): "Street",
            re.compile(r"Ln\b"): "Lane",
            re.compile(r"Ct\b"): "Court",
            re.compile(r"Dr\b"): "Drive",
            re.compile(r"Po\b"): "PO",
            re.compile(r"P\sO\b"): "PO",
            re.compile(r"Cir\b"): "Circle",
            re.compile(r"Pt\b"): "Point",
            re.compile(r"Tk\b"): "Trunk",
            re.compile(r"Tr\b"): "Trail",
            re.compile(r"Trl\b"): "Trail",
            re.compile(r"Ter\b"): "Terrace",
            re.compile(r"\sN\s"): " North ",
            re.compile(r"\sS\s"): " South ",
            re.compile(r"\sE\s"): " East ",
            re.compile(r"\sW\s"): " West ",
            re.compile(r"Us\b"): "US",
        },
        "reg_no_split": re.compile(r"(\sof\s|c\\o|-|trust|')", re.IGNORECASE),
    }

    system_overrides: dict[str, dict[str, re.Pattern[str] | None]] = {
        "mips": {},
        "spectrum_v1": {
            "search_name_single": re.compile(r"(\w*\W\w?\W|\w*\W)(\w*\s?\w{0})?(\w*)?"),
            "search_name_mult": re.compile(
                r"(\w*\W\w|\w*\W*)(\W\w*|\w*\W\w*)?\s(&)\s"
                r"(\w*\W\w?\W|\w*\W?\w{0})?(\W*\w*)?(\W*\w*)?"
            ),
        },
        "spectrum_v2": {
            "search_name_single": re.compile(r"(\w*\W\w?\W|\w*\W)(\w*\s?\w{0})?(\w*)?"),
            "search_name_mult": re.compile(
                r"(\w*\W\w|\w*\W*)(\W\w*|\w*\W\w*)?\s(&)\s"
                r"(\w*\W\w?\W|\w*\W?\w{0})?(\W*\w*)?(\W*\w*)?"
            ),
        },
    }

    common.update(system_overrides[mutual_system])

    system_naming_groups: dict[str, dict[str, dict[str, int]]] = {
        "mips": {
            "multi": {
                "last_name_1": 1,
                "last_name_2": 3,
                "first_name_1": 2,
                "first_name_2": 4,
                "suffix": 5,
            }
        },
        "spectrum_v1": {
            "multi": {
                "last_name_1": 5,
                "last_name_2": 2,
                "first_name_1": 1,
                "first_name_2": 4,
                "suffix": 6,
            }
        },
        "spectrum_v2": {
            "multi": {
                "last_name_1": 5,
                "last_name_2": 2,
                "first_name_1": 1,
                "first_name_2": 4,
                "suffix": 6,
            }
        },
    }

    return common, system_naming_groups[mutual_system]


# ---------------------------------------------------------------------------
# load_regexes — try local private file first, then built-in fallback
# ---------------------------------------------------------------------------
try:
    from britecore_libraries.maps.britecore_policy_name_map import load_regexes

    logger.debug("maps: loaded load_regexes from local britecore_policy_name_map.py")
except ImportError:
    load_regexes = _builtin_load_regexes  # type: ignore[assignment]
    logger.debug(
        "maps: britecore_policy_name_map.py absent – using built-in load_regexes"
    )

# ---------------------------------------------------------------------------
# Agency map
# ---------------------------------------------------------------------------
try:
    from britecore_libraries.maps.britecore_agency_map import agency

    logger.debug("maps: loaded agency from local britecore_agency_map.py")
except ImportError:
    agency: dict[str, str] = {}
    logger.debug("maps: britecore_agency_map.py absent – agency map is empty")

# ---------------------------------------------------------------------------
# Policy maps
# ---------------------------------------------------------------------------
try:
    from britecore_libraries.maps.britecore_policy_map import (
        britecore_policy_type_map,
        policy_map,
    )

    logger.debug("maps: loaded policy maps from local britecore_policy_map.py")
except ImportError:
    policy_map: dict[str, str] = {}
    britecore_policy_type_map: dict[str, dict[str, str]] = {}
    logger.debug("maps: britecore_policy_map.py absent – policy maps are empty")

# ---------------------------------------------------------------------------
# Field maps
# ---------------------------------------------------------------------------
try:
    from britecore_libraries.maps.britecore_field_map import (
        field_map_to_britecore,
        field_map_to_named_insured,
        field_map_to_risk_location,
    )

    logger.debug("maps: loaded field maps from local britecore_field_map.py")
except ImportError:
    field_map_to_britecore: dict[str, Any] = {}
    field_map_to_named_insured: dict[str, Any] = {}
    field_map_to_risk_location: dict[str, Any] = {}
    logger.debug("maps: britecore_field_map.py absent – field maps are empty")

# ---------------------------------------------------------------------------
# Public surface
# ---------------------------------------------------------------------------
__all__ = [
    # regex / naming groups
    "load_regexes",
    # agency
    "agency",
    # policy
    "policy_map",
    "britecore_policy_type_map",
    # field
    "field_map_to_britecore",
    "field_map_to_named_insured",
    "field_map_to_risk_location",
]
