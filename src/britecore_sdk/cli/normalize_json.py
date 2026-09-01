"""Normalize BriteCore payload JSON for script workflows.

This CLI converts raw JSON payload files into normalized BriteCore-ready shapes
using the lightweight ``britecore_sdk.data_layer`` helpers.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from britecore_sdk.data_layer import (
    normalize_contact_payload,
    normalize_policy_payload,
    normalize_quote_payload,
)

Payload = dict[str, Any]

SCHEMA_MAP: dict[str, dict[str, list[str]]] = {
    "contact": {
        "required": ["name", "address"],
        "optional": [
            "policy_number",
            "phone_numbers",
            "emails",
            "contact_id",
            "contact_type",
        ],
    },
    "policy": {
        "required": ["policy_number", "effective_date", "policy_type_id"],
        "optional": [
            "contacts",
            "inception_date",
            "term_type",
            "renewal_term_type",
            "is_renewal",
            "as_agent",
            "manual_policy_number",
            "previous_inspection_date",
            "next_inspection_date",
        ],
    },
    "quote": {
        "required": [
            "number",
            "policy_type_id",
            "agency_id",
            "named_insureds",
            "risks",
        ],
        "optional": [
            "underwriting_questions",
            "description",
            "number_origin",
            "transaction_type",
            "term_type",
            "inception_date",
            "effective_date",
            "next_inspection_date",
            "previous_inspection_date",
        ],
    },
}


def _normalize_one(kind: str, payload: Payload) -> Payload:
    """Normalize one JSON object for the requested payload kind."""
    if kind == "contact":
        return normalize_contact_payload(
            name=payload["name"],
            address=payload["address"],
            policy_number=payload.get("policy_number"),
            phone_numbers=payload.get("phone_numbers"),
            emails=payload.get("emails"),
            contact_id=payload.get("contact_id"),
            contact_type=payload.get("contact_type", "individual"),
        )

    if kind == "policy":
        return normalize_policy_payload(
            policy_number=payload["policy_number"],
            contacts=payload.get("contacts"),
            effective_date=payload["effective_date"],
            policy_type_id=payload["policy_type_id"],
            inception_date=payload.get("inception_date"),
            term_type=payload.get("term_type", "1 Year"),
            renewal_term_type=payload.get("renewal_term_type", "1 Year"),
            is_renewal=payload.get("is_renewal", True),
            as_agent=payload.get("as_agent", False),
            manual_policy_number=payload.get("manual_policy_number", True),
            previous_inspection_date=payload.get("previous_inspection_date"),
            next_inspection_date=payload.get("next_inspection_date"),
        )

    return normalize_quote_payload(
        number=payload["number"],
        policy_type_id=payload["policy_type_id"],
        agency_id=payload["agency_id"],
        named_insureds=payload["named_insureds"],
        risks=payload["risks"],
        underwriting_questions=payload.get("underwriting_questions"),
        description=payload.get("description", ""),
        number_origin=payload.get("number_origin", "manual"),
        transaction_type=payload.get("transaction_type", "renewal"),
        term_type=payload.get("term_type", "1 Year"),
        inception_date=payload.get("inception_date"),
        effective_date=payload.get("effective_date"),
        next_inspection_date=payload.get("next_inspection_date"),
        previous_inspection_date=payload.get("previous_inspection_date"),
    )


def _normalize_payload(kind: str, raw_payload: Any) -> Any:
    """Normalize a JSON object or list of objects."""
    if isinstance(raw_payload, list):
        return [_normalize_one(kind, item) for item in raw_payload]
    if isinstance(raw_payload, dict):
        return _normalize_one(kind, raw_payload)
    raise ValueError("Input JSON must be an object or a list of objects")


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint for normalizing JSON payload files."""
    parser = argparse.ArgumentParser(
        description="Normalize BriteCore payload JSON for contact/policy/quote shapes.",
    )
    parser.add_argument(
        "--kind",
        choices=("contact", "policy", "quote"),
        help="Payload type to normalize.",
    )
    parser.add_argument(
        "--input",
        help="Path to input JSON file (object or list of objects).",
    )
    parser.add_argument(
        "--output",
        help="Optional path to write normalized JSON. Prints to stdout when omitted.",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print output JSON with indentation.",
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Print required/optional keys for payload kinds and exit.",
    )

    args = parser.parse_args(argv)

    if args.schema:
        if args.kind:
            result: Any = {args.kind: SCHEMA_MAP[args.kind]}
        else:
            result = SCHEMA_MAP
    else:
        if not args.kind:
            parser.error("--kind is required unless --schema is used")
        if not args.input:
            parser.error("--input is required unless --schema is used")

        try:
            input_path = Path(args.input)
            raw_payload = json.loads(input_path.read_text(encoding="utf-8"))
            result = _normalize_payload(args.kind, raw_payload)
        except FileNotFoundError:
            print(f"Input file not found: {args.input}", file=sys.stderr)
            return 1
        except json.JSONDecodeError as exc:
            print(f"Invalid JSON in {args.input}: {exc}", file=sys.stderr)
            return 1
        except (KeyError, TypeError, ValueError) as exc:
            print(f"Normalization error: {exc}", file=sys.stderr)
            return 1

    if args.pretty:
        output_json = json.dumps(result, indent=2, sort_keys=True)
    else:
        output_json = json.dumps(result, separators=(",", ":"), sort_keys=True)

    if args.output:
        Path(args.output).write_text(output_json + "\n", encoding="utf-8")
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
