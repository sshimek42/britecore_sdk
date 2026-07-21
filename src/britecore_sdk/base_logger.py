"""Library-safe logging helpers built on Python's standard logging module."""

import logging
from enum import StrEnum
from pathlib import Path
from typing import Any


class LogCategory(StrEnum):
    """Standard logging categories for observability and filtering."""

    AUTH = "auth"  # OAuth token, credential validation
    HTTP = "http"  # Raw request/response (redacted)
    RATE_LIMIT = "rate_limit"  # Rate limit state changes
    CACHE = "cache"  # Cache hits/misses
    PERF = "perf"  # Timing measurements
    CONFIG = "config"  # Configuration resolution


_DEFAULT_FORMAT = (
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
)


def _to_log_level(level: str | int) -> int:
    """Resolve string/int log levels into logging module constants."""
    if isinstance(level, int):
        return level
    return getattr(logging, str(level).upper())


def get_logger(name: str = "britecore_sdk") -> logging.Logger:
    """Return the SDK logger with a NullHandler attached by default.

    SDK code should emit records but avoid configuring global/root logging behavior.
    Applications can opt in to SDK-local handlers via ``configure_logging``.
    """
    logger = logging.getLogger(name)
    logger.propagate = False

    if not logger.handlers:
        logger.addHandler(logging.NullHandler())

    return logger


def configure_logging(
    name: str = "britecore_sdk",
    level: str | int = "INFO",
    *,
    log_to_file: bool = False,
    log_file_level: str | int | None = None,
) -> logging.Logger:
    """Opt in to SDK-managed stream/file handlers.

    This helper is intentionally explicit so SDK import does not alter host app logging.
    """
    logger = get_logger(name)
    logger.setLevel(_to_log_level(level))

    if not any(
        not isinstance(handler, logging.NullHandler) for handler in logger.handlers
    ):
        logger.handlers.clear()

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.NOTSET)
        console_handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
        logger.addHandler(console_handler)

        if log_to_file:
            file_level = level if log_file_level is None else log_file_level
            log_dir = Path.home() / ".britecore_logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"{name}.log"

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(_to_log_level(file_level))
            file_handler.setFormatter(logging.Formatter(_DEFAULT_FORMAT))
            logger.addHandler(file_handler)

    return logger


def log_with_category(
    logger: logging.Logger,
    level: int,
    message: str,
    category: LogCategory | str,
    **extra_fields: Any,
) -> None:
    """Log a message with a category and optional extra fields.

    This helper adds structured logging support with categories and extra fields
    that can be used for filtering and monitoring.

    Args:
        logger: Logger instance to use.
        level: Log level (e.g., logging.INFO, logging.DEBUG).
        message: Log message.
        category: LogCategory enum value or string.
        **extra_fields: Additional key-value pairs to include in the log extra dict.

    Example::

        from britecore_sdk.base_logger import get_logger, log_with_category, LogCategory

        logger = get_logger()
        log_with_category(
            logger,
            logging.DEBUG,
            "Token refresh successful",
            LogCategory.AUTH,
            token_expires_in=3600
        )
    """
    extra = {"category": str(category)}
    extra.update(extra_fields)
    logger.log(level, message, extra=extra)
