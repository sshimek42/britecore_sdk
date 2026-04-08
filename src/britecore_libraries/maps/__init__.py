"""Map exports and regex loader for the SDK."""

import os
import re
from typing import Any

from britecore_libraries.maps.britecore_agency_map import agency
from britecore_libraries.maps.britecore_field_map import (
    field_map_to_britecore,
    field_map_to_named_insured,
    field_map_to_risk_location,
)
from britecore_libraries.maps.britecore_policy_map import (
    britecore_policy_type_map,
    policy_map,
)


def load_regexes() -> (
    tuple[dict[str | Any, re.Pattern[str] | Any], dict[str, dict[str, int]]]
):
    """Return compiled regexes and naming groups for the configured system."""
    mutual_system = os.environ.get("system", "")
    if not mutual_system:
        raise ValueError(
            "The 'system' environment variable is not set. "
            "Set it to the mutual system identifier before calling load_regexes()."
        )

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

    common.update(system_overrides.get(mutual_system, {}))

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


__all__ = [
    "load_regexes",
    "agency",
    "policy_map",
    "britecore_policy_type_map",
    "field_map_to_britecore",
    "field_map_to_named_insured",
    "field_map_to_risk_location",
]
