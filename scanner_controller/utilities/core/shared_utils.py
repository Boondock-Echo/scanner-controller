"""Shared utilities for scanner communication and control.

This module provides diagnostic helpers that are used across adapters. The
``ScannerCommand`` class now lives in :mod:`utilities.core.command_library`.
Serial communication helpers can be found in
``utilities.core.serial_utils``.
"""

import os
import sys
import glob

from scanner_controller.utilities.core.command_library import ScannerCommand
from scanner_controller.utilities.core.serial_utils import read_response


def ensure_root_in_path():
    """Add the project root directory to ``sys.path`` if missing."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)


def diagnose_connection_issues():
    """Diagnose common connection problems with the scanner."""
    import serial.tools.list_ports

    print("\nDiagnosing connection issues...")
    ports = list(serial.tools.list_ports.comports())
    hid_paths = glob.glob("/dev/usb/hiddev*")
    soapy_devices = []
    rtl_devices = []
    try:
        from SoapySDR import Device as SoapyDevice

        soapy_devices = SoapyDevice.enumerate()
    except Exception:
        pass
    try:
        from rtlsdr import RtlSdr

        rtl_devices = RtlSdr.get_devices()
    except Exception:
        pass
    if not ports and not hid_paths and not soapy_devices and not rtl_devices:
        print(
            "No serial, HID, or SDR devices detected. Ensure the scanner is connected."
        )
        return

    if ports:
        print("Available serial ports:")
        for port in ports:
            print(f"  - {port.device}: {port.description}")
    else:
        print("No serial ports detected.")

    if hid_paths:
        print("Available HID devices (may require additional setup or drivers):")
        for path in hid_paths:
            print(f"  - {path}")
        print("See README section 'Enabling HID Devices' for more details.")

    if soapy_devices or rtl_devices:
        print("Available SDR pseudo-ports:")
        for dev in soapy_devices:
            label = dev.get("label") if isinstance(dev, dict) else str(dev)
            print(f"  - SoapySDR: {label}")
        for dev in rtl_devices:
            print(f"  - RTL-SDR: {dev}")
    else:
        print("No SDR devices detected.")

    print("\nSuggestions:")
    print("  1. Verify the scanner is powered on.")
    print("  2. Check that the correct port is selected.")
    print("  3. Ensure no other application is using the port.")
    print("  4. Try reconnecting the scanner or using a different USB port.")
    print("  5. If using a HID device, install any required drivers or enable permissions.")


__all__ = [
    "ScannerCommand",
    "ensure_root_in_path",
    "diagnose_connection_issues",
    "read_response",
]
