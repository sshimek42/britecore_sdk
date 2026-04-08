"""Settings config"""

import logging
import os
from pathlib import Path
from typing import Any

from dynaconf import Dynaconf, Validator

from britecore_libraries.exceptions import BritecoreError

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

    def __init__(self, target_site: str | None = None) -> None:
        """
        Initialize with a target site or the ``target_site`` environment value.
        """
        self.target_site: str | None = target_site or os.environ.get("target_site")

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
                    return SimpleNamespace(
                        base_url=settings.get("base_url", default=""),
                        client_id=settings.get("client_id", default=""),
                        client_secret=settings.get("client_secret", default=""),
                        api_key=settings.get("api_key", default=""),
                        db_conn_string=settings.get("db_conn_string", default=""),
                        db_conn_options=settings.get("db_conn_options", default={}),
                        web_retry=settings.get("web_retry"),
                        web_timeout=settings.get("web_timeout"),
                        web_timeout_long=settings.get("web_timeout_long"),
                        web_browser=settings.get("web_browser", default=""),
                    )
            except Exception as exc:
                raise BritecoreError.ConfigurationError(
                    f"Failed to load configuration for target_site '{target_site}': {exc}"
                ) from exc
        return settings


def load_database_config(target_site: str) -> tuple[str, dict[str, Any]]:
    """Load and validate database configuration for ODBC utilities.

    This keeps DB validation opt-in: only code paths that need ODBC call this
    helper, so API-only consumers are not required to define DB settings.
    """
    if not target_site or not target_site.strip():
        raise BritecoreError.ConfigurationError(
            "target_site is required to load database configuration"
        )

    with settings.using_env(target_site):
        conn_string = settings.get("db_conn_string")
        conn_options = settings.get("db_conn_options")

    missing_keys: list[str] = []
    if not conn_string:
        missing_keys.append("db_conn_string")
    if conn_options is None:
        missing_keys.append("db_conn_options")

    if missing_keys:
        keys = ", ".join(missing_keys)
        raise BritecoreError.ConfigurationError(
            f"Missing database configuration key(s) for '{target_site}': {keys}"
        )

    if not isinstance(conn_string, str):
        raise BritecoreError.ConfigurationError(
            f"Invalid type for '{target_site}.db_conn_string': expected str"
        )
    if not isinstance(conn_options, dict):
        raise BritecoreError.ConfigurationError(
            f"Invalid type for '{target_site}.db_conn_options': expected dict"
        )

    return conn_string, conn_options
