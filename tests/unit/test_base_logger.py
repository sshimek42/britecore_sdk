"""Unit tests for base logger behavior."""

import logging
import uuid
from unittest.mock import patch

import pytest

from britecore_sdk.base_logger import get_logger


class _CountingHandler(logging.Handler):
    """Simple handler that stores emitted log records for assertions."""

    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.mark.unit
def test_get_logger_disables_propagation_to_root():
    """SDK logger should not propagate to root to avoid duplicate console lines."""
    logger_name = f"britecore_sdk.test.{uuid.uuid4().hex}"

    root_logger = logging.getLogger()
    root_handler = _CountingHandler()
    root_logger.addHandler(root_handler)

    logger = get_logger(logger_name, level="INFO", log_to_file=False)
    local_handler = _CountingHandler()
    logger.addHandler(local_handler)

    try:
        logger.info("hello")
        assert logger.propagate is False
        assert len(local_handler.records) == 1
        assert len(root_handler.records) == 0
    finally:
        logger.handlers.clear()
        root_logger.removeHandler(root_handler)


@pytest.mark.unit
def test_get_logger_does_not_add_duplicate_handlers_for_same_name():
    """Repeated get_logger calls should reuse existing handlers for the same logger."""
    logger_name = f"britecore_sdk.test.{uuid.uuid4().hex}"

    logger_a = get_logger(logger_name, level="INFO", log_to_file=False)
    handler_count = len(logger_a.handlers)
    logger_b = get_logger(logger_name, level="INFO", log_to_file=False)

    try:
        assert logger_a is logger_b
        assert logger_b.propagate is False
        assert len(logger_b.handlers) == handler_count
    finally:
        logger_b.handlers.clear()


@pytest.mark.unit
def test_get_logger_allows_runtime_debug_level_changes():
    """Raising logger level to DEBUG should emit debug without changing handler levels."""
    logger_name = f"britecore_sdk.test.{uuid.uuid4().hex}"
    logger = get_logger(logger_name, level="INFO", log_to_file=False)
    console_handler = logger.handlers[0]
    records: list[logging.LogRecord] = []

    assert console_handler.level == logging.NOTSET

    try:
        with patch.object(
            console_handler, "emit", side_effect=lambda record: records.append(record)
        ):
            logger.debug("hidden at info")
            logger.setLevel(logging.DEBUG)
            logger.debug("visible at debug")

        assert [record.getMessage() for record in records] == ["visible at debug"]
    finally:
        logger.handlers.clear()
