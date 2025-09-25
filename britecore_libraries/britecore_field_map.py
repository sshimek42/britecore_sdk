"""Mappings between carrier export field names and BriteCore internal field names.

This module provides:
- field_map_to_britecore: Per-carrier, per-section mappings from carrier column
  headers to BriteCore attribute names. Each section dict may include a special
  key "address_fields" listing the carrier fields that compose an address.
- field_map_to_named_insured: Reverse lookup for named insured fields
  (carrier <- BriteCore).
- field_map_to_risk_location: Reverse lookup for risk location fields
  (carrier <- BriteCore).
"""

from typing import Dict, List, Union

# Type aliases for clarity
FieldName = str
BritecoreFieldName = str
Section = Dict[FieldName, Union[BritecoreFieldName, List[FieldName]]]
CarrierSections = Dict[str, Section]
CarrierFieldMap = Dict[str, CarrierSections]

field_map_to_britecore: CarrierFieldMap = {
    "MIPS": {
        "policy_list": {
            "NAME": "name",
            "ADDR 1": "address_line1",
            "ADDR 2": "address_line2",
            "CITY": "address_city",
            "ST": "address_state",
            "ZIP": "address_zip",
            "PHONE 1": "phone_number_h",
            "PHONE 2": "phone_number_m",
            "E-MAIL ADDR": "email",
            "POLICY #": "policy_number",
            "NEW POL DATE": "inception_date",
            "FROM DATE": "effective_date",
            "INSPECTION DATE LAST": "previous_inspection_date",
            "INSPECTION DATE NEXT": "next_inspection_date",
            "address_fields": [
                "ADDR 1",
                "ADDR 2",
                "CITY",
                "ST",
                "ZIP",
                "PHONE 1",
                "PHONE 2",
                "E-MAIL ADDR",
                "POLICY #",
            ],
        },
        "location_list": {
            "Policy Number": "policy_number",
            "Legal Address": "address_line1",
            "Legal City": "address_city",
            "Legal State": "address_state",
            "Legal Zip": "address_zip",
            "County": "address_county",
            "address_fields": [
                "Legal Address",
                "Legal City",
                "Legal State",
                "Legal Zip",
                "Policy Number",
                "County",
            ],
        },
    },
    "Spectrum": {
        "policy_list": {
            "Named Insured": "name",
            "Address Line 1": "address_line1",
            "Address Line 2": "address_line2",
            "City": "address_city",
            "State": "address_state",
            "Postal Code": "address_zip",
            "Home Phone": "phone_number_h",
            "Mobile Phone": "phone_number_m",
            "Email Address": "email",
            "Policy #": "policy_number",
            "Policy Eff Date": "effective_date",
            "address_fields": [
                "Address Line 1",
                "Address Line 2",
                "City",
                "State",
                "Postal Code",
                "Home Phone",
                "Mobile Phone",
                "Email Address",
                "Policy #",
            ],
        },
        "location_list": {
            "Policy #": "policy_number",
            "Physical Address": "address_line1",
            "City": "address_city",
            "State": "address_state",
            "Zip": "address_zip",
            "address_fields": ["Physical Address", "City", "State", "Zip", "Policy #"],
        },
    },
}

# Reverse mapping: BriteCore named insured fields back to carrier headers.
field_map_to_named_insured: Dict[str, Dict[str, str]] = {
    "MIPS": {
        v: k
        for k, v in field_map_to_britecore["MIPS"]["policy_list"].items()
        if k != "address_fields"
    },
    "Spectrum": {
        v: k
        for k, v in field_map_to_britecore["Spectrum"]["policy_list"].items()
        if k != "address_fields"
    },
}

# Reverse mapping: BriteCore risk location fields back to carrier headers.
field_map_to_risk_location: Dict[str, Dict[str, str]] = {
    "MIPS": {
        v: k
        for k, v in field_map_to_britecore["MIPS"]["location_list"].items()
        if k != "address_fields"
    },
    "Spectrum": {
        v: k
        for k, v in field_map_to_britecore["Spectrum"]["location_list"].items()
        if k != "address_fields"
    },
}
