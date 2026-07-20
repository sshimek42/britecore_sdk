"""
Built-in defaults for optional configuration settings.

These defaults apply when a setting is missing from settings.toml or environment
variables. Users can override any default by adding the key to settings.toml.

Example override in settings.toml:
    [default]
    web_timeout = 10           # Override default 5 seconds
    web_retry = 3              # Override default 5 retries
"""

from typing import Any, TypedDict


class ConfigDefaults(TypedDict, total=False):
    """Type hints for configuration defaults."""

    web_timeout: int
    web_timeout_long: int
    web_retry: int
    rate_limiter_enabled: bool
    rate_limiter_requests_per_second: float
    rate_limiter_burst_size: int
    rate_limiter_adaptive_backoff: bool
    rate_limiter_backoff_timeout_seconds: float


# Core defaults: used when settings.toml or environment does not provide values
DEFAULTS: ConfigDefaults = {
    "web_timeout": 5,  # Standard HTTP timeout in seconds
    "web_retry": 5,  # Number of retries for failed HTTP requests
    "rate_limiter_enabled": False,  # Disabled by default; opt-in
    "rate_limiter_requests_per_second": 10.0,  # Target rate: 10 requests/second
    "rate_limiter_burst_size": 20,  # Allow up to 20-request bursts
    "rate_limiter_adaptive_backoff": True,  # Automatically back off on 429
    "rate_limiter_backoff_timeout_seconds": 60.0,  # Back off for 60 seconds after 429
}


def get_default(key: str, default: Any = None) -> Any:
    """
    Retrieve a default value for a given setting key.

    Args:
        key: The configuration key (e.g., 'web_timeout').
        default: Optional fallback if key is not in DEFAULTS.

    Returns:
        The default value, or the provided fallback, or None.
    """
    return DEFAULTS.get(key, default)


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
