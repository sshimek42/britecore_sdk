"""Settings config"""

import logging
import os
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf, Validator

from britecore_sdk.exceptions import BritecoreError

LOGGER = logging.getLogger(__name__)

curr_dir = Path(__file__).parent
setting_files: list[str] = [".secrets.toml", "settings.toml"]

setting_files_full: list[Path] = []
for each_file in setting_files:
    setting_files_full.append(curr_dir / each_file)

settings = Dynaconf(settings_files=setting_files_full, environments=True)

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
                            # Dynaconf supports both UPPERCASE and lowercase env vars, check both
                            env_val = os.environ.get(key) or os.environ.get(key.upper())
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
                                    "set all required keys in the environment."
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
