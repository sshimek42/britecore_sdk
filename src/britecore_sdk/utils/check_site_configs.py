"""
Utility to check configured sites in .secrets.toml for required API keys.

Usage:
    python -m britecore_sdk.utils.check_site_configs

Outputs a table of sites showing status, auth mode, URL, and any missing keys.
"""

from britecore_sdk.utils import _config_common as _common
from britecore_sdk.utils._config_common import (
    CONFIG_PATH,
    SETTINGS_PATH,
    get_auth_mode,
    load_secrets,
    validate_site,
    warn_if_secrets_in_settings,
)

# Backward-compatibility exports used by tests and external monkeypatching.
os = _common.os
toml = _common.toml
check_site = validate_site


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
