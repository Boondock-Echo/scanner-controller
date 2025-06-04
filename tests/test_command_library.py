"""Tests for :class:`utilities.command_library.scanner_command`."""

import os
import sys

import pytest

# Ensure the project root is on the Python path so `utilities` can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utilities.command_library import scanner_command  # noqa: E402
from utilities.errors import CommandError  # noqa: E402


def test_parse_response_ok():
    """Return the response unchanged when no error is present."""
    cmd = scanner_command("TEST")
    assert cmd.parse_response("OK") == "OK"


def test_parse_response_error():
    """Raise an exception when the response begins with ``ERR``."""
    cmd = scanner_command("TEST")
    with pytest.raises(CommandError):  # Use the imported CommandError
        cmd.parse_response("ERR")


def test_parse_response_err_substring():
    """Treat responses containing ``ERR`` as valid if not prefixed by it."""
    cmd = scanner_command("TEST")
    assert cmd.parse_response("CARRIER") == "CARRIER"


def test_build_command_query():
    """Return query string when no value is provided."""
    cmd = scanner_command("FREQ")
    assert cmd.build_command() == "FREQ\r"


def test_build_command_set_valid():
    """Build set command when value is in range."""
    cmd = scanner_command("VOL", valid_range=(0, 10))
    assert cmd.build_command(5) == "VOL,5\r"


def test_build_command_set_invalid():
    """Raise ``ValueError`` when value is outside the allowed range."""
    cmd = scanner_command("SQUELCH", valid_range=(0, 100))
    with pytest.raises(ValueError):
        cmd.build_command(150)
