"""Check for per-site ODBC settings in `.secrets.toml`."""

from pathlib import Path

import toml

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / ".secrets.toml"

ODBC_KEYS = ["db_conn_string", "db_conn_options"]


def check_odbc_settings() -> bool:
    """Validate that per-site ODBC settings are either complete or absent."""
    if not CONFIG_PATH.exists():
        print(f"Config file not found: {CONFIG_PATH}")
        return False
    secrets = toml.load(CONFIG_PATH)
    site_sections = {k: v for k, v in secrets.items() if isinstance(v, dict)}
    found_any = False
    for site, config in site_sections.items():
        present = [k for k in ODBC_KEYS if k in config and config[k]]
        missing = [k for k in ODBC_KEYS if k not in config or not config[k]]
        if present:
            found_any = True
            if missing:
                print(
                    f"WARNING: Site '{site}' has incomplete ODBC settings. Missing: {', '.join(missing)}"
                )
            else:
                print(f"Site '{site}' has complete ODBC settings.")
    if not found_any:
        print("No ODBC settings found in any site section.")
    return True


def main() -> None:
    """Run the ODBC settings check script."""
    print("Checking ODBC settings in .secrets.toml...")
    check_odbc_settings()


if __name__ == "__main__":
    main()
