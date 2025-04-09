# scannerGui.py

import logging
import os
import sys
import time

import serial
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ..commandLibrary import getScannerInterface
from ..scanner_utils import find_all_scanner_ports
from .audioControls import buildAudioControls
from .controlKeys import buildControlKeys
from .displayGroup import buildDisplayGroup
from .keypad import buildKeypad
from .rotaryKnob import buildRotaryKnob
from .signalMeters import buildSignalMeters

BAUDRATE = 115200


class ScannerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scanner Faceplate GUI")
        self.loadStyleSheet(os.path.join(os.path.dirname(__file__), "style.qss"))

        self.font_main = QFont("Courier", 16)
        self.font_lcd = QFont("Courier", 18, QFont.Weight.Bold)

        self.ser = None
        self.adapter = None
        self.scanner_ports = []
        self.childWindows = []
        self.displayLabels = []
        self.connected_port = None  # Track which port we're connected to

        self.initUI()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refreshScannerList)
        self.refresh_timer.start(10000)  # Change to 10 seconds as requested

        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.updateDisplay)
        self.display_timer.start(250)

        self.refreshScannerList(initial=True)

    def loadStyleSheet(self, path: str):
        try:
            with open(path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Warning: Could not load stylesheet: {e}")

    def initUI(self):
        outerLayout = QHBoxLayout()

        # Left Panel: Knob above sliders
        self.volSlider = QSlider(Qt.Orientation.Vertical)
        self.volSlider.sliderReleased.connect(self.setVolume)
        self.sqlSlider = QSlider(Qt.Orientation.Vertical)
        self.sqlSlider.sliderReleased.connect(self.setSquelch)

        leftPanel = QVBoxLayout()
        leftPanel.addWidget(
            buildRotaryKnob(
                knobPressedCallback=lambda: self.sendKey("^"),
                rotateLeftCallback=lambda: self.sendKey("<"),
                rotateRightCallback=lambda: self.sendKey(">"),
            )
        )
        leftPanel.addWidget(buildAudioControls(self.volSlider, self.sqlSlider))
        leftPanel.setAlignment(Qt.AlignmentFlag.AlignTop)
        leftPanel.setSpacing(20)
        outerLayout.addLayout(leftPanel)

        # Right Panel: Everything else
        layout = QVBoxLayout()

        # Port selector
        # Port selector: Connect button above dropdown, inside a QGroupBox
        portLayout = QVBoxLayout()

        self.connectButton = QPushButton("Connect")
        self.connectButton.clicked.connect(self.manualConnect)
        portLayout.addWidget(self.connectButton)

        self.portSelector = QComboBox()
        portLayout.addWidget(self.portSelector)

        portGroup = QGroupBox("Scanner Port")
        portGroup.setLayout(portLayout)
        layout.addWidget(portGroup)

        self.modelLabel = QLabel("Model: ---")
        self.modelLabel.setFont(self.font_main)
        layout.addWidget(self.modelLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        # Display
        self.displayLabels = []
        layout.addWidget(buildDisplayGroup(self.font_lcd, self.displayLabels))

        # Signal Meters
        self.rssiBar = QProgressBar()
        self.squelchBar = QProgressBar()
        layout.addWidget(buildSignalMeters(self.rssiBar, self.squelchBar))

        # Keypad + Vertical Buttons
        keypadRow = QHBoxLayout()
        keypadRow.addWidget(buildControlKeys(self.sendKey))  # On the left
        keypadRow.addWidget(buildKeypad(self.sendKey))  # On the right
        layout.addLayout(keypadRow)

        outerLayout.addLayout(layout)
        self.setLayout(outerLayout)

    def refreshScannerList(self, initial=False):
        # Skip checking ports that we're already connected to
        if self.connected_port and self.ser and self.ser.is_open:
            logging.debug(
                f"Skipping scan of port {self.connected_port} (already connected)"
            )
            return

        ports = find_all_scanner_ports()
        if ports != self.scanner_ports:
            self.scanner_ports = ports
            self.portSelector.clear()
            for port, model in ports:
                self.portSelector.addItem(f"{model} ({port})", (port, model))
            if initial and len(ports) == 1:
                self.connectScanner(*ports[0])

    def connectScanner(self, port, model):
        try:
            # If we're already connected to this port, don't reconnect
            if self.connected_port == port and self.ser and self.ser.is_open:
                logging.info(f"Already connected to {model} on {port}")
                return

            # Close any existing connection
            if self.ser:
                try:
                    self.ser.close()
                    logging.debug(f"Closed existing connection")
                except Exception as e:
                    logging.warning(f"Error closing existing connection: {e}")

            # Give the OS time to release the port
            time.sleep(0.5)

            # Connect to the new port
            self.ser = serial.Serial(port, BAUDRATE, timeout=1, exclusive=True)
            time.sleep(0.2)  # Allow the scanner to wake up

            # Store the port we're connected to
            self.connected_port = port

            # Set up the interface
            self.adapter = getScannerInterface(model)
            self.modelLabel.setText(f"Model: {model}")

            logging.info(f"Successfully connected to {model} on {port}")
        except Exception as e:
            logging.error(f"Error connecting to {model} on {port}: {e}")
            QMessageBox.critical(
                self,
                "Connection Error",
                f"Could not connect to {model} on {port}:\n{e}",
            )
            self.connected_port = None
            self.ser = None
            self.adapter = None

    def manualConnect(self):
        index = self.portSelector.currentIndex()
        data = self.portSelector.itemData(index)
        if data:
            port, model = data
            self.connectScanner(port, model)

    def onPortSelected(self, index):
        data = self.portSelector.itemData(index)
        if data:
            port, model = data
            new_window = ScannerGUI()
            new_window.connectScanner(port, model)
            new_window.show()
            self.childWindows.append(new_window)

    def updateDisplay(self):
        if not self.adapter or not self.ser:
            return
        try:
            raw = self.adapter.readStatus(self.ser)
            parsed = self.parseStsLine(raw)
            for i, line in enumerate(parsed["screen"]):
                is_menu = "M E N U" in parsed["screen"][0]["text"].upper()
                if is_menu and i >= 4 and not line["text"].strip().isalpha():
                    self.displayLabels[i].setVisible(False)
                    continue
                if i == 0 and not line["text"].strip().isalpha():
                    self.displayLabels[i].setVisible(False)
                    continue
                self.displayLabels[i].setVisible(True)
                text = line["text"].ljust(16)
                label = self.displayLabels[i]
                label.setText(text)
                label.setProperty("highlight", line["highlight"])
                label.setProperty("underline", line["underline"])
                label.style().unpolish(label)
                label.style().polish(label)
        except Exception:
            for lbl in self.displayLabels:
                lbl.setText("Freq: Error")

        try:
            rssi = self.adapter.readRSSI(self.ser)
            self.rssiBar.setValue(int(rssi * 100))
        except Exception:
            self.rssiBar.setValue(0)

        try:
            value = self.sqlSlider.value()
            self.squelchBar.setValue(value)
        except Exception:
            self.squelchBar.setValue(0)

    def knobScrolled(self, event):
        angle = event.angleDelta().y()
        if angle > 0:
            self.sendKey("<")
        elif angle < 0:
            self.sendKey(">")

    def knobPressed(self, event):
        self.sendKey("^")

    def sendKey(self, key):
        """Send a key press to the scanner"""
        if not self.adapter or not self.ser:
            logging.warning(f"Cannot send key '{key}': not connected to a scanner")
            return

        if not self.ser.is_open:
            logging.warning(f"Cannot send key '{key}': serial port is closed")
            try:
                # Try to reopen the port
                self.ser.open()
                logging.info(f"Reopened connection to {self.connected_port}")
            except Exception as e:
                logging.error(f"Failed to reopen serial port: {e}")
                return

        try:
            logging.info(f"Sending key: '{key}'")
            # Use the adapter's sendKey method which now includes the ',P' suffix
            response = self.adapter.sendKey(self.ser, key)
            logging.info(f"Response: {response}")
        except Exception as e:
            logging.error(f"Error sending key '{key}': {e}")
            import traceback

            logging.error(traceback.format_exc())

    def setVolume(self):
        if self.adapter and self.ser:
            value = self.volSlider.value() / 100.0
            self.adapter.writeVolume(self.ser, value)

    def setSquelch(self):
        if self.adapter and self.ser:
            value = self.sqlSlider.value() / 100.0
            self.adapter.writeSquelch(self.ser, value)

    def parseStsLine(self, sts_line: str) -> dict:
        if not sts_line.startswith("STS,"):
            raise ValueError("Not an STS line")
        parts = [p.strip() for p in sts_line.strip().split(",")]
        while len(parts) < 23:
            parts.append("")
        status_bits = parts[1]
        screen = []
        for i in range(2, 14, 2):
            text = parts[i] if i < len(parts) else ""
            modifier = parts[i + 1] if i + 1 < len(parts) else ""
            screen.append(
                {
                    "text": text.strip(),
                    "underline": modifier == "_" * 16,
                    "highlight": modifier == "*" * 16,
                }
            )
        key_flags = parts[14:21]
        keys = [flag == "1" for flag in key_flags]
        backlight = parts[21] if len(parts) > 21 else ""
        try:
            volume = int(parts[22]) if len(parts) > 22 else 0
        except ValueError:
            volume = 0
        return {
            "status_bits": status_bits,
            "screen": screen,
            "keys": keys,
            "backlight": backlight,
            "volume": volume,
        }
