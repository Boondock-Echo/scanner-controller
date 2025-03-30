# scannerGUI.py

import sys
import time
import os

# Ensure the 'gui' directory is in the Python module search path
sys.path.append(os.path.join(os.path.dirname(__file__), 'gui'))

import serial
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QHBoxLayout, QSlider, QProgressBar, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

from commandLibrary import getScannerInterface
from scannerUtils import findAllScannerPorts

from gui import (
    buildAudioControls,
    buildDisplayGroup,
    buildSignalMeters,
    buildControlKeys,
    buildKeypad,
    buildRotaryKnob
)



BAUDRATE = 115200

def loadStyleSheet(self, path: str):
    try:
        with open(path, "r") as f:
            self.setStyleSheet(f.read())
    except Exception as e:
        print(f"Warning: Could not load stylesheet: {e}")


class ScannerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scanner Faceplate GUI")
       
        self.loadStyleSheet("style.qss")
       
        self.font_main = QFont("Courier", 16)
        self.font_lcd = QFont("Courier", 18, QFont.Weight.Bold)

        self.ser = None
        self.adapter = None
        self.scanner_ports = []
        self.childWindows = []
        self.displayLabels = []

        self.initUI()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refreshScannerList)
        self.refresh_timer.start(30000)

        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.updateDisplay)
        self.display_timer.start(5000)

        self.refreshScannerList(initial=True)

    def initUI(self):
        outerLayout = QHBoxLayout()

        # Audio Controls
        self.volSlider = QSlider(Qt.Orientation.Vertical)
        self.volSlider.sliderReleased.connect(self.setVolume)
