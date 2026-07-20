"""Interactive configuration wizard for BriteCore SDK.

Guides users through setting up credentials and configuration via CLI prompts.
"""

import sys
from pathlib import Path
from typing import Any

from britecore_sdk import logger


def _try_import_questionary():
    """Try to import questionary, with helpful error message if missing."""
    try:
        import questionary

        return questionary
    except ImportError:
        print(
            "Error: 'questionary' is required for the config wizard.\n"
            "Install it with:\n"
            "  pip install 'britecore_sdk[interactive]'\n"
        )
        sys.exit(1)


def _write_config_file(
    filepath: str, config: dict[str, Any], is_secrets: bool = False
) -> bool:
    """Write configuration to a TOML file.

    Args:
        filepath: Path to write config to.
        config: Configuration dictionary.
        is_secrets: Whether this is a secrets file (for comments).

    Returns:
        True if successful, False otherwise.
    """
    try:
        # Simple TOML generation (not using library to avoid extra deps)
        content = ""
        if is_secrets:
            content += "# WARNING: This file contains secrets. Do not commit to version control.\n"
            content += "# Add .britecore_secrets.toml to .gitignore\n\n"
        else:
            content += "# BriteCore SDK Configuration\n"
            content += "# Multiple environments can be configured by creating sections like [production], [sandbox]\n\n"

        # Write sections
        for key, value in config.items():
            if isinstance(value, str):
                # Escape quotes in string values
                escaped = value.replace('"', '\\"')
                content += f'{key} = "{escaped}"\n'
            elif isinstance(value, bool):
                content += f"{key} = {'true' if value else 'false'}\n"
            elif isinstance(value, int | float):
                content += f"{key} = {value}\n"

        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

        if is_secrets:
            # Set restrictive permissions on secrets file
            path.chmod(0o600)

        return True
    except Exception as e:
        logger.error(f"Failed to write config file {filepath}: {e}")
        return False


def main(argv: list[str] | None = None) -> int:
    """Run the interactive configuration wizard.

    Args:
        argv: Command-line arguments (not currently used).

    Returns:
        Exit code (0 for success, 1 for error/cancel).
    """
    questionary = _try_import_questionary()

    print("\n🔧 BriteCore SDK Configuration Wizard\n")
    print("This wizard will help you configure the BriteCore SDK.\n")

    # Ask for environment/target site
    target_site = questionary.text(
        "Target environment name (e.g., 'production', 'sandbox'):",
        default="production",
    ).ask()

    if target_site is None:
        print("Cancelled.")
        return 1

    # Ask for auth method
    auth_method = questionary.select(
        "Authentication method:",
        choices=["API Key", "OAuth (Client Credentials)"],
    ).ask()

    if auth_method is None:
        print("Cancelled.")
        return 1

    # Ask for base URL
    base_url = questionary.text(
        "Base URL (e.g., https://britecore.example.com):",
    ).ask()

    if not base_url:
        print("Base URL is required.")
        return 1

    # Collect credentials based on auth method
    if "API Key" in auth_method:
        api_key = questionary.password(
            "API Key:",
        ).ask()
        if not api_key:
            print("API Key is required.")
            return 1
        credentials = {
            "base_url": base_url,
            "api_key": api_key,
        }
        auth_display = "API Key"
    else:
        client_id = questionary.text(
            "Client ID:",
        ).ask()
        if not client_id:
            print("Client ID is required.")
            return 1

        client_secret = questionary.password(
            "Client Secret:",
        ).ask()
        if not client_secret:
            print("Client Secret is required.")
            return 1

        credentials = {
            "base_url": base_url,
            "client_id": client_id,
            "client_secret": client_secret,
        }
        auth_display = "OAuth"

    # Ask where to save
    save_location = questionary.select(
        "Save configuration to:",
        choices=[
            "~/.britecore/.secrets.toml (user-level, recommended)",
            "./britecore_secrets.toml (project-local)",
            "~/.britecore/settings.toml (user-level, shared settings)",
        ],
    ).ask()

    if save_location is None:
        print("Cancelled.")
        return 1

    # Determine file path
    if "user-level, recommended" in save_location:
        config_dir = Path.home() / ".britecore"
        config_file = config_dir / ".secrets.toml"
        is_secrets = True
    elif "project-local" in save_location:
        config_file = Path("./.britecore_secrets.toml")
        is_secrets = True
    else:
        config_dir = Path.home() / ".britecore"
        config_file = config_dir / "settings.toml"
        is_secrets = False

    # Write the configuration
    print(f"\n✓ Writing configuration to {config_file}...")

    # Format as TOML section under target site

    try:
        config_file.parent.mkdir(parents=True, exist_ok=True)

        # Read existing config if present
        existing_content = ""
        if config_file.exists():
            existing_content = config_file.read_text()

        # Append or update section (simple append for now)
        section_header = f"\n[{target_site}]\n"
        section_content = ""
        for key, value in credentials.items():
            if isinstance(value, str):
                escaped = value.replace('"', '\\"')
                section_content += f'{key} = "{escaped}"\n'

        new_content = existing_content + section_header + section_content
        config_file.write_text(new_content)

        if is_secrets:
            config_file.chmod(0o600)

        print("✓ Configuration saved!\n")
        print("Configuration Details:")
        print(f"  Environment: {target_site}")
        print(f"  Auth Method: {auth_display}")
        print(f"  Base URL: {base_url}")
        print(f"  Config File: {config_file}\n")
        print("You can now use the SDK with this configuration:")
        print("  from britecore_sdk.api.api_calls import get_api_client")
        print(f"  client = get_api_client('{target_site}').init_client()\n")

        return 0
    except Exception as e:
        print(f"✗ Failed to save configuration: {e}")
        logger.error(f"Config wizard failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
