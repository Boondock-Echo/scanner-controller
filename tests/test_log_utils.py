"""Tests for basic functionality in :mod:`utilities.log_utils`."""

import logging
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from scanner_controller.utilities.log_utils import get_logger  # noqa: E402


def test_get_logger_custom_level():
    """Retrieve a logger with a specific level."""
    logger_name = "my_test_logger"
    logger = get_logger(logger_name, level="WARNING")
    assert logger.name == logger_name
    assert logger.level == logging.WARNING
