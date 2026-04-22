"""
Configuration manager for adding, updating, deleting, and listing sites.

Provides a ConfigManager class that wraps Dynaconf + file I/O for safe
configuration management with validation and backup.

Usage (programmatic):
    manager = ConfigManager()
    manager.add_site("production", "https://api.example.com", "oauth",
                     client_id="...", client_secret="...")
    manager.list_sites()
    manager.update_site("production", base_url="https://new-api.example.com")
    manager.delete_site("production")

Usage (interactive):
    python -c "from britecore_sdk.utils.config_manager import interactive_config_menu; interactive_config_menu()"
"""

from typing import Any, Literal

from britecore_sdk import logger
from britecore_sdk.settings.defaults import DEFAULTS
from britecore_sdk.utils._config_common import (
    API_KEY,
    CONFIG_PATH,
    SETTINGS_PATH,
    get_auth_mode,
    load_secrets,
    load_settings,
    mask_secret,
    save_secrets,
    save_settings,
    validate_setting_key,
    validate_site,
    warn_if_secrets_in_settings,
)


class ConfigManager:
    """Manage BriteCore API site configurations with validation and backups.

    Manages both secret configurations (.secrets.toml) and non-secret settings
    (settings.toml) with validation and automatic backups.
    """

    def __init__(
        self, config_path: str = CONFIG_PATH, settings_path: str = SETTINGS_PATH
    ):
        """Initialize the config manager.

        Args:
            config_path: Path to .secrets.toml file.
            settings_path: Path to settings.toml file.
        """
        self.config_path = config_path
        self.settings_path = settings_path
        self.config = load_secrets(config_path)
        self.settings = load_settings(settings_path)

    def reload(self) -> None:
        """Reload both configuration files from disk."""
        self.config = load_secrets(self.config_path)
        self.settings = load_settings(self.settings_path)
        logger.info("Configuration reloaded from disk")

    def list_sites(self, mask_secrets: bool = True) -> list[dict]:
        """List all configured sites with their status.

        Args:
            mask_secrets: If True, mask sensitive values in output.

        Returns:
            List of site dictionaries with keys: name, status, auth_mode, base_url, missing_keys.
        """
        site_sections = {k: v for k, v in self.config.items() if isinstance(v, dict)}
        sites = []
        for site_name, config in site_sections.items():
            is_valid, missing = validate_site(site_name, config)
            auth_mode = get_auth_mode(config)
            base_url = config.get("base_url", "")

            site_info = {
                "name": site_name,
                "status": "OK" if is_valid else "INCOMPLETE",
                "auth_mode": auth_mode,
                "base_url": base_url,
                "missing_keys": missing,
            }

            if mask_secrets:
                # Add masked credential info
                if auth_mode == "OAuth":
                    site_info["client_id"] = mask_secret(str(config.get("client_id", "")))
                    site_info["client_secret"] = mask_secret(
                        str(config.get("client_secret", ""))
                    )
                elif auth_mode == "API Key":
                    site_info["api_key"] = mask_secret(str(config.get(API_KEY, "")))

            sites.append(site_info)

        return sites

    def get_site(self, site_name: str) -> dict | None:
        """Retrieve a specific site configuration.

        Args:
            site_name: Name of the site.

        Returns:
            Site configuration dictionary, or None if not found.
        """
        return self.config.get(site_name)

    def add_site(
        self,
        site_name: str,
        base_url: str,
        auth_type: Literal["oauth", "api_key"],
        **credentials: Any,
    ) -> tuple[bool, str]:
        """Add a new site to the configuration.

        Args:
            site_name: Name of the site (must be unique).
            base_url: API base URL.
            auth_type: Either "oauth" or "api_key".
            **credentials: For oauth: client_id, client_secret.
                          For api_key: api_key.

        Returns:
            Tuple of (success: bool, message: str).
        """
        if site_name in self.config:
            return False, f"Site '{site_name}' already exists"

        config = {"base_url": base_url}

        if auth_type == "oauth":
            if "client_id" not in credentials or "client_secret" not in credentials:
                return False, "OAuth requires 'client_id' and 'client_secret'"
            config.update(
                {
                    "client_id": credentials["client_id"],
                    "client_secret": credentials["client_secret"],
                }
            )
        elif auth_type == "api_key":
            if "api_key" not in credentials:
                return False, "API Key auth requires 'api_key'"
            config["api_key"] = credentials["api_key"]
        else:
            return False, f"Unknown auth_type: {auth_type}"

        # Validate before saving
        is_valid, missing = validate_site(site_name, config)
        if not is_valid:
            return False, f"Configuration invalid. Missing: {', '.join(missing)}"

        self.config[site_name] = config
        try:
            save_secrets(self.config_path, self.config, backup=True)
            logger.info("Site '%s' added successfully", site_name)
            return True, f"Site '{site_name}' added successfully"
        except OSError as e:
            # Revert on save failure
            self.reload()
            return False, f"Failed to save configuration: {e}"

    def update_site(self, site_name: str, **updates: Any) -> tuple[bool, str]:
        """Update an existing site configuration.

        Args:
            site_name: Name of the site to update.
            **updates: Fields to update (base_url, client_id, client_secret, api_key, etc.).

        Returns:
            Tuple of (success: bool, message: str).
        """
        if site_name not in self.config:
            return False, f"Site '{site_name}' not found"

        if not isinstance(self.config[site_name], dict):
            return False, f"Site '{site_name}' is not a valid configuration"

        # Merge updates into existing config
        updated_config = {**self.config[site_name], **updates}

        # Validate before saving
        is_valid, missing = validate_site(site_name, updated_config)
        if not is_valid:
            return (
                False,
                f"Configuration invalid after update. Missing: {', '.join(missing)}",
            )

        self.config[site_name] = updated_config
        try:
            save_secrets(self.config_path, self.config, backup=True)
            logger.info("Site '%s' updated successfully", site_name)
            return True, f"Site '{site_name}' updated successfully"
        except OSError as e:
            # Revert on save failure
            self.reload()
            return False, f"Failed to save configuration: {e}"

    def delete_site(self, site_name: str) -> tuple[bool, str]:
        """Delete a site from the configuration.

        Args:
            site_name: Name of the site to delete.

        Returns:
            Tuple of (success: bool, message: str).
        """
        if site_name not in self.config:
            return False, f"Site '{site_name}' not found"

        del self.config[site_name]
        try:
            save_secrets(self.config_path, self.config, backup=True)
            logger.info("Site '%s' deleted successfully", site_name)
            return True, f"Site '{site_name}' deleted successfully"
        except OSError as e:
            # Revert on save failure
            self.reload()
            return False, f"Failed to save configuration: {e}"

    def export_backup(self, backup_path: str) -> tuple[bool, str]:
        """Export current configuration to a backup file.

        Args:
            backup_path: Path where backup should be saved.

        Returns:
            Tuple of (success: bool, message: str).
        """
        try:
            save_secrets(backup_path, self.config, backup=False)
            return True, f"Configuration backed up to {backup_path}"
        except OSError as e:
            return False, f"Failed to create backup: {e}"

    # === Non-secret settings management ===

    def list_settings(self) -> dict:
        """List all non-secret settings by section.

        Returns:
            Dictionary with section names as keys and their settings as values.
        """
        return dict(self.settings)

    @staticmethod
    def get_available_defaults() -> dict:
        """Get all available configuration defaults.

        These defaults are applied when a setting is not provided in settings.toml.
        Users can override any default by adding the key to settings.toml.

        Returns:
            Dictionary mapping setting keys to their default values.
        """
        return dict(DEFAULTS)

    def get_setting(self, section: str, key: str) -> Any:
        """Get a specific setting value.

        Args:
            section: Section name (e.g., 'default', 'wausau').
            key: Setting key.

        Returns:
            The setting value, or None if not found.
        """
        if section not in self.settings:
            return None
        if not isinstance(self.settings[section], dict):
            return None
        return self.settings[section].get(key)

    def add_setting(self, section: str, key: str, value: Any) -> tuple[bool, str]:
        """Add or update a non-secret setting.

        Args:
            section: Section name (e.g., 'default', 'wausau').
            key: Setting key name.
            value: Setting value (must be serializable to TOML).

        Returns:
            Tuple of (success: bool, message: str).
        """
        # Validate key is not a forbidden secret key
        is_valid, error = validate_setting_key(key)
        if not is_valid:
            return False, error or "Invalid setting key"

        # Ensure section exists
        if section not in self.settings:
            self.settings[section] = {}

        # Ensure section is a dict
        if not isinstance(self.settings[section], dict):
            return False, f"Section '{section}' is not a valid settings section"

        # Add/update the setting
        self.settings[section][key] = value

        try:
            save_settings(self.settings_path, self.settings, backup=True)
            logger.info("Setting '%s.%s' = %r saved successfully", section, key, value)
            return True, f"Setting '{section}.{key}' added/updated successfully"
        except OSError as e:
            # Revert on save failure
            self.reload()
            return False, f"Failed to save settings: {e}"

    def update_setting(self, section: str, key: str, value: Any) -> tuple[bool, str]:
        """Update an existing non-secret setting.

        Args:
            section: Section name.
            key: Setting key.
            value: New value.

        Returns:
            Tuple of (success: bool, message: str).
        """
        if section not in self.settings:
            return False, f"Section '{section}' not found"

        if not isinstance(self.settings[section], dict):
            return False, f"Section '{section}' is not a valid settings section"

        if key not in self.settings[section]:
            return False, f"Setting '{section}.{key}' not found"

        # Validate key is not a forbidden secret key (defensive check)
        is_valid, error = validate_setting_key(key)
        if not is_valid:
            return False, error or "Invalid setting key"

        self.settings[section][key] = value

        try:
            save_settings(self.settings_path, self.settings, backup=True)
            logger.info("Setting '%s.%s' updated successfully", section, key)
            return True, f"Setting '{section}.{key}' updated successfully"
        except OSError as e:
            # Revert on save failure
            self.reload()
            return False, f"Failed to save settings: {e}"

    def delete_setting(self, section: str, key: str) -> tuple[bool, str]:
        """Delete a non-secret setting.

        Args:
            section: Section name.
            key: Setting key.

        Returns:
            Tuple of (success: bool, message: str).
        """
        if section not in self.settings:
            return False, f"Section '{section}' not found"

        if not isinstance(self.settings[section], dict):
            return False, f"Section '{section}' is not a valid settings section"

        if key not in self.settings[section]:
            return False, f"Setting '{section}.{key}' not found"

        del self.settings[section][key]

        # Remove empty sections
        if not self.settings[section]:
            del self.settings[section]

        try:
            save_settings(self.settings_path, self.settings, backup=True)
            logger.info("Setting '%s.%s' deleted successfully", section, key)
            return True, f"Setting '{section}.{key}' deleted successfully"
        except OSError as e:
            # Revert on save failure
            self.reload()
            return False, f"Failed to save settings: {e}"


