"""Tests for the timeout decorator in :mod:`utilities.io.timeout_utils`."""

import time
import pytest
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utilities.io.timeout_utils import (  # noqa: E402
    with_timeout,
    ScannerTimeoutError,
)


def test_with_timeout_success():
    """Return the function result when it finishes in time."""
    @with_timeout(1)
    def quick():
        return "done"

    assert quick() == "done"


def test_with_timeout_error():
    """Raise :class:`ScannerTimeoutError` when the function times out."""
    @with_timeout(0.1)
    def slow():
        time.sleep(0.2)
        return "late"

    with pytest.raises(ScannerTimeoutError):
        slow()


def test_with_timeout_default_value():
    """Return the ``default_result`` value when a timeout occurs."""
    @with_timeout(0.1, default_result="default")
    def slow():
        time.sleep(0.2)
        return "late"

    assert slow() == "default"
