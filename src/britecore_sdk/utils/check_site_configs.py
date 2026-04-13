"""
Utility to check configured sites in .secrets.toml for required API keys.

Usage:
    python -m britecore_sdk.utils.check_site_configs

Outputs a table of sites showing status, auth mode, URL, and any missing keys.
"""

import os
import sys
from pathlib import Path

import toml

REQUIRED_KEYS = ["base_url"]
OAUTH_KEYS = ["client_id", "client_secret"]
API_KEY = "api_key"
FORBIDDEN_KEYS = ["api_key", "client_id", "client_secret"]

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH: str = str(BASE_DIR / "settings" / ".secrets.toml")
SETTINGS_PATH: str = str(BASE_DIR / "settings" / "settings.toml")


def load_secrets(path: str) -> dict:
    """Load site secrets from TOML, exiting with code 1 when missing."""
    if not os.path.exists(path):
        print(f"Config file not found: {path}")
        sys.exit(1)
    return toml.load(path)


def get_auth_mode(config: dict) -> str:
    """Return the auth mode that would be selected for this site config.

    Returns:
        ``"OAuth"``   – both ``client_id`` and ``client_secret`` are present.
        ``"API Key"`` – ``api_key`` is present (and OAuth keys are absent/incomplete).
        ``"-"``       – neither auth option is fully configured.
    """
    has_oauth = all(config.get(k) for k in OAUTH_KEYS)
    has_api_key = bool(config.get(API_KEY))
    if has_oauth:
        return "OAuth"
    if has_api_key:
        return "API Key"
    return "-"


def check_site(_site: str, config: dict) -> tuple[bool, list[str]]:
    """Validate one site section and return status with missing required keys."""
    missing = []
    for key in REQUIRED_KEYS:
        if not config.get(key):
            missing.append(key)
    has_oauth = all(config.get(k) for k in OAUTH_KEYS)
    has_api_key = bool(config.get(API_KEY))
    if not (has_oauth or has_api_key):
        # List missing auth keys
        if not has_oauth:
            for k in OAUTH_KEYS:
                if not config.get(k):
                    missing.append(k)
        if not has_api_key:
            missing.append(API_KEY)
    return (len(missing) == 0), missing


def warn_if_secrets_in_settings(path: str) -> None:
    """Warn when sensitive keys are found in settings.toml instead of secrets."""
    if not os.path.exists(path):
        return
    settings = toml.load(path)
    found = []
    for section, config in settings.items():
        if isinstance(config, dict):
            for key in FORBIDDEN_KEYS:
                if key in config and config[key]:
                    found.append((section, key))
        else:
            # Top-level keys
            if section in FORBIDDEN_KEYS and config:
                found.append(("[top-level]", section))
    if found:
        print(
            "\nWARNING: Sensitive keys found in settings.toml (should be in .secrets.toml only):"
        )
        for section, key in found:
            print(f"  Section: {section}, Key: {key}")
        print("Move these to .secrets.toml and remove from settings.toml!")


def main() -> None:
    """Check all configured site sections and print a status table."""
    warn_if_secrets_in_settings(SETTINGS_PATH)
    secrets = load_secrets(CONFIG_PATH)
    # Only process keys whose value is a dict (site sections)
    site_sections = {k: v for k, v in secrets.items() if isinstance(v, dict)}
    print(f"Checking API config for {len(site_sections)} site(s) in {CONFIG_PATH}...\n")
    print(f"{'Site':<20} {'Status':<11} {'Auth':<9} {'URL':<45} Missing Keys")
    print("-" * 100)
    for site, config in site_sections.items():
        ok, missing = check_site(site, config)
        status = "OK" if ok else "INCORRECT"
        auth = get_auth_mode(config)
        url = config.get("base_url", "")
        missing_str = ", ".join(missing) if missing else ""
        print(f"{site:<20} {status:<11} {auth:<9} {url:<45} {missing_str}")


if __name__ == "__main__":
    main()
