"""Unit tests for base logger behavior."""

import logging
import uuid

import pytest

from britecore_sdk.base_logger import configure_logging, get_logger


class _CountingHandler(logging.Handler):
    """Simple handler that stores emitted log records for assertions."""

    def __init__(self):
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.records.append(record)


@pytest.mark.unit
def test_get_logger_uses_null_handler_by_default():
    """SDK logger should be safe for libraries until users opt into handlers."""
    logger_name = f"britecore_sdk.test.{uuid.uuid4().hex}"
    logger = get_logger(logger_name)

    try:
        assert logger.propagate is False
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.NullHandler)
    finally:
        logger.handlers.clear()


@pytest.mark.unit
def test_get_logger_does_not_add_duplicate_handlers_for_same_name():
    """Repeated get_logger calls should reuse existing handlers for the same logger."""
    logger_name = f"britecore_sdk.test.{uuid.uuid4().hex}"

    logger_a = get_logger(logger_name)
    handler_count = len(logger_a.handlers)
    logger_b = get_logger(logger_name)

    try:
        assert logger_a is logger_b
        assert logger_b.propagate is False
        assert len(logger_b.handlers) == handler_count
    finally:
        logger_b.handlers.clear()


@pytest.mark.unit
def test_configure_logging_adds_stream_handler_and_emits_records():
    """configure_logging should replace NullHandler with a usable stream handler."""
    logger_name = f"britecore_sdk.test.{uuid.uuid4().hex}"
    logger = configure_logging(logger_name, level="INFO")
    stream_handler = logger.handlers[0]
    counter_handler = _CountingHandler()
    counter_handler.setLevel(logging.NOTSET)
    logger.addHandler(counter_handler)

    assert logger.level == logging.INFO
    assert logger.propagate is False
    assert not isinstance(stream_handler, logging.NullHandler)
    assert stream_handler.level == logging.NOTSET

    logger.info("visible at info")
    logger.debug("hidden at info")

    assert [record.getMessage() for record in counter_handler.records] == [
        "visible at info"
    ]
    logger.handlers.clear()


@pytest.mark.unit
def test_configure_logging_is_idempotent_for_same_logger():
    """Repeated configure_logging calls should not duplicate handlers."""
    logger_name = f"britecore_sdk.test.{uuid.uuid4().hex}"
    logger = configure_logging(logger_name, level="INFO")

    try:
        initial_handlers = list(logger.handlers)
        configure_logging(logger_name, level="DEBUG")

        assert logger.level == logging.DEBUG
        assert logger.handlers == initial_handlers
    finally:
        logger.handlers.clear()


@pytest.mark.unit
def test_configure_logging_preserves_existing_custom_handlers():
    """SDK helper should not replace custom handlers already attached by applications."""
    logger_name = f"britecore_sdk.test.{uuid.uuid4().hex}"
    logger = get_logger(logger_name)
    custom_handler = _CountingHandler()

    try:
        logger.handlers.clear()
        logger.addHandler(custom_handler)
        configure_logging(logger_name, level="INFO")

        assert logger.handlers == [custom_handler]
        logger.info("custom")
        assert [record.getMessage() for record in custom_handler.records] == ["custom"]
    finally:
        logger.handlers.clear()
