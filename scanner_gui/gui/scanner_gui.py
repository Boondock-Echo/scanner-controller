"""
scannerGui.py.

This module defines the ScannerGUI class, which provides a graphical user
interface for controlling and interacting with a scanner device.
"""

import logging
import os
import time

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

# Import our controller instead of direct scanner interface
from scanner_gui.controller import ScannerController
from scanner_gui.scannerUtils import findAllScannerPorts

# Import GUI components
from .audio_controls import buildAudioControls
from .control_keys import buildControlKeys
from .display_group import buildDisplayGroup
from .keypad import buildKeypad
from .rotary_knob import buildRotaryKnob
from .signal_meters import buildSignalMeters

BAUDRATE = 115200


class ScannerGUI(QWidget):
    """
    ScannerGUI class.

    Graphical user interface for controlling and interacting with a scanner.
    """

    def __init__(self):
        """Initialize the ScannerGUI instance."""
        super().__init__()
        self.setWindowTitle("Scanner Faceplate GUI")
        self.loadStyleSheet(
            os.path.join(os.path.dirname(__file__), "style.qss")
        )

        self.font_main = QFont("Courier", 16)
        self.font_lcd = QFont("Courier", 18, QFont.Weight.Bold)

        # Use our controller instead of direct serial connection
        self.controller = ScannerController(baudrate=BAUDRATE)
        self.scanner_ports = []
        self.childWindows = []
        self.displayLabels = []
        self.connected_port = None

        self.initUI()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refreshScannerList)
        self.refresh_timer.start(10000)

        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.updateDisplay)
        self.display_timer.start(250)

        self.refreshScannerList(initial=True)

    def loadStyleSheet(self, path: str):
        """
        Load and apply a stylesheet to the GUI.

        This method reads a stylesheet file from the given path and applies
        it to the GUI. If the file cannot be loaded, a warning is printed.

        Args:
            path (str): The file path to the stylesheet.
        """
        try:
            with open(path, "r") as f:
                self.setStyleSheet(f.read())
        except Exception as e:
            print(f"Warning: Could not load stylesheet: {e}")

    def initUI(self):
        """
        Initialize the user interface components of the ScannerGUI.

        This method sets up the layout, widgets, and controls for the GUI,
        including the port selector, display, signal meters, and keypad.
        """
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
        layout.addWidget(
            self.modelLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )

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
        """
        Refresh the list of available scanner ports.

        This method updates the scanner port list by finding all available
        scanner ports and populating the port selector dropdown. If this is
        the initial call and only one port is found, it automatically connects
        to that port.

        Args:
            initial (bool): Whether this is the initial call to refresh the
                            scanner list.
        """
        ports = findAllScannerPorts()
        if ports != self.scanner_ports:
            self.scanner_ports = ports
            self.portSelector.clear()
            for port, model in ports:
                self.portSelector.addItem(f"{model} ({port})", (port, model))
            if initial and len(ports) == 1:
                self.connectScanner(*ports[0])

    def connectScanner(self, port, model):
        """
        Scanner connection method.

        Connect to the scanner device on the specified port.
        """
        try:
            if self.connected_port:
                self.controller.disconnect()

            # Give the OS time to release the port
            time.sleep(0.5)

            # Connect to the new port using our controller
            if self.controller.connect(port=port, model=model):
                self.connected_port = port
                self.modelLabel.setText(f"Model: {model}")
                logging.info(f"Successfully connected to {model} on {port}")
            else:
                raise Exception("Failed to connect to scanner")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Connection Error",
                f"Could not connect to {model} on {port}:\n{e}",
            )

    def manualConnect(self):
        """Manually connect to the selected scanner port."""
        index = self.portSelector.currentIndex()
        data = self.portSelector.itemData(index)
        if data:
            port, model = data
            self.connectScanner(port, model)

    def onPortSelected(self, index):
        """
        Handle the event when a port is selected from the dropdown.

        This method creates a new ScannerGUI window, connects it to the
        selected port and model, and displays the new window.

        Args:
            index (int): The index of the selected item in the port selector.
        """
        data = self.portSelector.itemData(index)
        if data:
            port, model = data
            new_window = ScannerGUI()
            new_window.connectScanner(port, model)
            new_window.show()
            self.childWindows.append(new_window)

    def updateDisplay(self):
        """Update the scanner display and signal meters."""
        if not self.controller.adapter:
            return

        try:
            raw = self.controller.read_status()
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
            rssi = self.controller.read_rssi()
            self.rssiBar.setValue(int(rssi * 100))
        except Exception:
            self.rssiBar.setValue(0)

        try:
            value = self.sqlSlider.value()
            self.squelchBar.setValue(value)
        except Exception:
            self.squelchBar.setValue(0)

    def knobScrolled(self, event):
        """
        Handle the knob scroll event.

        This method determines the direction of the scroll based on the angle
        delta of the event and sends the corresponding key command to the
        scanner.

        Args:
            event: The scroll event containing the angle delta.
        """
        angle = event.angleDelta().y()
        if angle > 0:
            self.sendKey("<")
        elif angle < 0:
            self.sendKey(">")

    def knobPressed(self, event):
        """
        Handle the knob press event.

        This method sends the corresponding key command to the scanner
        when the knob is pressed.

        Args:
            event: The press event triggering the knob action.
        """
        self.sendKey("^")

    def sendKey(self, key):
        """Send a key command to the scanner."""
        self.controller.send_key(key)

    def setVolume(self):
        """Set the volume level on the scanner."""
        value = self.volSlider.value() / 100.0
        self.controller.set_volume(value)

    def setSquelch(self):
        """Set the squelch level on the scanner."""
        value = self.sqlSlider.value() / 100.0
        self.controller.set_squelch(value)

    def parseStsLine(self, sts_line: str) -> dict:
        """
        Parse an STS line from the scanner.

        This method processes a status (STS) line received from the scanner,
        extracting information such as screen data, key flags, backlight status,
        and volume level.

        Args:
            sts_line (str): The status line string to parse.

        Returns:
            dict: A dictionary containing parsed data, including screen text,
                  key flags, backlight status, and volume level.
        """
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
