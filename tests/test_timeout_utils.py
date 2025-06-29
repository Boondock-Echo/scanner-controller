"""Tests for the timeout decorator in :mod:`utilities.io.timeout_utils`."""

import os
import sys
import time
import threading

import pytest

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from utilities.io.timeout_utils import (  # noqa: E402
    ScannerTimeoutError,
    with_timeout,
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


def test_with_timeout_propagates_exception():
    """Exceptions raised inside the wrapped function are re-raised."""

    class CustomError(Exception):
        pass

    @with_timeout(1)
    def bad():
        raise CustomError("boom")

    with pytest.raises(CustomError):
        bad()


def test_with_timeout_thread_cleanup():
    """Timed out calls should not leave background threads running."""

    @with_timeout(0.1)
    def never_ending(stop_event):
        while not stop_event.is_set():
            time.sleep(0.01)

    before = {t.name for t in threading.enumerate()}
    with pytest.raises(ScannerTimeoutError):
        never_ending()
    time.sleep(0.2)
    after = {t.name for t in threading.enumerate()}
    assert before == after
