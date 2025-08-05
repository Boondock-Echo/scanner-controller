"""
Utilities Package.

This package provides various utility functions and classes for the scanner
controller application. It centralizes common functionality used across
different modules.
"""

# Core functionality - import in exact order specified by the error message
from scanner_controller.utilities.core.command_library import (
    get_scanner_interface,
    read_frequency,
    read_model,
    read_rssi,
    read_smeter,
    read_squelch,
    read_swver,
    read_volume,
    ScannerCommand,
    write_frequency,
    write_squelch,
    write_volume,
)
from scanner_controller.utilities.core.command_registry import build_command_table
from scanner_controller.utilities.core.serial_utils import (
    clear_serial_buffer,
    read_response,
    send_command,
    wait_for_data,
)
from scanner_controller.utilities.io.readline_setup import initialize_readline
from scanner_controller.utilities.log_utils import configure_logging, get_logger
from scanner_controller.utilities.graph_utils import render_rssi_graph

try:
    from scanner_controller.utilities.scanner.close_call_logger import record_close_calls
except Exception:  # pragma: no cover - optional import for tests
    record_close_calls = None

try:
    from scanner_controller.utilities.scanner.close_call_search import close_call_search
except Exception:  # pragma: no cover - optional import for tests
    close_call_search = None

# Only export specific names (instead of using __all__ = ['*'])
__all__ = [
    "configure_logging",
    "get_logger",
    "initialize_readline",
    "ScannerCommand",
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
    "render_rssi_graph",
    "record_close_calls",
    "close_call_search",
]
