"""
Utility to check configured sites in .secrets.toml for required API keys.

Usage:
    python -m britecore_libraries.utils.check_site_configs

Outputs a table of sites and whether they are correctly configured for API access.
"""

import os
import sys

import toml

REQUIRED_KEYS = ["base_url"]
OAUTH_KEYS = ["client_id", "client_secret"]
API_KEY = "api_key"
FORBIDDEN_KEYS = ["api_key", "client_id", "client_secret"]

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    ".secrets.toml",
)
SETTINGS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "settings.toml",
)


def load_secrets(path: str) -> dict:
    """Load site secrets from TOML, exiting with code 1 when missing."""
    if not os.path.exists(path):
        print(f"Config file not found: {path}")
        sys.exit(1)
    return toml.load(path)


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
    print(f"{'Site':<20} {'Status':<10} Missing Keys")
    print("-" * 60)
    for site, config in site_sections.items():
        ok, missing = check_site(site, config)
        status = "OK" if ok else "INCORRECT"
        print(f"{site:<20} {status:<10} {', '.join(missing) if missing else ''}")


if __name__ == "__main__":
    main()
