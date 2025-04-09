"""
Pytest configuration and shared fixtures
"""

import os
import sys
from unittest.mock import MagicMock

import pytest

# Add project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_serial_port():
    """Mock serial port for testing without hardware"""
    mock_serial = MagicMock()

    # Configure the mock to return valid responses
    def mock_read(size=1):
        """Mock read method that returns realistic responses for known commands"""
        command = getattr(mock_serial, "last_command", None)

        responses = {
            b"MDL\r": b"MDL,BC125AT\r",
            b"VER\r": b"VER,1.00.06\r",
            b"STS\r": b"STS,200,0,0,0,0\r",
            b"KEY,1\r": b"KEY,1\r",
        }

        return responses.get(command, b"ERR\r")

    def mock_write(data):
        """Save the last command written to the serial port"""
        mock_serial.last_command = data
        return len(data)

    mock_serial.read = mock_read
    mock_serial.write = mock_write
    mock_serial.reset_input_buffer = MagicMock()
    mock_serial.reset_output_buffer = MagicMock()
    mock_serial.in_waiting = 20

    return mock_serial


@pytest.fixture
def adapter_helpers():
    """Helper functions for adapter testing"""

    class Helpers:
        @staticmethod
        def create_mock_adapter(adapter_class):
            """Create a mock adapter with essential methods for testing"""
            mock_adapter = MagicMock(spec=adapter_class)

            # Add common methods/properties
            mock_adapter.machineMode = "MOCK_SCANNER"
            mock_adapter.send_command.return_value = "MDL,MOCK_SCANNER"
            mock_adapter.readFrequency.return_value = "154.3250"

            return mock_adapter

    return Helpers()
