# main.py

"""
Main module.

This module provides functionality related to main.
"""

# Standard library imports
import logging
import os
import shutil
import sys

# Third-party imports
from PyQt6.QtWidgets import QApplication, QMessageBox

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def clear_pycache():
    """Clear all __pycache__ directories to ensure fresh imports."""
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logging.info(f"Clearing cached Python files in {root_dir}")

    for dirpath, dirnames, _filenames in os.walk(root_dir):
        if "__pycache__" in dirnames:
            pycache_path = os.path.join(dirpath, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                logging.info(f"Removed cache directory: {pycache_path}")
            except Exception as e:
                logging.warning(f"Could not remove {pycache_path}: {e}")


def main():
    """Execute the Scanner GUI application.

    Clears Python cache, initializes the GUI, checks for port accessibility,
    and runs the main application loop.
    """
    # Clear cache on startup
    clear_pycache()

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
