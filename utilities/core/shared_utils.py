"""Shared utilities for scanner communication and control.

This module provides diagnostic helpers that are used across adapters. The
``ScannerCommand`` class now lives in :mod:`utilities.core.command_library`.
Serial communication helpers can be found in
``utilities.core.serial_utils``.
"""

import logging
import os
import sys

from utilities.core.command_library import ScannerCommand


def ensure_root_in_path():
    """Add the project root directory to ``sys.path`` if missing."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)


# Call this function when the module is imported
ensure_root_in_path()


def diagnose_connection_issues():
    """Diagnose common connection problems with the scanner."""
    import serial.tools.list_ports

    print("\nDiagnosing connection issues...")
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports detected. Ensure the scanner is connected.")
        return

    print("Available serial ports:")
    for port in ports:
        print(f"  - {port.device}: {port.description}")

    print("\nSuggestions:")
    print("  1. Verify the scanner is powered on.")
    print("  2. Check that the correct port is selected.")
    print("  3. Ensure no other application is using the port.")
    print("  4. Try reconnecting the scanner or using a different USB port.")


def read_response(ser, timeout=1.0):
    """Read a response from the serial port with a temporary timeout."""

    original_timeout = ser.timeout
    try:
        ser.timeout = timeout
        response = ser.read_until(b"\r").decode("utf-8").strip()
        logging.debug(f"Shared utils received response: {response}")
        return response
    except Exception as e:  # pragma: no cover - error path
        logging.error(f"Error reading response: {e}")
        return ""
    finally:
        ser.timeout = original_timeout


__all__ = [
    "ScannerCommand",
    "ensure_root_in_path",
    "diagnose_connection_issues",
    "read_response",
]

