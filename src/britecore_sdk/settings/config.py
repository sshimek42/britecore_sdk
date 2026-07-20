"""Configuration management for BriteCore SDK.

This module implements a layered configuration system using Dynaconf to manage
SDK settings from multiple sources with a defined priority order:

1. **SDK package defaults** — ``settings.toml`` and ``.secrets.toml``
2. **User-level config** — ``~/.britecore/settings.toml`` and ``.secrets.toml``
3. **Project-local config** — ``britecore.toml`` and ``.britecore_secrets.toml``
4. **Explicit file path** — ``BRITECORE_SDK_SETTINGS_FILE`` environment variable
5. **Environment variables** — ``BRITECORE_SDK_*`` (highest priority)

The module provides functions to discover and load configuration files, validate
required settings, and access configuration values through the global settings object.

Functions:
    _discover_settings_files: Build ordered list of settings files to load.
    _validate_site_settings: Verify required keys for a target site.
    get_settings: Access the global settings object (Dynaconf instance).
"""

import logging
import os
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf, Validator

from britecore_sdk.exceptions import BritecoreError

LOGGER = logging.getLogger(__name__)


def _discover_settings_files() -> list[Path]:
    """Return an ordered list of settings files to load, from lowest to highest priority.

    Priority order (earlier = lower, later = higher priority; all are overridden by
    ``BRITECORE_SDK_*`` environment variables):

    1. **SDK package defaults** — ``settings.toml`` / ``.secrets.toml`` inside the
       installed package directory. Loaded when they exist (they are in .gitignore
       and are not required for operation).
    2. **User-level config** — ``~/.britecore/settings.toml`` and
       ``~/.britecore/.secrets.toml``.  Loaded when they exist; useful for
       developer workstation defaults that span many projects.
    3. **Project-local config** — ``britecore.toml`` and ``.britecore_secrets.toml``
       in the current working directory.  Loaded when they exist; intended for
       per-project credentials checked into the project (non-secret) or kept out of
       version control (secrets).
    4. **Explicit env-var override** — the path given by
       ``BRITECORE_SDK_SETTINGS_FILE``.  Loaded last (highest file priority) when
       the variable is set and points to an existing file.

    Returns:
        List of :class:`~pathlib.Path` objects for all settings files that should be
        passed to Dynaconf's ``settings_files`` parameter.  Files that do not exist
        are omitted so Dynaconf does not raise ``FileNotFoundError``.
    """
    candidates: list[Path] = []

    # 1. SDK package defaults — settings.toml and .secrets.toml may be present
    #    (both are in .gitignore and are optional for operation).
    sdk_dir = Path(__file__).parent
    for name in ("settings.toml", ".secrets.toml"):
        p = sdk_dir / name
        if p.exists():
            candidates.append(p)

    # 2. User-level config (~/.britecore/)
    user_dir = Path.home() / ".britecore"
    for name in ("settings.toml", ".secrets.toml"):
        p = user_dir / name
        if p.exists():
            candidates.append(p)

    # 3. Project-local config (CWD)
    cwd = Path.cwd()
    for name in ("britecore.toml", ".britecore_secrets.toml"):
        p = cwd / name
        if p.exists():
            candidates.append(p)

    # 4. Explicit env-var override (highest file priority)
    env_path_str = os.environ.get("BRITECORE_SDK_SETTINGS_FILE")
    if env_path_str:
        env_path = Path(env_path_str)
        if env_path.exists():
            candidates.append(env_path)
        else:
            LOGGER.warning(
                "BRITECORE_SDK_SETTINGS_FILE points to a non-existent file: %s",
                env_path,
            )

    LOGGER.debug(
        "Discovered %d settings file(s): %s",
        len(candidates),
        [str(p) for p in candidates],
    )
    return candidates


setting_files_full: list[Path] = _discover_settings_files()

settings = Dynaconf(
    settings_files=setting_files_full,
    environments=True,
    envvar_prefix="BRITECORE_SDK",
)


def get_target_site() -> str | None:
    """
    Return the active target site name from settings or the environment.

    Resolution order (first non-empty value wins):

    1. ``target_site`` key in ``settings.toml`` (under ``[default]`` or a
       site-specific section).
    2. ``target_site`` environment variable (backward-compatible fallback).

    Returns:
        The target site name, or ``None`` if neither source provides one.
    """
    # Dynaconf reads TOML values; os.environ fallback preserves backward
    # compatibility with the historical env-var-only approach.
    site: str | None = settings.get("target_site", default=None) or os.environ.get(
        "target_site"
    )
    return site


settings.validators.register(
    Validator(
        "base_url",
        "client_id",
        "client_secret",
        "api_key",
        must_exist=True,
        is_type_of=str,
    ),
)
# Only validate site-specific keys when an explicit (non-default) environment
# is active.  The default environment intentionally omits API credentials, so
# running validators unconditionally causes a ValidationError on import.
_active_env = os.environ.get("ENV_FOR_DYNACONF", "default").lower()
if _active_env != "default":
    settings.validators.validate()


class LoadClientSettings:
    """
    Loads and manages client configuration settings for a specified target site.

    This class is responsible for initializing with a target site and loading
    configuration settings that combine default settings with site-specific
    overrides.
    """

    def __init__(self, target_site: str) -> None:
        """Initialize with a target site; environment fallback is not allowed."""
        if not target_site:
            raise BritecoreError.ConfigurationError(
                "target_site must be specified explicitly; environment fallback is not allowed."
            )
        self.target_site: str = target_site
        self._warned_hybrid_config = False

    def load_config(self) -> Any:
        """
        Load and return configuration settings for the target site.

        Returns:
            SimpleNamespace: Combined configuration settings for the target site.

        Raises:
            BritecoreError.ConfigurationError: If target site configuration
                fails to load.
        """
        from types import SimpleNamespace

        target_site: str | None = self.target_site

        if target_site:
            try:
                with settings.using_env(target_site):
                    # --- Begin hybrid config warning logic ---
                    # Only warn once per process
                    if not self._warned_hybrid_config:
                        required_keys = [
                            "base_url",
                            "client_id",
                            "client_secret",
                            "api_key",
                        ]
                        missing_env_keys = []
                        for key in required_keys:
                            # required_keys contains lowercase names (e.g. "base_url").
                            # Dynaconf reads BRITECORE_SDK_BASE_URL for key "base_url",
                            # so we uppercase the key to form the expected env var name.
                            env_key = f"BRITECORE_SDK_{key.upper()}"
                            env_val = os.environ.get(env_key)
                            config_val = settings.get(key, default=None)
                            if not env_val and config_val:
                                missing_env_keys.append(key)
                        if missing_env_keys:
                            LOGGER.warning(
                                (
                                    "Hybrid config: The following required keys were missing "
                                    "from environment variables and loaded from config files "
                                    "instead: %s. This means a mix of env and config file "
                                    "values is being used. For full environment-only config, "
                                    "set all required keys as BRITECORE_SDK_* environment "
                                    "variables (e.g., BRITECORE_SDK_BASE_URL)."
                                ),
                                ", ".join(missing_env_keys),
                            )
                        self._warned_hybrid_config = True
                    # --- End hybrid config warning logic ---
                    return SimpleNamespace(
                        base_url=settings.get("base_url", default=""),
                        client_id=settings.get("client_id", default=""),
                        client_secret=settings.get("client_secret", default=""),
                        api_key=settings.get("api_key", default=""),
                    )
            except Exception as exc:
                raise BritecoreError.ConfigurationError(
                    f"Failed to load configuration for target_site '{target_site}': {exc}"
                ) from exc
        return settings
