"""Tests for :class:`utilities.core.command_library.ScannerCommand`."""

import os
import sys

import pytest

# Ensure the project root is on the Python path so `utilities` can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scanner_controller.utilities.core.command_library import ScannerCommand  # noqa: E402
from scanner_controller.utilities.errors import CommandError  # noqa: E402


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


def test_build_command_query():
    """Return query string when no value is provided."""
    cmd = ScannerCommand("FREQ")
    assert cmd.build_command() == "FREQ\r"


def test_build_command_set_valid():
    """Build set command when value is in range."""
    cmd = ScannerCommand("VOL", valid_range=(0, 10))
    assert cmd.build_command(5) == "VOL,5\r"


def test_build_command_set_invalid():
    """Raise ``ValueError`` when value is outside the allowed range."""
    cmd = ScannerCommand("SQUELCH", valid_range=(0, 100))
    with pytest.raises(ValueError):
        cmd.build_command(150)
