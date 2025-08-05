"""Tests for core serial utilities."""

from unittest.mock import MagicMock

from scanner_controller.utilities.core.serial_utils import (
    clear_serial_buffer,
    read_response,
    send_command,
    wait_for_data,
)


def test_clear_serial_buffer_uses_read():
    class Dummy:
        def __init__(self):
            self.in_waiting = 5
            self.called = False

        def read(self, n):
            self.called = True
            self.in_waiting = 0

    ser = Dummy()
    clear_serial_buffer(ser)
    assert ser.called


def test_send_command_writes_and_reads():
    ser = MagicMock()
    ser.timeout = 1
    ser.in_waiting = 0
    ser.reset_input_buffer = MagicMock()
    ser.read_until.return_value = b"OK\r"
    response = send_command(ser, "CMD")
    assert response == "OK"
    ser.write.assert_called_once_with(b"CMD\r")


def test_wait_for_data_true_when_bytes_available():
    ser = MagicMock()
    ser.in_waiting = 1
    assert wait_for_data(ser, max_wait=0.01)


def test_read_response_restores_timeout():
    ser = MagicMock()
    ser.timeout = 2
    ser.read_until.return_value = b"RES\r"
    read_response(ser, timeout=0.1)
    assert ser.timeout == 2
