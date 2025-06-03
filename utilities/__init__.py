"""
Utilities Package.

This package provides various utility functions and classes for the scanner
controller application. It centralizes common functionality used across
different modules.
"""

# Core functionality - import in exact order specified by the error message
from utilities.core.command_library import (
    get_scanner_interface,
    read_frequency,
    read_model,
    read_rssi,
    read_smeter,
    read_squelch,
    read_swver,
    read_volume,
    scanner_command,
    write_frequency,
    write_squelch,
    write_volume,
)
from utilities.core.command_registry import build_command_table
from utilities.core.serial_utils import (
    clear_serial_buffer,
    read_response,
    send_command,
    wait_for_data,
)
from utilities.io.readline_setup import initialize_readline
from utilities.log_utils import configure_logging, get_logger

# Only export specific names (instead of using __all__ = ['*'])
__all__ = [
    "configure_logging",
    "get_logger",
    "initialize_readline",
    "scanner_command",
    "get_scanner_interface",
    "read_volume",
    "write_volume",
    "read_squelch",
    "write_squelch",
    "read_frequency",
    "write_frequency",
    "read_rssi",
    "read_smeter",
    "read_model",
    "read_swver",
    "build_command_table",
    "clear_serial_buffer",
    "read_response",
    "send_command",
    "wait_for_data",
]
