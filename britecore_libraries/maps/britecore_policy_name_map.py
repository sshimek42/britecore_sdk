import os
import re

mutual_system = os.environ.get("system")

common_compiled_regexes = {
    "search_name_mult": re.compile(
        r"^(\w*\W\w?\W|\w*\W)(\w*\s?\w)?\s(&)\s(\w*\W\w?\W|\w*\W?\w*)?("
        r"\W*\w*)?"
    ),
    "search_name_single": re.compile(r"^(\w*\W\w|\w*\W*)(\W\w*|\w*\W\w*)(\W\w*)?"),
    "search_email": re.compile(
        r"[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{"
        r"2,64}"
    ),
    "reg_name_c": re.compile(r"[^0-9a-zA-Z\s#+&',/-]+"),
    "reg_and_or": re.compile(r"\W(&/or|and/or|and|or)\W", re.IGNORECASE),
    "reg_address": re.compile(r"[^0-9a-zA-Z\s#,/-]+"),
    "reg_address2": re.compile(r"c/o|dba|inc|att|co\W|trust", re.IGNORECASE),
    "reg_city_state": re.compile(r"[^0-9a-zA-Z\s]+"),
    "reg_zip": re.compile(r"[^0-9a-zA-Z]+"),
    "reg_phone": re.compile(r"-|\(|\)|\s"),
    "reg_email": re.compile(r"\b([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7})\b"),
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

system_compiled_regexes = {
    "MIPS": {},
    "Spectrum": {
        "search_name_single": re.compile(r"(\w*\W\w?\W|\w*\W)(\w*\s?\w{0})?(\w*)?"),
        "search_name_mult": re.compile(
            r"(\w*\W\w|\w*\W*)(\W\w*|\w*\W\w*)?\s(&)\s(\w*\W\w?\W|\w*\W?\w{0})?(\W*\w*)?(\W*\w*)?"
        ),
    },
}

common_compiled_regexes.update(system_compiled_regexes.get(mutual_system))

compiled_regexes = common_compiled_regexes

system_naming_groups = {
    "MIPS": {
        "multi": {
            "last_name_1": 1,
            "last_name_2": 3,
            "first_name_1": 2,
            "first_name_2": 4,
            "suffix": 5,
        }
    },
    "Spectrum": {
        "multi": {
            "last_name_1": 5,
            "last_name_2": 2,
            "first_name_1": 1,
            "first_name_2": 4,
            "suffix": 6,
        }
    },
}

name_groups = system_naming_groups.get(mutual_system)
