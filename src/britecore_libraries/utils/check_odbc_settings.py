"""
Script to check for ODBC settings in .secrets.toml for each site.
Warns if ODBC settings are present but incomplete.
"""

import os

import toml

CONFIG_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    ".secrets.toml",
)

ODBC_KEYS = ["db_conn_string", "db_conn_options"]


def check_odbc_settings():
    if not os.path.exists(CONFIG_PATH):
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


def main():
    print("Checking ODBC settings in .secrets.toml...")
    check_odbc_settings()


if __name__ == "__main__":
    main()
