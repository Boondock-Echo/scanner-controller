"""Compatibility layer for serial utility functions."""

from utilities.core.serial_utils import (
    clear_serial_buffer,
    read_response,
    send_command,
    wait_for_data,
)

__all__ = [
    "clear_serial_buffer",
    "read_response",
    "send_command",
    "wait_for_data",
]

