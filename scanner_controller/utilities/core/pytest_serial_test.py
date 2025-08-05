"""Pytest tests for serial communication functionality."""

from unittest.mock import MagicMock, patch

import pytest

# Import the module but not the function
from scanner_controller.utilities.core import serial_test


@pytest.fixture
def mock_serial():
    """Create a mock serial connection for testing."""
    mock = MagicMock()

    # Configure the mock for common commands
    responses = {
        b"MDL\r": b"MDL,BC125AT\r",
        b"VER\r": b"VER,1.00.06\r",
        b"STS\r": b"STS,200,0,0,0,0\r",
        b"KEY,1\r": b"KEY,1\r",
    }

    def mock_read(size=1):
        """Mock the serial read function.

        Returns data based on the last command sent.
        """
        return responses.get(mock.last_command, b"ERR\r")

    def mock_write(data):
        """Mock the serial write function.

        Stores the command and returns the number of bytes written.
        """
        mock.last_command = data
        return len(data)

    mock.read = mock_read
    mock.write = mock_write
    mock.reset_input_buffer = MagicMock()
    mock.reset_output_buffer = MagicMock()
    mock.in_waiting = 20

    return mock


def test_scanner_detection(mock_serial):
    """Test the scanner detection functionality."""
    with patch("serial.Serial", return_value=mock_serial):
        with patch(
            "serial.tools.list_ports.comports",
            return_value=[
                type(
                    "obj",
                    (object,),
                    {"device": "COM1", "description": "Test Port"},
                )()
            ],
        ):
            port = serial_test.scan_for_scanners()
            assert port == "COM1"


def test_command_sending(mock_serial):
    """Test sending commands to the scanner."""
    with patch("serial.Serial", return_value=mock_serial):
        response = serial_test.send_command("COM1", "MDL")
        assert "BC125AT" in response

        response = serial_test.send_command("COM1", "VER")
        assert "1.00.06" in response
