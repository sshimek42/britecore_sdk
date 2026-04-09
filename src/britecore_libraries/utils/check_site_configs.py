"""
Utility to check configured sites in .secrets.toml for required API keys.

Usage:
    python -m britecore_libraries.utils.check_site_configs

Outputs a table of sites and whether they are correctly configured for API access.
"""
import os
import sys
import toml
from typing import Dict, List

REQUIRED_KEYS = ["base_url"]
OAUTH_KEYS = ["client_id", "client_secret"]
API_KEY = "api_key"

CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "..", "config", ".secrets.toml")


def load_secrets(path: str) -> Dict:
    if not os.path.exists(path):
        print(f"Config file not found: {path}")
        sys.exit(1)
    return toml.load(path)


def check_site(site: str, config: Dict) -> (bool, List[str]):
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


def main():
    secrets = load_secrets(CONFIG_PATH)
    sites = secrets.keys()
    print(f"Checking API config for {len(sites)} site(s) in {CONFIG_PATH}...\n")
    print(f"{'Site':<20} {'Status':<10} Missing Keys")
    print("-" * 60)
    for site in sites:
        config = secrets[site]
        ok, missing = check_site(site, config)
        status = "OK" if ok else "INCORRECT"
        print(f"{site:<20} {status:<10} {', '.join(missing) if missing else ''}")

if __name__ == "__main__":
    main()

