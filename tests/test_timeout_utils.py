"""Tests for the timeout utility decorator in :mod:`utilities.io.timeout_utils`."""

import os
import sys
import time
import pytest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.io.timeout_utils import with_timeout, ScannerTimeoutError


def test_with_timeout_success():
    @with_timeout(1)
    def quick():
        return "done"

    assert quick() == "done"


def test_with_timeout_error():
    @with_timeout(0.1)
    def slow():
        time.sleep(0.2)
        return "late"

    with pytest.raises(ScannerTimeoutError):
        slow()


def test_with_timeout_default_value():
    @with_timeout(0.1, default_result="default")
    def slow():
        time.sleep(0.2)
        return "late"

    assert slow() == "default"
