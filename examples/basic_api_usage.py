"""Basic usage sample for britecore_sdk.

This script is safe by default:
- It demonstrates local model/validator usage without network calls.
- Optional dry-run API flow example is available via --dry-run-policy-number.
- Optional live API read call is available via --live-policy-number.
"""

from __future__ import annotations

import argparse
from pprint import pprint

import britecore_sdk
from britecore_sdk.models.contact import BritecoreContact
from britecore_sdk.validators.email_validator import EmailValidator
from britecore_sdk.validators.name_validator import NameValidator


def run_local_demo() -> None:
    """Run local-only examples that do not require API credentials."""
    print(f"britecore_sdk version: {britecore_sdk.__version__}")

    normalized_name = NameValidator.normalize_business_name("acme llc")
    normalized_email = EmailValidator.validate_email("USER@EXAMPLE.COM")

    contact = BritecoreContact(
        name="john smith",
        address={
            "address_line1": "123 Main St",
            "address_city": "Madison",
            "address_state": "WI",
            "address_zip": "53703",
            "type": "home",
        },
        email=[{"email": "USER@EXAMPLE.COM", "type": "home"}],
        phone_number=[{"phone_number": "5551234567", "type": "mobile"}],
    )
    contact_payload = contact.process_contact()

    print("\nLocal normalization demo:")
    print(f"- NameValidator: {normalized_name}")
    print(f"- EmailValidator: {normalized_email}")
    print("- BritecoreContact payload:")
    pprint(contact_payload)


def run_live_policy_lookup(policy_number: str) -> None:
    """Run an optional read-only API example.

    This requires valid local configuration and credentials.
    """
    from britecore_sdk.api.api_calls import init_api_client
    from britecore_sdk.api.api_calls.v2 import policies

    print(f"\nRunning live retrieve_policy call for policy_number={policy_number!r}...")
    # Uses target_site from environment; pass a site string here if you prefer explicit site selection.
    init_api_client()
    result = policies.retrieve_policy(policy_number=policy_number)
    print("Live API call succeeded. Result preview:")
    if isinstance(result, dict):
        preview = {
            key: result.get(key)
            for key in ("id", "policy_number", "status")
            if key in result
        }
        pprint(preview if preview else result)
    else:
        pprint(result)


def run_dry_run_policy_lookup(policy_number: str) -> None:
    """Run an optional dry-run API example without sending a live request.

    This still requires local site configuration, but for OAuth sites it skips
    token acquisition unless you explicitly pass request headers.
    """
    from britecore_sdk.api.api_calls import init_api_client
    from britecore_sdk.api.api_calls.v2 import policies

    print(
        f"\nRunning dry-run retrieve_policy call for policy_number={policy_number!r}..."
    )
    init_api_client(default_dry_run=True)
    result = policies.retrieve_policy(policy_number=policy_number)
    print("Dry-run preview:")
    pprint(result)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI arguments for local demo and optional live lookup."""
    parser = argparse.ArgumentParser(
        description=("Run local and optional live usage samples for britecore_sdk."),
    )
    parser.add_argument(
        "--dry-run-policy-number",
        help=(
            "Optional policy number to preview a retrieve_policy request in dry-run "
            "mode without sending a live API call."
        ),
    )
    parser.add_argument(
        "--live-policy-number",
        help=(
            "Optional policy number to trigger a live, read-only "
            "retrieve_policy API call."
        ),
    )
    return parser


def main() -> int:
    """Run the sample workflow and return a process exit code."""
    parser = build_parser()
    args = parser.parse_args()

    run_local_demo()

    if args.dry_run_policy_number:
        try:
            run_dry_run_policy_lookup(args.dry_run_policy_number)
        except Exception as exc:  # pragma: no cover - usage helper
            print("\nDry-run API sample failed.")
            print(
                "Ensure target_site and local site configuration are available before using --dry-run-policy-number."
            )
            print(f"Error: {exc}")
            return 1

    if args.live_policy_number:
        try:
            run_live_policy_lookup(args.live_policy_number)
        except Exception as exc:  # pragma: no cover - usage helper
            print("\nLive API sample failed.")
            print(
                "Ensure target_site and credentials are configured before using --live-policy-number."
            )
            print(f"Error: {exc}")
            return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
