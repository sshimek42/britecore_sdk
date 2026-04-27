"""
Shared configuration validation and file I/O utilities.

This module provides common constants and functions used by both
check_site_configs.py (diagnostic) and config_manager.py (CRUD operations).
"""

import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

import toml  # type: ignore[import-untyped]

logger = logging.getLogger("britecore_sdk")

REQUIRED_KEYS = ["base_url"]
OAUTH_KEYS = ["client_id", "client_secret"]
API_KEY = "api_key"
FORBIDDEN_KEYS = ["api_key", "client_id", "client_secret"]
# Non-secret settings that can be managed by the config manager
# (examples: web_timeout, web_retry, target_site, web_timeout_long, etc.)
# Any key except FORBIDDEN_KEYS is allowed in settings.toml
SETTINGS_ONLY_KEYS = FORBIDDEN_KEYS  # Keys NOT allowed in settings.toml

BASE_DIR = Path(__file__).resolve().parent.parent
_PKG_SECRETS = BASE_DIR / "settings" / ".secrets.toml"
_PKG_SETTINGS = BASE_DIR / "settings" / "settings.toml"
_USER_DIR = Path.home() / ".britecore"
_USER_SECRETS = _USER_DIR / ".secrets.toml"
_USER_SETTINGS = _USER_DIR / "settings.toml"

# Prefer user-level files so the installed package directory is never required
# to hold credentials (it shouldn't — secrets don't belong in site-packages).
CONFIG_PATH: str = str(_USER_SECRETS if _USER_SECRETS.exists() else _PKG_SECRETS)
SETTINGS_PATH: str = str(_USER_SETTINGS if _USER_SETTINGS.exists() else _PKG_SETTINGS)


def load_secrets(path: str) -> dict:
    """Load site secrets from TOML, exiting with code 1 when missing.

    Args:
        path: Path to .secrets.toml file.

    Returns:
        Parsed TOML dictionary.

    Raises:
        SystemExit: If file does not exist.
    """
    if not os.path.exists(path):
        print(f"Config file not found: {path}")
        sys.exit(1)
    return toml.load(path)


def save_secrets(path: str, config: dict, backup: bool = True) -> None:
    """Save site secrets to TOML with optional backup.

    Args:
        path: Path to .secrets.toml file.
        config: Configuration dictionary to save.
        backup: If True, create a timestamped backup before overwriting.

    Raises:
        IOError: If file write fails.
    """
    if backup and os.path.exists(path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}.backup.{timestamp}"
        try:
            shutil.copy2(path, backup_path)
            logger.info("Backup created: %s", backup_path)
        except OSError as e:
            logger.warning("Could not create backup: %s", e)

    try:
        with open(path, "w") as f:
            toml.dump(config, f)
        logger.info("Configuration saved to %s", path)
    except OSError as e:
        logger.error("Failed to save configuration: %s", e)
        raise


def load_settings(path: str) -> dict:
    """Load non-secret settings from TOML, creating empty dict if missing.

    Args:
        path: Path to settings.toml file.

    Returns:
        Parsed TOML dictionary.
    """
    if not os.path.exists(path):
        logger.warning("Settings file not found: %s; using empty defaults", path)
        return {}
    return toml.load(path)


def save_settings(path: str, config: dict, backup: bool = True) -> None:
    """Save non-secret settings to TOML with optional backup.

    Args:
        path: Path to settings.toml file.
        config: Settings dictionary to save.
        backup: If True, create a timestamped backup before overwriting.

    Raises:
        IOError: If file write fails.
    """
    if backup and os.path.exists(path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"{path}.backup.{timestamp}"
        try:
            shutil.copy2(path, backup_path)
            logger.info("Backup created: %s", backup_path)
        except OSError as e:
            logger.warning("Could not create backup: %s", e)

    try:
        with open(path, "w") as f:
            toml.dump(config, f)
        logger.info("Settings saved to %s", path)
    except OSError as e:
        logger.error("Failed to save settings: %s", e)
        raise


def get_auth_mode(config: dict) -> str:
    """Return the auth mode that would be selected for this site config.

    Args:
        config: Site configuration dictionary.

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


def validate_site(_site_name: str, config: dict) -> tuple[bool, list[str]]:
    """Validate one site section and return status with missing required keys.

    Args:
        site_name: Name of the site (for context in errors).
        config: Site configuration dictionary.

    Returns:
        Tuple of (is_valid, missing_keys_list).
        is_valid is True if all required keys are present and auth is configured.
    """
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
    """Warn when sensitive keys are found in settings.toml instead of secrets.

    Args:
        path: Path to settings.toml file.
    """
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


def mask_secret(value: str, show_chars: int = 4) -> str:
    """Mask a secret value for display, showing only last N characters.

    Args:
        value: Secret value to mask.
        show_chars: Number of characters to show at end.

    Returns:
        Masked string (e.g., "****...abcd").
    """
    if not value or len(value) <= show_chars:
        return "****"
    return "****" + value[-show_chars:]


def validate_setting_key(key: str) -> tuple[bool, str | None]:
    """Validate that a setting key is allowed (not a forbidden secret key).

    Args:
        key: Setting key name.

    Returns:
        Tuple of (is_valid, error_message). error_message is None if valid.
    """
    if key in FORBIDDEN_KEYS:
        return False, f"Key '{key}' is a secret and must be managed in .secrets.toml"
    if not key or not isinstance(key, str):
        return False, "Key must be a non-empty string"
    return True, None
