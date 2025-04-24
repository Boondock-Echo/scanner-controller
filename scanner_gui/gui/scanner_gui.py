"""
scanner_gui

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

# Updated import from scanner_utils instead of scannerUtils
from scanner_gui.scanner_utils import find_all_scanner_ports

# Import GUI components
from .audio_controls import buildAudioControls
from .control_keys import buildControlKeys
from .display_group import buildDisplayGroup
from .keypad import buildKeypad
from .rotary_knob import buildRotaryKnob
from .signal_meters import buildSignalMeters

# Constants
BAUDRATE = 115200
REFRESH_INTERVAL = 10000  # 10 seconds
DISPLAY_REFRESH = 250  # 250ms
FONT_SIZE_MAIN = 12  # Reduced from 16
FONT_SIZE_LCD = 14  # Reduced from 18
DISPLAY_WIDTH = 16  # Character width for display


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

        self.font_main = QFont("Courier", FONT_SIZE_MAIN)
        self.font_lcd = QFont("Courier", FONT_SIZE_LCD, QFont.Weight.Bold)

        # Use our controller instead of direct serial connection
        self.controller = ScannerController(baudrate=BAUDRATE)
        self.scanner_ports = []
        self.childWindows = []
        self.displayLabels = []
        self.connected_port = None

        self.initUI()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refreshScannerList)
        self.refresh_timer.start(REFRESH_INTERVAL)

        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.updateDisplay)
        self.display_timer.start(DISPLAY_REFRESH)

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
        # Set application-wide styles for compactness
        self.setStyleSheet(
            self.styleSheet()
            + """
            QGroupBox { margin-top: 6px; padding-top: 10px; }
            QPushButton { min-height: 20px; padding: 2px; }
            QLabel { margin: 0px; }
        """
        )

        # Create outer layout with minimal margins
        outerLayout = QHBoxLayout()
        outerLayout.setContentsMargins(5, 5, 5, 5)
        outerLayout.setSpacing(5)

        # Left Panel: Knob above sliders
        self.volSlider = QSlider(Qt.Orientation.Vertical)
        # Set proper range for volume slider
        self.volSlider.setMinimum(0)
        self.volSlider.setMaximum(100)
        self.volSlider.setValue(50)  # Default to 50%
        self.volSlider.valueChanged.connect(
            self.onVolumeChanged
        )  # Add real-time updates
        self.volSlider.sliderReleased.connect(self.setVolume)

        self.sqlSlider = QSlider(Qt.Orientation.Vertical)
        # Set proper range for squelch slider
        self.sqlSlider.setMinimum(0)
        self.sqlSlider.setMaximum(100)
        self.sqlSlider.setValue(20)  # Default to 20%
        self.sqlSlider.valueChanged.connect(
            self.onSquelchChanged
        )  # Add real-time updates
        self.sqlSlider.sliderReleased.connect(self.setSquelch)

        leftPanel = QVBoxLayout()
        leftPanel.setContentsMargins(2, 2, 2, 2)
        leftPanel.setSpacing(10)  # Reduced from 20
        leftPanel.addWidget(
            buildRotaryKnob(
                knobPressedCallback=lambda: self.sendKey("^"),
                rotateLeftCallback=lambda: self.sendKey("<"),
                rotateRightCallback=lambda: self.sendKey(">"),
            )
        )
        leftPanel.addWidget(buildAudioControls(self.volSlider, self.sqlSlider))
        leftPanel.setAlignment(Qt.AlignmentFlag.AlignTop)
        outerLayout.addLayout(leftPanel)

        # Right Panel: Everything else
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)  # Reduced spacing

        # Port selector
        portLayout = QVBoxLayout()
        portLayout.setContentsMargins(2, 2, 2, 2)
        portLayout.setSpacing(2)

        self.connectButton = QPushButton("Connect")
        self.connectButton.clicked.connect(self.manualConnect)
        portLayout.addWidget(self.connectButton)

        self.portSelector = QComboBox()
        self.portSelector.setMaximumHeight(25)  # Restrict height
        portLayout.addWidget(self.portSelector)

        portGroup = QGroupBox("Scanner Port")
        portGroup.setLayout(portLayout)
        layout.addWidget(portGroup)

        self.modelLabel = QLabel("Model: ---")
        self.modelLabel.setFont(self.font_main)
        self.modelLabel.setMaximumHeight(20)  # Restrict height
        layout.addWidget(
            self.modelLabel, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Display
        self.displayLabels = []
        layout.addWidget(buildDisplayGroup(self.font_lcd, self.displayLabels))

        # Signal Meters
        self.rssiBar = QProgressBar()
        self.rssiBar.setMaximumHeight(15)  # Restrict height
        self.squelchBar = QProgressBar()
        self.squelchBar.setMaximumHeight(15)  # Restrict height

        # Store the signal meter group for access to the squelch bar
        self.signalMetersGroup = buildSignalMeters(
            self.rssiBar, self.squelchBar
        )
        layout.addWidget(self.signalMetersGroup)

        # Debug logging to verify the squelch bar is properly set
        logging.debug(f"Squelch bar initialized: {self.squelchBar}")

        # Keypad + Vertical Buttons
        keypadRow = QHBoxLayout()
        keypadRow.setContentsMargins(0, 0, 0, 0)
        keypadRow.setSpacing(5)
        keypadRow.addWidget(buildControlKeys(self.sendKey))  # On the left
        keypadRow.addWidget(buildKeypad(self.sendKey))  # On the right
        layout.addLayout(keypadRow)

        outerLayout.addLayout(layout)
        self.setLayout(outerLayout)

        # Set a smaller fixed size for the window
        self.adjustSize()
        self.setMinimumSize(int(self.width() * 0.8), int(self.height() * 0.85))

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
        ports = find_all_scanner_ports()  # Updated function call
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

                # Read current volume and squelch levels from scanner
                self.readAndApplyScannerLevels()
            else:
                raise Exception("Failed to connect to scanner")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Connection Error",
                f"Could not connect to {model} on {port}:\n{e}",
            )

    def readAndApplyScannerLevels(self):
        """
        Read current volume and squelch level from scanner and apply to GUI.

        This method retrieves the current volume and squelch levels from the
        connected scanner and updates the corresponding UI elements. It also
        logs the values for debugging purposes.
        """
        if not self.controller.adapter:
            logging.warning("Cannot read scanner levels: No adapter")
            return

        try:
            # Read and apply volume
            current_vol = self.controller.read_volume()
            vol_percent = int(current_vol * 100)
            logging.info(f"Scanner volume level: {vol_percent}%")
            self.volSlider.setValue(vol_percent)

            # Read and apply squelch
            current_sql = self.controller.read_squelch()
            sql_percent = int(current_sql * 100)
            logging.info(f"Scanner squelch level: {sql_percent}%")
            self.sqlSlider.setValue(sql_percent)

            self.squelchBar.setValue(sql_percent)

            # Feedback to user
            self.modelLabel.setText(
                f"Model: {self.controller.model} (Vol: {vol_percent}%, "
                f"SQL: {sql_percent}%)"
            )
            # Reset label after a few seconds
            QTimer.singleShot(
                5000,
                lambda: self.modelLabel.setText(
                    f"Model: {self.controller.model}"
                ),
            )

        except Exception as e:
            logging.error(f"Error reading scanner levels: {e}")

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
                if self._shouldHideLine(i, line, parsed):
                    self.displayLabels[i].setVisible(False)
                    continue

                self.displayLabels[i].setVisible(True)
                text = line["text"].ljust(DISPLAY_WIDTH)
                label = self.displayLabels[i]
                label.setText(text)
                label.setProperty("highlight", line["highlight"])
                label.setProperty("underline", line["underline"])
                label.style().unpolish(label)
                label.style().polish(label)
        except Exception:
            for lbl in self.displayLabels:
                lbl.setText("Freq: Error")

        self._updateMeters()

    def _shouldHideLine(self, index, line, parsed_data):
        """Determine if a display line should be hidden."""
        is_menu = "M E N U" in parsed_data["screen"][0]["text"].upper()
        # Never hide the line containing the menu text
        is_menu_line = "M E N U" in line["text"].upper()
        if is_menu_line:
            return False

        text_not_alpha = not line["text"].strip().isalpha()

        # Hide empty lines in menu mode (index >= 4)
        if is_menu and index >= 4 and text_not_alpha:
            return True
        # Hide empty title line
        if index == 0 and text_not_alpha:
            return True
        return False

    def _updateMeters(self):
        """Update the RSSI and squelch meters."""
        try:
            rssi = self.controller.read_rssi()
            if hasattr(self, 'rssiBar'):
                self.rssiBar.setValue(int(rssi * 100))
        except Exception as e:
            logging.error(f"Error updating RSSI meter: {e}")
            if hasattr(self, 'rssiBar'):
                self.rssiBar.setValue(0)

        try:
            # Get the current slider value for squelch display
            value = self.sqlSlider.value()
            if hasattr(self, 'squelchBar'):
                self.squelchBar.setValue(value)
        except Exception as e:
            logging.error(f"Error updating squelch meter: {e}")
            if hasattr(self, 'squelchBar'):
                self.squelchBar.setValue(0)

    def onVolumeChanged(self):
        """Update the UI when volume slider changes value."""
        # This updates the UI without sending commands to scanner
        # Good for immediate feedback while dragging
        value = self.volSlider.value()
        # Could update a volume display here if we had one
        logging.debug(f"Volume slider changed to {value}%")

    def onSquelchChanged(self):
        """Update the UI when squelch slider changes value."""
        # Update the squelch bar in real-time while slider moves
        value = self.sqlSlider.value()

        # Check if squelchBar exists and log for debugging
        if hasattr(self, 'squelchBar'):
            self.squelchBar.setValue(value)
            logging.debug(f"Squelch slider changed to {value}%")
        else:
            logging.error("squelchBar not found - wasn't properly initialized")
            # Try to recover - this is a fallback if buildSignalMeters creates
            # new bars
            try:
                # Find the squelch bar in the signal meters group
                for child in self.signalMetersGroup.findChildren(QProgressBar):
                    if child.objectName() == "squelchBar":
                        child.setValue(value)
                        # Save reference for future use
                        self.squelchBar = child
                        logging.info("Recovered squelchBar reference")
                        break
            except Exception as e:
                logging.error(f"Cannot recover squelchBar: {e}")

    def setVolume(self):
        """Set the volume level on the scanner."""
        if not self.controller.adapter:
            logging.warning("Cannot set volume: No scanner connected")
            return

        value = self.volSlider.value() / 100.0
        logging.info(
            f"Setting volume to {value:.2f} ({self.volSlider.value()}%)"
        )
        success = self.controller.set_volume(value)
        if not success:
            logging.error(f"Failed to set volume to {value:.2f}")
            self.modelLabel.setText(f"{self.modelLabel.text()} - Vol Error")
            # Reset label after a few seconds
            QTimer.singleShot(
                3000,
                lambda: self.modelLabel.setText(
                    f"Model: {self.controller.model}"
                ),
            )

    def setSquelch(self):
        """Set the squelch level on the scanner."""
        if not self.controller.adapter:
            logging.warning("Cannot set squelch: No scanner connected")
            return

        value = self.sqlSlider.value() / 100.0
        logging.info(
            f"Setting squelch to {value:.2f} ({self.sqlSlider.value()}%)"
        )
        success = self.controller.set_squelch(value)
        if not success:
            logging.error(f"Failed to set squelch to {value:.2f}")
            self.modelLabel.setText(f"{self.modelLabel.text()} - SQL Error")
            # Reset label after a few seconds
            QTimer.singleShot(
                3000,
                lambda: self.modelLabel.setText(
                    f"Model: {self.controller.model}"
                ),
            )

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
