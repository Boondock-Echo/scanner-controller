"""Tests for the centralized ``read_response`` function."""
from unittest.mock import MagicMock

from scanner_controller.utilities.core.serial_utils import read_response


def test_read_response_restores_timeout():
    """Ensure read_response restores the original timeout."""
    ser = MagicMock()
    ser.timeout = 5
    ser.read_until.return_value = b"RES\r"

    read_response(ser, timeout=0.1)
    assert ser.timeout == 5
