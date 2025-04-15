"""
This is the main entry point for the scanner GUI application.

It initializes the PyQt application and launches the ScannerGUI interface.
"""

# main.py

import sys

from PyQt6.QtWidgets import QApplication

from scanner_gui.gui.scannerGui import ScannerGUI


def main():
    """
    Run the scanner GUI application.

    The main function initializes the PyQt application and launches the
    ScannerGUI interface.
    """
    app = QApplication(sys.argv)
    gui = ScannerGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
