# main.py

import sys

from PyQt6.QtWidgets import QApplication

from scanner_gui.gui.scannerGui import ScannerGUI


def main():
    app = QApplication(sys.argv)
    gui = ScannerGUI()
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
