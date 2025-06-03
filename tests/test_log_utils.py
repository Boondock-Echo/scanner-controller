import logging
import os
import sys

# Ensure the project root is on the Python path so ``utilities`` can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.log_utils import get_logger


def test_get_logger_custom_level():
    logger_name = "my_test_logger"
    logger = get_logger(logger_name, level="WARNING")
    assert logger.name == logger_name
    assert logger.level == logging.WARNING