def interactive_config_menu() -> None:
    """Interactive menu for managing configuration.

    Provides a loop where users can:
    1. Manage API sites (list, add, update, delete)
    2. Manage non-secret settings (list, add, update, delete)
    3. Export backup
    4. Exit
    """
    warn_if_secrets_in_settings(SETTINGS_PATH)
    manager = ConfigManager()

    while True:
        print("\n" + "=" * 60)
        print("BriteCore Configuration Manager")
        print("=" * 60)
        print("1. Manage API Sites")
        print("2. Manage Settings")
        print("3. Export backup")
        print("4. Exit")
        print("-" * 60)

        choice = input("Select an option (1-4): ").strip()

        if choice == "1":
            _sites_menu(manager)
        elif choice == "2":
            _settings_menu(manager)
        elif choice == "3":
            _export_backup_interactive(manager)
        elif choice == "4":
            print("Exiting.")
            break
        else:
            print("Invalid option. Please select 1-4.")


def _sites_menu(manager: ConfigManager) -> None:
    """Sub-menu for managing API sites."""
    while True:
        print("\n" + "-" * 60)
        print("API Sites Management")
        print("-" * 60)
        print("1. List sites")
        print("2. Add new site")
        print("3. Update site")
        print("4. Delete site")
        print("5. Back to main menu")
        print("-" * 60)

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            _list_sites_interactive(manager)
        elif choice == "2":
            _add_site_interactive(manager)
        elif choice == "3":
            _update_site_interactive(manager)
        elif choice == "4":
            _delete_site_interactive(manager)
        elif choice == "5":
            break
        else:
            print("Invalid option. Please select 1-5.")


