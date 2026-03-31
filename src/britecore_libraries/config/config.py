"""Settings config"""

import os
from pathlib import Path
from typing import Any, Optional

from dynaconf import Dynaconf, Validator

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
    Validator("web_retry", "web_timeout", "web_timeout_long", is_type_of=int),
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

    def __init__(self, target_site: Optional[str] = None) -> None:
        """
        Initialize with a target site, falling back to the ``target_site``
        environment variable when *target_site* is ``None`` or empty.
        """
        self.target_site: Optional[str] = target_site or os.environ.get("target_site")

    def load_config(self) -> Any:
        """
        Load and return configuration settings for the target site.

        Returns:
            SimpleNamespace: Combined configuration settings for the target site.
        """
        from types import SimpleNamespace

        target_site: Optional[str] = self.target_site

        if target_site:
            try:
                with settings.using_env(target_site):
                    return SimpleNamespace(
                        base_url=settings.get("base_url", default=""),
                        client_id=settings.get("client_id", default=""),
                        client_secret=settings.get("client_secret", default=""),
                        api_key=settings.get("api_key", default=""),
                        web_retry=settings.get("web_retry"),
                        web_timeout=settings.get("web_timeout"),
                        web_timeout_long=settings.get("web_timeout_long"),
                        web_browser=settings.get("web_browser", default=""),
                    )
            except Exception:
                pass
        return settings

