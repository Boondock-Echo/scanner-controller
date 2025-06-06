"""
Scanner GUI Module.

This module defines the ScannerGUI class, which provides a graphical user
interface for controlling and interacting with a scanner device.
"""

import logging
import os
import time

from PyQt6.QtCore import Qt, QTimer

from .background_worker import BackgroundWorker
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
from utilities.scanner.backend import find_all_scanner_ports

# Import GUI components
from .audio_controls import build_audio_controls
from .control_keys import build_control_keys
from .display_group import build_display_group
from .keypad import build_keypad
from .rotary_knob import build_rotary_knob
from .signal_meters import build_signal_meters

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
        self.load_stylesheet(
            os.path.join(os.path.dirname(__file__), "style.qss")
        )

        self.font_main = QFont("Courier", FONT_SIZE_MAIN)
        self.font_lcd = QFont("Courier", FONT_SIZE_LCD, QFont.Weight.Bold)

        # Use our controller instead of direct serial connection
        self.controller = ScannerController(baudrate=BAUDRATE)
        self.scanner_ports = []
        self.child_windows = []
        self.display_labels = []
        self.connected_port = None

        self.init_ui()

        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_scanner_list)
        self.refresh_timer.start(REFRESH_INTERVAL)

        self.worker = BackgroundWorker(self.controller, DISPLAY_REFRESH)
        self.worker.status_received.connect(self.on_status_received)
        self.worker.rssi_received.connect(self.on_rssi_received)
        self.worker.start()

        self.refresh_scanner_list(initial=True)

    def load_stylesheet(self, path: str):
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

    def init_ui(self):
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
        outer_layout = QHBoxLayout()
        outer_layout.setContentsMargins(5, 5, 5, 5)
        outer_layout.setSpacing(5)

        # Left Panel: Knob above sliders
        self.vol_slider = QSlider(Qt.Orientation.Vertical)
        # Set proper range for volume slider
        self.vol_slider.setMinimum(0)
        self.vol_slider.setMaximum(100)
        self.vol_slider.setValue(50)  # Default to 50%
        self.vol_slider.valueChanged.connect(
            self.on_volume_changed
        )  # Add real-time updates
        self.vol_slider.sliderReleased.connect(self.set_volume)

        self.sql_slider = QSlider(Qt.Orientation.Vertical)
        # Set proper range for squelch slider
        self.sql_slider.setMinimum(0)
        self.sql_slider.setMaximum(100)
        self.sql_slider.setValue(20)  # Default to 20%
        self.sql_slider.valueChanged.connect(
            self.on_squelch_changed
        )  # Add real-time updates
        self.sql_slider.sliderReleased.connect(self.set_squelch)

        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(2, 2, 2, 2)
        left_panel.setSpacing(10)  # Reduced from 20
        left_panel.addWidget(
            build_rotary_knob(
                knob_pressed_callback=lambda: self.send_key("^"),
                rotate_left_callback=lambda: self.send_key("<"),
                rotate_right_callback=lambda: self.send_key(">"),
            )
        )
        left_panel.addWidget(build_audio_controls(self.vol_slider, self.sql_slider))
        left_panel.setAlignment(Qt.AlignmentFlag.AlignTop)
        outer_layout.addLayout(left_panel)

        # Right Panel: Everything else
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)  # Reduced spacing

        # Port selector
        port_layout = QVBoxLayout()
        port_layout.setContentsMargins(2, 2, 2, 2)
        port_layout.setSpacing(2)

        self.connect_button = QPushButton("Connect")
        self.connect_button.clicked.connect(self.manual_connect)
        port_layout.addWidget(self.connect_button)

        self.port_selector = QComboBox()
        self.port_selector.setMaximumHeight(25)  # Restrict height
        port_layout.addWidget(self.port_selector)

        port_group = QGroupBox("Scanner Port")
        port_group.setLayout(port_layout)
        layout.addWidget(port_group)

        self.model_label = QLabel("Model: ---")
        self.model_label.setFont(self.font_main)
        self.model_label.setMaximumHeight(20)  # Restrict height
        layout.addWidget(
            self.model_label, alignment=Qt.AlignmentFlag.AlignCenter
        )

        # Display
        self.display_labels = []
        layout.addWidget(build_display_group(self.font_lcd, self.display_labels))

        # Signal Meters
        self.rssi_bar = QProgressBar()
        self.rssi_bar.setMaximumHeight(15)  # Restrict height
        self.squelch_bar = QProgressBar()
        self.squelch_bar.setMaximumHeight(15)  # Restrict height

        # Store the signal meter group for access to the squelch bar
        self.signal_meters_group = build_signal_meters(
            self.rssi_bar, self.squelch_bar
        )
        layout.addWidget(self.signal_meters_group)

        # Debug logging to verify the squelch bar is properly set
        logging.debug(f"Squelch bar initialized: {self.squelch_bar}")

        # Keypad + Vertical Buttons
        keypad_row = QHBoxLayout()
        keypad_row.setContentsMargins(0, 0, 0, 0)
        keypad_row.setSpacing(5)
        keypad_row.addWidget(build_control_keys(self.send_key))  # On the left
        keypad_row.addWidget(build_keypad(self.send_key))  # On the right
        layout.addLayout(keypad_row)

        outer_layout.addLayout(layout)
        self.setLayout(outer_layout)

        # Set a smaller fixed size for the window
        self.adjustSize()
        self.setMinimumSize(int(self.width() * 0.8), int(self.height() * 0.85))

    def refresh_scanner_list(self, initial=False):
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
            self.port_selector.clear()
            for port, model in ports:
                self.port_selector.addItem(f"{model} ({port})", (port, model))
            if initial and len(ports) == 1:
                self.connect_scanner(*ports[0])

    def connect_scanner(self, port, model):
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
                self.model_label.setText(f"Model: {model}")
                logging.info(f"Successfully connected to {model} on {port}")

                # Read current volume and squelch levels from scanner
                self.read_and_apply_scanner_levels()
            else:
                raise Exception("Failed to connect to scanner")

        except Exception as e:
            QMessageBox.critical(
                self,
                "Connection Error",
                f"Could not connect to {model} on {port}:\n{e}",
            )

    def read_and_apply_scanner_levels(self):
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
            self.vol_slider.setValue(vol_percent)

            # Read and apply squelch
            current_sql = self.controller.read_squelch()
            sql_percent = int(current_sql * 100)
            logging.info(f"Scanner squelch level: {sql_percent}%")
            self.sql_slider.setValue(sql_percent)

            self.squelch_bar.setValue(sql_percent)

            # Feedback to user
            self.model_label.setText(
                f"Model: {self.controller.model} (Vol: {vol_percent}%, "
                f"SQL: {sql_percent}%)"
            )
            # Reset label after a few seconds
            QTimer.singleShot(
                5000,
                lambda: self.model_label.setText(
                    f"Model: {self.controller.model}"
                ),
            )

        except Exception as e:
            logging.error(f"Error reading scanner levels: {e}")

    def manual_connect(self):
        """Manually connect to the selected scanner port."""
        index = self.port_selector.currentIndex()
        data = self.port_selector.itemData(index)
        if data:
            port, model = data
            self.connect_scanner(port, model)

    def on_port_selected(self, index):
        """
        Handle the event when a port is selected from the dropdown.

        This method creates a new ScannerGUI window, connects it to the
        selected port and model, and displays the new window.

        Args:
            index (int): The index of the selected item in the port selector.
        """
        data = self.port_selector.itemData(index)
        if data:
            port, model = data
            new_window = ScannerGUI()
            new_window.connect_scanner(port, model)
            new_window.show()
            self.child_windows.append(new_window)

    def on_status_received(self, raw: str):
        """Update the scanner display with data from the worker."""
        if not raw:
            return

        try:
            parsed = self.parse_sts_line(raw)

            for i, line in enumerate(parsed["screen"]):
                if self._should_hide_line(i, line, parsed):
                    self.display_labels[i].setVisible(False)
                    continue
                self.display_labels[i].setVisible(True)
                text = line["text"].ljust(DISPLAY_WIDTH)
                label = self.display_labels[i]
                label.setText(text)
                label.setProperty("highlight", line["highlight"])
                label.setProperty("underline", line["underline"])
                label.style().unpolish(label)
                label.style().polish(label)
        except Exception:
            for lbl in self.display_labels:
                lbl.setText("Freq: Error")

        self._update_meters()

    def _should_hide_line(self, index, line, parsed_data):
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

    def _update_meters(self):
        """Update the squelch meter."""
        try:
            value = self.sql_slider.value()
            if hasattr(self, "squelch_bar"):
                self.squelch_bar.setValue(value)
        except Exception as e:  # pragma: no cover - log only
            logging.error(f"Error updating squelch meter: {e}")
            if hasattr(self, "squelch_bar"):
                self.squelch_bar.setValue(0)

    def on_rssi_received(self, rssi: float) -> None:
        """Update the RSSI meter from the worker signal."""
        try:
            if hasattr(self, "rssi_bar"):
                self.rssi_bar.setValue(int(rssi * 100))
        except Exception as e:  # pragma: no cover - log only
            logging.error(f"Error updating RSSI meter: {e}")
            if hasattr(self, "rssi_bar"):
                self.rssi_bar.setValue(0)

    def on_volume_changed(self):
        """Update the UI when volume slider changes value."""
        # This updates the UI without sending commands to scanner
        # Good for immediate feedback while dragging
        value = self.vol_slider.value()
        # Could update a volume display here if we had one
        logging.debug(f"Volume slider changed to {value}%")

    def on_squelch_changed(self):
        """Update the UI when squelch slider changes value."""
        # Update the squelch bar in real-time while slider moves
        value = self.sql_slider.value()

        # Check if squelchBar exists and log for debugging
        if hasattr(self, 'squelch_bar'):
            self.squelch_bar.setValue(value)
            logging.debug(f"Squelch slider changed to {value}%")
        else:
            logging.error("squelchBar not found - wasn't properly initialized")
            # Try to recover - this is a fallback if buildSignalMeters creates
            # new bars
            try:
                # Find the squelch bar in the signal meters group
                for child in self.signal_meters_group.findChildren(QProgressBar):
                    if child.objectName() == "squelchBar":
                        child.setValue(value)
                        # Save reference for future use
                        self.squelch_bar = child
                        logging.info("Recovered squelchBar reference")
                        break
            except Exception as e:
                logging.error(f"Cannot recover squelchBar: {e}")

    def set_volume(self):
        """Set the volume level on the scanner."""
        if not self.controller.adapter:
            logging.warning("Cannot set volume: No scanner connected")
            return

        value = self.vol_slider.value() / 100.0
        logging.info(
            f"Setting volume to {value:.2f} ({self.vol_slider.value()}%)"
        )
        success = self.controller.set_volume(value)
        if not success:
            logging.error(f"Failed to set volume to {value:.2f}")
            self.model_label.setText(f"{self.model_label.text()} - Vol Error")
            # Reset label after a few seconds
            QTimer.singleShot(
                3000,
                lambda: self.model_label.setText(
                    f"Model: {self.controller.model}"
                ),
            )

    def set_squelch(self):
        """Set the squelch level on the scanner."""
        if not self.controller.adapter:
            logging.warning("Cannot set squelch: No scanner connected")
            return

        value = self.sql_slider.value() / 100.0
        logging.info(
            f"Setting squelch to {value:.2f} ({self.sql_slider.value()}%)"
        )
        success = self.controller.set_squelch(value)
        if not success:
            logging.error(f"Failed to set squelch to {value:.2f}")
            self.model_label.setText(f"{self.model_label.text()} - SQL Error")
            # Reset label after a few seconds
            QTimer.singleShot(
                3000,
                lambda: self.model_label.setText(
                    f"Model: {self.controller.model}"
                ),
            )

    def knob_scrolled(self, event):
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
            self.send_key("<")
        elif angle < 0:
            self.send_key(">")

    def knob_pressed(self, event):
        """
        Handle the knob press event.

        This method sends the corresponding key command to the scanner
        when the knob is pressed.

        Args:
            event: The press event triggering the knob action.
        """
        self.send_key("^")

    def send_key(self, key):
        """Send a key command to the scanner."""
        self.controller.send_key(key)

    def parse_sts_line(self, sts_line: str) -> dict:
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

    def closeEvent(self, event):
        """Stop worker thread on window close."""
        if hasattr(self, "worker"):
            self.worker.stop()
            self.worker.wait()
        super().closeEvent(event)