def _settings_menu(manager: ConfigManager) -> None:
    """Sub-menu for managing non-secret settings."""
    while True:
        print("\n" + "-" * 60)
        print("Settings Management")
        print("-" * 60)
        print("1. List all settings")
        print("2. Add/update setting")
        print("3. Delete setting")
        print("4. View available defaults")
        print("5. Back to main menu")
        print("-" * 60)

        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            _list_settings_interactive(manager)
        elif choice == "2":
            _add_update_setting_interactive(manager)
        elif choice == "3":
            _delete_setting_interactive(manager)
        elif choice == "4":
            _show_defaults(manager)
        elif choice == "5":
            break
        else:
            print("Invalid option. Please select 1-5.")


def _list_sites_interactive(manager: ConfigManager) -> None:
    """Display list of sites interactively."""
    sites = manager.list_sites(mask_secrets=True)
    if not sites:
        print("No sites configured.")
        return

    print(f"\nConfigured sites ({len(sites)}):")
    print(f"{'Site':<20} {'Status':<12} {'Auth':<10} {'URL':<40}")
    print("-" * 82)
    for site in sites:
        print(
            f"{site['name']:<20} {site['status']:<12} "
            f"{site['auth_mode']:<10} {site['base_url']:<40}"
        )
        if site["missing_keys"]:
            print(f"  ⚠ Missing: {', '.join(site['missing_keys'])}")


