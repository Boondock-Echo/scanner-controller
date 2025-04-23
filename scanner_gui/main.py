"""
Main module for the scanner GUI application.

This module provides the entry point for the scanner GUI application and
re-exports the ScannerGUI class.
"""

import sys

from PyQt6.QtWidgets import QApplication, QMessageBox
from serial.tools import list_ports


def main():
    """
    Execute the Scanner GUI application.

    Initializes the GUI, checks for port accessibility,
    and runs the main application loop.
    """
    # Create QApplication BEFORE importing any widget classes
    app = QApplication(sys.argv)

    # Import ScannerGUI here, after QApplication is created
    from scanner_gui.gui.scanner_gui import ScannerGUI

    # Show warning if COM ports are inaccessible
    busy_ports = []
    for port in list_ports.comports():
        try:
            from serial import Serial

            with Serial(port.device, timeout=0.1):
                pass  # Port could be opened successfully
        except Exception as e:
            busy_ports.append((port.device, str(e)))

    if busy_ports:
        warning_msg = "Some COM ports are inaccessible and can't be used:\n\n"
        for port, error in busy_ports:
            warning_msg += f"• {port}: {error}\n"
        warning_msg += (
            "\nThis might be caused by another application using the port."
        )

        QMessageBox.warning(None, "Port Access Warning", warning_msg)

    # Create and show the GUI
    gui = ScannerGUI()
    gui.show()

    # Run the application
    sys.exit(app.exec())


# This allows the module to be re-exported properly
def get_scanner_gui():
    """Return the ScannerGUI class after ensuring QApplication exists."""
    if not QApplication.instance():
        # Create a QApplication instance if one doesn't exist
        QApplication.instance() or QApplication(sys.argv)

    from scanner_gui.gui.scanner_gui import ScannerGUI

    return ScannerGUI


if __name__ == "__main__":
    main()
