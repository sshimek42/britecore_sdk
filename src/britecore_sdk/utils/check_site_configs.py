"""
Utility to check configured sites in .secrets.toml for required API keys.

Usage:
    python -m britecore_sdk.utils.check_site_configs

Outputs a table of sites showing status, auth mode, URL, and any missing keys.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from britecore_sdk.utils import _config_common as _common
from britecore_sdk.utils._config_common import (
    FORBIDDEN_KEYS,
    CONFIG_PATH,
    SETTINGS_PATH,
    get_auth_mode,
    load_secrets,
    validate_site,
    warn_if_secrets_in_settings,
)
from britecore_sdk.settings import setting_files_full

# Backward-compatibility exports used by tests and external monkeypatching.
os = _common.os
toml = _common.toml
check_site = validate_site


def _display_path(path: str | Path) -> str:
    """Render file paths with home/cwd aliases for friendlier, less-sensitive output."""
    resolved = Path(path).resolve()
    text = str(resolved)
    home = str(Path.home().resolve())
    cwd = str(Path.cwd().resolve())
    if text.startswith(home):
        return text.replace(home, "~", 1)
    if text.startswith(cwd):
        return text.replace(cwd, ".", 1)
    return text


def _print_config_source_diagnostics() -> None:
    """Print config precedence and the discovered settings file load order."""
    print("Configuration source precedence (lowest -> highest):")
    print("  1) SDK package defaults")
    print("  2) User-level config (~/.britecore)")
    print("  3) Project-local config (./britecore.toml, ./.britecore_secrets.toml)")
    print("  4) BRITECORE_SDK_SETTINGS_FILE override")
    print("  5) BRITECORE_SDK_* environment variables")
    print()
    print("Resolved settings files (load order):")
    if setting_files_full:
        for idx, path in enumerate(setting_files_full, start=1):
            print(f"  {idx}. {_display_path(path)}")
    else:
        print("  (none)")
    print()


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the site-config checker."""
    parser = argparse.ArgumentParser(
        description="Validate configured BriteCore site sections and print status."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON instead of table output.",
    )
    if argv is None:
        # Ignore unrelated args (e.g., pytest flags) while still honoring known
        # CLI options like ``--json`` from real module invocation.
        args, _unknown = parser.parse_known_args(sys.argv[1:])
        return args
    return parser.parse_args(argv)


def _find_sensitive_keys_in_settings(path: str) -> list[dict[str, str]]:
    """Return sensitive keys found in settings.toml as structured entries."""
    if not os.path.exists(path):
        return []

    found: list[dict[str, str]] = []
    settings = toml.load(path)
    for section, config in settings.items():
        if isinstance(config, dict):
            for key in FORBIDDEN_KEYS:
                if key in config and config[key]:
                    found.append({"section": str(section), "key": key})
        elif section in FORBIDDEN_KEYS and config:
            found.append({"section": "[top-level]", "key": str(section)})
    return found


def build_site_config_report() -> dict[str, Any]:
    """Build a structured config validation report used by table and JSON modes."""
    secrets = load_secrets(CONFIG_PATH)
    site_sections = {k: v for k, v in secrets.items() if isinstance(v, dict)}

    sites: list[dict[str, Any]] = []
    for site, config in site_sections.items():
        ok, missing = check_site(site, config)
        sites.append(
            {
                "site": site,
                "ok": ok,
                "status": "OK" if ok else "INCORRECT",
                "auth_mode": get_auth_mode(config),
                "url": config.get("base_url", ""),
                "missing_keys": missing,
            }
        )

    return {
        "config_precedence": [
            "sdk_package_defaults",
            "user_level_config",
            "project_local_config",
            "envvar_settings_file",
            "envvar_britecore_sdk_prefix",
        ],
        "resolved_settings_files": [
            _display_path(path) for path in setting_files_full
        ],
        "active_paths": {
            "secrets_file": _display_path(CONFIG_PATH),
            "settings_file": _display_path(SETTINGS_PATH),
        },
        "warnings": {
            "sensitive_keys_in_settings": _find_sensitive_keys_in_settings(
                SETTINGS_PATH
            )
        },
        "sites": sites,
    }


def main(argv: list[str] | None = None) -> None:
    """Check all configured site sections and print a status table or JSON report."""
    args = _parse_args(argv)
    report = build_site_config_report()

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return

    _print_config_source_diagnostics()
    warn_if_secrets_in_settings(SETTINGS_PATH)
    print(
        f"Checking API config for {len(report['sites'])} site(s) in {CONFIG_PATH}...\n"
    )
    print(f"{'Site':<20} {'Status':<11} {'Auth':<9} {'URL':<45} Missing Keys")
    print("-" * 100)
    for site in report["sites"]:
        missing_str = ", ".join(site["missing_keys"]) if site["missing_keys"] else ""
        print(
            f"{site['site']:<20} {site['status']:<11} {site['auth_mode']:<9} "
            f"{site['url']:<45} {missing_str}"
        )


if __name__ == "__main__":
    main()