def _add_site_interactive(manager: ConfigManager) -> None:
    """Prompt for and add a new site."""
    print("\n--- Add New Site ---")
    site_name = input("Site name: ").strip()
    if not site_name:
        print("Site name cannot be empty.")
        return

    base_url = input("Base URL (e.g., https://api.example.com): ").strip()
    if not base_url:
        print("Base URL cannot be empty.")
        return

    print("\nAuthentication type:")
    print("1. OAuth (client_id + client_secret)")
    print("2. API Key")
    auth_choice = input("Select (1 or 2): ").strip()

    if auth_choice == "1":
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()
        if not client_id or not client_secret:
            print("Client ID and Secret cannot be empty.")
            return
        _, msg = manager.add_site(
            site_name,
            base_url,
            "oauth",
            client_id=client_id,
            client_secret=client_secret,
        )
    elif auth_choice == "2":
        api_key = input("API Key: ").strip()
        if not api_key:
            print("API Key cannot be empty.")
            return
        _, msg = manager.add_site(site_name, base_url, "api_key", api_key=api_key)
    else:
        print("Invalid auth type.")
        return

    print(msg)


def _update_site_interactive(manager: ConfigManager) -> None:
    """Prompt for and update an existing site."""
    print("\n--- Update Site ---")
    site_name = input("Site name to update: ").strip()
    site = manager.get_site(site_name)
    if not site:
        print(f"Site '{site_name}' not found.")
        return

    print(f"\nCurrent config for '{site_name}':")
    print(f"  Base URL: {site.get('base_url', 'N/A')}")
    auth_mode = get_auth_mode(site)
    print(f"  Auth Mode: {auth_mode}")

    print("\nWhat would you like to update?")
    print("1. Base URL")
    print("2. Client ID (OAuth)")
    print("3. Client Secret (OAuth)")
    print("4. API Key")
    print("5. Cancel")

    choice = input("Select (1-5): ").strip()

    updates = {}
    if choice == "1":
        base_url = input("New Base URL: ").strip()
        if base_url:
            updates["base_url"] = base_url
    elif choice == "2":
        client_id = input("New Client ID: ").strip()
        if client_id:
            updates["client_id"] = client_id
    elif choice == "3":
        client_secret = input("New Client Secret: ").strip()
        if client_secret:
            updates["client_secret"] = client_secret
    elif choice == "4":
        api_key = input("New API Key: ").strip()
        if api_key:
            updates[API_KEY] = api_key
    elif choice == "5":
        return
    else:
        print("Invalid option.")
        return

    if updates:
        _, msg = manager.update_site(site_name, **updates)
        print(msg)
    else:
        print("No updates provided.")


