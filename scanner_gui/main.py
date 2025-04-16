"""
This is the main entry point for the scanner GUI application.

It initializes the PyQt application and launches the ScannerGUI interface.
"""

# Standard library imports
import os
import sys

from PyQt6.QtWidgets import QApplication, QMessageBox


def main():
    """Execute the Scanner GUI application.

    Clears Python cache, initializes the GUI, checks for port accessibility,
    and runs the main application loop.
    """
    # Import here after cache clearing
    try:
        # Application imports
        from scanner_gui.gui.scannerGui import ScannerGUI
    except ImportError:
        # If package import fails, try relative import (when run as script)
        try:
            from .gui.scannerGui import ScannerGUI
        except ImportError:
            # Last resort - direct import (when run directly)
            sys.path.insert(
                0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            )
            # Application imports
            from scanner_gui.gui.scannerGui import ScannerGUI

    # Start the application
    """
    Run the scanner GUI application.

    The main function initializes the PyQt application and launches the
    ScannerGUI interface.
    """
    app = QApplication(sys.argv)

    # Show warning if COM ports are inaccessible
    # Third-party imports
    from serial.tools import list_ports

    busy_ports = []
    for port in list_ports.comports():
        try:
            # Third-party imports
            from serial import Serial

            # Use context manager without assigning to an unused variable
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


# This allows the script to be run directly

if __name__ == "__main__":
    main()
