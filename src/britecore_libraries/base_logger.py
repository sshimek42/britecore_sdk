"""Logger configuration using Python's built-in logging module."""

import logging
from pathlib import Path


def get_logger(
    name: str,
    level: str = "INFO",
    log_to_file: bool = True,
    log_file_level: str = "INFO",
) -> logging.Logger:
    """
    Create and configure a logger instance with both console and optional file output.

    This function provides a simple way to set up a logger with sensible defaults,
    supporting both console output and file output. It replaces the previous SCLogging
    wrapper with Python's built-in logging module.

    Args:
        name: The logger name (typically __package__ or module name)
        level: Console output log level (default: "INFO")
        log_to_file: Whether to enable file logging (default: True)
        log_file_level: File output log level (default: "INFO")

    Returns:
        logging.Logger: A configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured (prevent duplicate handlers)
    if not logger.handlers:
        logger.setLevel(getattr(logging, level))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level))
        console_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler (optional)
        if log_to_file:
            log_dir = Path.home() / ".britecore_logs"
            log_dir.mkdir(exist_ok=True)
            log_file = log_dir / f"{name}.log"

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, log_file_level))
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

    return logger
