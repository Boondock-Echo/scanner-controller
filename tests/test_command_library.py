"""Tests for :class:`utilities.command_library.ScannerCommand`."""

import os
import sys

import pytest

# Ensure the project root is on the Python path so `utilities` can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.command_library import ScannerCommand  # noqa: E402
from utilities.errors import CommandError  # noqa: E402


def test_parse_response_ok():
    """Return the response unchanged when no error is present."""
    cmd = ScannerCommand("TEST")
    assert cmd.parse_response("OK") == "OK"


def test_parse_response_error():
    """Raise an exception when the response begins with ``ERR``."""
    cmd = ScannerCommand("TEST")
    with pytest.raises(CommandError):  # Use the imported CommandError
        cmd.parse_response("ERR")


def test_parse_response_err_substring():
    """Treat responses containing ``ERR`` as valid if not prefixed by it."""
    cmd = ScannerCommand("TEST")
    assert cmd.parse_response("CARRIER") == "CARRIER"
