"""Regex loader for the britecore_libraries SDK.

Architecture note
-----------------
This module provides two things:

1. ``get_common_regexes()`` – carrier-agnostic compiled regex patterns used by
   the built-in validators (address, email, name, phone).  No ``system``
   environment variable is required.

2. ``load_regexes(system, overrides, naming_groups)`` – returns the common
   patterns extended with caller-supplied, carrier-specific overrides and
   naming-group index maps.  The carrier-specific content belongs in the
   consuming project; this function just merges and returns the combined result.

Data maps (agency, field, policy type) were previously bundled here as
``britecore_agency_map.py``, ``britecore_field_map.py``, and
``britecore_policy_map.py``.  Those files have been removed — carrier-specific mapping data
is no longer included in this package. If you require such mappings, manage them in your own
deployment or integration layer.
"""

import os
import re
from logging import getLogger
from typing import Any

LOGGER = getLogger(__name__)


def get_common_regexes() -> dict[str, re.Pattern[str] | Any]:
    """Return carrier-agnostic compiled regex patterns.

    These patterns are used by the built-in validators (address, email, name,
    phone) and do not require any carrier-system context.  They cover generic
    data formats: names, addresses, phone numbers, email addresses, and common
    street abbreviation replacements.

    Returns:
        dict mapping pattern name to compiled ``re.Pattern`` (or a nested
        dict for ``street_name_replacement``).
    """
    return {
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


def load_regexes(
    system: str | None = None,
    overrides: dict[str, re.Pattern[str]] | None = None,
    naming_groups: dict[str, dict[str, int]] | None = None,
) -> tuple[dict[str | Any, re.Pattern[str] | Any], dict[str, dict[str, int]]]:
    """Return compiled regexes and naming groups for a carrier system.

    Starts from the carrier-agnostic common patterns (see
    ``get_common_regexes``) and merges in the caller-supplied overrides and
    naming groups.  Carrier-specific content belongs in the consuming project
    (e.g. ``britecore_import.mappings.RegexMappings``); this function is the
    merge point.

    Args:
        system: Carrier system identifier (e.g. ``"mips"``).  When *None*,
            the value of the ``system`` environment variable is used as a
            fallback for backward compatibility.
        overrides: Carrier-specific regex patterns that replace or extend the
            common patterns for the given system.  When *None* and *system* is
            provided, the function raises ``KeyError`` for unknown systems only
            if no overrides are supplied.
        naming_groups: Mapping of group-name → capture-group index used to
            extract name parts from the carrier-specific name-split regex.

    Returns:
        ``(compiled_regexes, naming_groups_dict)`` where ``compiled_regexes``
        is the merged common + override dict and ``naming_groups_dict`` is the
        supplied (or empty) naming-group map.

    Raises:
        ValueError: If neither *system* nor the ``system`` env var is set and
            no *overrides* are provided.
    """
    if system is None:
        system = os.environ.get("system", "")
    if not system and overrides is None:
        raise ValueError(
            "The 'system' environment variable is not set. "
            "Pass system= or set the 'system' env var before calling load_regexes()."
        )

    merged = get_common_regexes()
    if overrides:
        merged.update(overrides)

    resolved_naming_groups: dict[str, dict[str, int]] = (
        naming_groups if naming_groups is not None else {}
    )

    return merged, resolved_naming_groups


__all__ = [
    "get_common_regexes",
    "load_regexes",
]
