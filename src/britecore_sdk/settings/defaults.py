"""
Built-in defaults for optional configuration settings.

These defaults apply when a setting is missing from settings.toml or environment
variables. Users can override any default by adding the key to settings.toml.

Example override in settings.toml:
    [default]
    web_timeout = 10           # Override default 5 seconds
    web_retry = 3              # Override default 5 retries
"""

from typing import TypedDict


class ConfigDefaults(TypedDict, total=False):
    """Type hints for configuration defaults."""

    web_timeout: int
    web_timeout_long: int
    web_retry: int


# Core defaults: used when settings.toml or environment does not provide values
DEFAULTS: ConfigDefaults = {
    "web_timeout": 5,  # Standard HTTP timeout in seconds
    "web_retry": 5,  # Number of retries for failed HTTP requests
}


def get_default(key: str, default: int | str | None = None) -> int | str | None:
    """
    Retrieve a default value for a given setting key.

    Args:
        key: The configuration key (e.g., 'web_timeout').
        default: Optional fallback if key is not in DEFAULTS.

    Returns:
        The default value, or the provided fallback, or None.
    """
    return DEFAULTS.get(key, default)  # type: ignore


def calculate_long_timeout(web_timeout: int) -> int:
    """
    Calculate the long timeout as a multiple of the standard timeout.

    Convention: web_timeout_long = web_timeout * 10

    Args:
        web_timeout: Standard timeout value in seconds.

    Returns:
        Long timeout value in seconds.
    """
    return web_timeout * 10