def _delete_site_interactive(manager: ConfigManager) -> None:
    """Prompt for and delete a site."""
    print("\n--- Delete Site ---")
    site_name = input("Site name to delete: ").strip()

    confirm = (
        input(f"Are you sure you want to delete '{site_name}'? (yes/no): ")
        .strip()
        .lower()
    )
    if confirm != "yes":
        print("Deletion cancelled.")
        return

    _, msg = manager.delete_site(site_name)
    print(msg)


def _export_backup_interactive(manager: ConfigManager) -> None:
    """Prompt for and export a backup."""
    print("\n--- Export Backup ---")
    backup_path = input("Backup file path: ").strip()
    if not backup_path:
        print("Backup path cannot be empty.")
        return

    _, msg = manager.export_backup(backup_path)
    print(msg)


def _list_settings_interactive(manager: ConfigManager) -> None:
    """Display all non-secret settings interactively."""
    settings = manager.list_settings()
    if not settings:
        print("No settings configured.")
        return

    print("\nConfigured settings:")
    for section, section_settings in sorted(settings.items()):
        if isinstance(section_settings, dict):
            print(f"\n[{section}]")
            for key, value in sorted(section_settings.items()):
                print(f"  {key} = {repr(value)}")
        else:
            print(f"\n{section} = {repr(section_settings)}")


def _show_defaults(manager: ConfigManager) -> None:
    """Display available configuration defaults."""
    defaults = manager.get_available_defaults()
    if not defaults:
        print("No defaults configured.")
        return

    print("\nAvailable Configuration Defaults:")
    print("(These apply when a setting is not in settings.toml)")
    print("-" * 60)
    for key, value in sorted(defaults.items()):
        print(f"  {key:<20} = {repr(value)}")
    print("-" * 60)
    print("To override a default, add the key to settings.toml:")
    print("  [default]")
    print("  web_timeout = 10  # Override default 5 seconds")


def _add_update_setting_interactive(manager: ConfigManager) -> None:
    """Prompt for and add/update a setting."""
    print("\n--- Add/Update Setting ---")
    section = input("Section (default='default'): ").strip() or "default"
    key = input("Setting key (e.g., 'web_timeout', 'target_site'): ").strip()
    if not key:
        print("Setting key cannot be empty.")
        return

    # Validate key first
    is_valid, error = validate_setting_key(key)
    if not is_valid:
        print(f"Invalid key: {error}")
        return

    value_str = input(
        "Setting value (JSON format for complex types, or string): "
    ).strip()
    if not value_str:
        print("Setting value cannot be empty.")
        return

    # Try to parse as JSON for complex types, otherwise use as string
    import json

    try:
        # Try JSON first for numbers, booleans, lists, dicts
        if value_str.lower() in ("true", "false"):
            value = value_str.lower() == "true"
        elif value_str.lower() in ("null", "none"):
            value = None
        else:
            try:
                value = json.loads(value_str)
            except json.JSONDecodeError:
                # If not valid JSON, treat as string
                value = value_str
    except Exception:
        value = value_str

    _, msg = manager.add_setting(section, key, value)
    print(msg)


def _delete_setting_interactive(manager: ConfigManager) -> None:
    """Prompt for and delete a setting."""
    print("\n--- Delete Setting ---")
    section = input("Section (default='default'): ").strip() or "default"
    key = input("Setting key to delete: ").strip()
    if not key:
        print("Setting key cannot be empty.")
        return

    confirm = (
        input(f"Are you sure you want to delete '{section}.{key}'? (yes/no): ")
        .strip()
        .lower()
    )
    if confirm != "yes":
        print("Deletion cancelled.")
        return

    _, msg = manager.delete_setting(section, key)
    print(msg)


if __name__ == "__main__":
    interactive_config_menu()
