import sys
import time
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QGridLayout, QHBoxLayout, QSlider, QProgressBar, QFrame, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
import serial
from commandLibrary import getScannerInterface
from scannerUtils import findAllScannerPorts

BAUDRATE = 115200

class ScannerGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Scanner Faceplate GUI")
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: white; }
            QGroupBox { border: 1px solid #666; margin-top: 10px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 3px 0 3px; }
            QPushButton {
                background-color: #444;
                border: 1px solid #888;
                border-radius: 5px;
                padding: 6px;
            }
            QPushButton:hover { background-color: #666; }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                text-align: center;
            }
            QProgressBar::chunk { background-color: limegreen; }
        """)
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
        self.refresh_timer.start(30000)  # 30 seconds

        self.display_timer = QTimer()
        self.display_timer.timeout.connect(self.updateDisplay)
        self.display_timer.start(500)  # 0.5 seconds

        self.refreshScannerList(initial=True)

    def initUI(self):
        outerLayout = QHBoxLayout()

        # Left-side sliders in a group box
        leftSliders = QVBoxLayout()
        volLabel = QLabel("Vol")
        volLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volSlider = QSlider(Qt.Orientation.Vertical)
        self.volSlider.setRange(0, 100)
        self.volSlider.setValue(50)
        self.volSlider.sliderReleased.connect(self.setVolume)
        leftSliders.addWidget(volLabel)
        leftSliders.addWidget(self.volSlider)

        sqlLabel = QLabel("SQL")
        sqlLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sqlSlider = QSlider(Qt.Orientation.Vertical)
        self.sqlSlider.setRange(0, 100)
        self.sqlSlider.setValue(30)
        self.sqlSlider.sliderReleased.connect(self.setSquelch)
        leftSliders.addWidget(sqlLabel)
        leftSliders.addWidget(self.sqlSlider)

        from PyQt6.QtWidgets import QGroupBox
        audioGroup = QGroupBox("Audio")
        audioGroup.setLayout(leftSliders)
        outerLayout.addWidget(audioGroup)

        layout = QVBoxLayout()
        portLayout = QHBoxLayout()
        self.portSelector = QComboBox()
        portLayout.addWidget(self.portSelector)
        self.connectButton = QPushButton("Connect")
        self.connectButton.clicked.connect(self.manualConnect)
        portLayout.addWidget(self.connectButton)
        layout.addLayout(portLayout)

        self.modelLabel = QLabel("Model: ---")
        self.modelLabel.setFont(self.font_main)
        layout.addWidget(self.modelLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        self.displayLabels = []
        displayGroupLayout = QVBoxLayout()
        for _ in range(6):
            lbl = QLabel("".ljust(16))
            lbl.setFont(self.font_lcd)
            lbl.setStyleSheet("background-color: #333; padding: 2px; border-radius: 5px;")
            self.displayLabels.append(lbl)
            displayGroupLayout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)
        displayGroup = QGroupBox("Display")
        displayGroup.setLayout(displayGroupLayout)
        layout.addWidget(displayGroup)

        self.rssiBar = QProgressBar()
        self.rssiBar.setRange(0, 100)
        self.rssiBar.setTextVisible(True)
        self.rssiBar.setFormat("RSSI: %p%")

        self.squelchBar = QProgressBar()
        self.squelchBar.setRange(0, 100)
        self.squelchBar.setTextVisible(True)
        self.squelchBar.setFormat("SQL: %p%")

        signalGroupLayout = QVBoxLayout()
        signalGroupLayout.addWidget(self.rssiBar)
        signalGroupLayout.addWidget(self.squelchBar)
        signalGroup = QGroupBox("Signal Meters")
        signalGroup.setLayout(signalGroupLayout)
        layout.addWidget(signalGroup)

        sideButtonLayout = QHBoxLayout()
        for label in ["Hold", "Scan", "L/O", "Menu", "Func"]:
            btn = QPushButton(label)
            btn.setFixedSize(80, 40)
            btn.clicked.connect(lambda _, k=label: self.sendKey(k[0]))
            sideButtonLayout.addWidget(btn)
        buttonGroup = QGroupBox("Control Keys")
        buttonGroup.setLayout(sideButtonLayout)
        layout.addWidget(buttonGroup)

        grid = QGridLayout()
        keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "0", "E"]
        for i, key in enumerate(keys):
            btn = QPushButton(key)
            btn.setFixedSize(60, 60)
            btn.clicked.connect(lambda _, k=key: self.sendKey(k))
            grid.addWidget(btn, i // 3, i % 3)
        gridGroup = QGroupBox("Keypad")
        gridGroup.setLayout(grid)
        layout.addWidget(gridGroup)

        outerLayout.addLayout(layout)

        knobLayout = QVBoxLayout()
        knobLabel = QLabel("↻")
        knobLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        knobLabel.setFont(QFont("Courier", 28))
        knobLabel.setStyleSheet("background-color: #444; color: white; padding: 20px; border-radius: 40px;")
        knobLabel.setFixedSize(100, 100)
        knobLabel.mousePressEvent = self.knobPressed
        knobLabel.wheelEvent = self.knobScrolled
        knobLayout.addWidget(knobLabel, alignment=Qt.AlignmentFlag.AlignTop)
        knobGroup = QGroupBox("Rotary Knob")
        knobGroup.setLayout(knobLayout)
        outerLayout.addWidget(knobGroup)

        self.setLayout(outerLayout)

    def refreshScannerList(self, initial=False):
        ports = findAllScannerPorts()
        if ports != self.scanner_ports:
            self.scanner_ports = ports
            self.portSelector.clear()
            for port, model in ports:
                self.portSelector.addItem(f"{model} ({port})", (port, model))
            if initial and len(ports) == 1:
                self.connectScanner(*ports[0])

    def connectScanner(self, port, model):
        try:
            if self.ser:
                self.ser.close()
            self.ser = serial.Serial(port, BAUDRATE, timeout=1)
            time.sleep(0.1)
            self.adapter = getScannerInterface(model)
            self.modelLabel.setText(f"Model: {model}")
        except Exception as e:
            QMessageBox.critical(self, "Connection Error", f"Could not connect to {model} on {port}:\n{e}")

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
                # Skip the last two lines in MENU mode if they are empty or numeric noise
                is_menu = "M E N U" in parsed["screen"][0]["text"].upper()
                if is_menu and i >= 4 and not line["text"].strip().isalpha():
                    self.displayLabels[i].setText("")
                    self.displayLabels[i].setStyleSheet("background-color: #222;")
                    continue
                text = line["text"].ljust(16)
                style = "background-color: #333; color: white; padding: 2px;"
                if line["underline"]:
                    style += " text-decoration: underline;"
                if line["highlight"]:
                    style += " background-color: white; color: black;"
                self.displayLabels[i].setText(text)
                self.displayLabels[i].setStyleSheet(style)
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

    # End of knob events

    def sendKey(self, key):
        if self.adapter and self.ser:
            self.adapter.sendKey(self.ser, key)

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

        # Handle trailing commas and empty fields more robustly
        parts = [p.strip() for p in sts_line.strip().split(",")]
        while len(parts) < 23:
            parts.append("")  # pad with empty fields if needed

        status_bits = parts[1]
        screen = []
        for i in range(2, 14, 2):
            text = parts[i] if i < len(parts) else ""
            modifier = parts[i + 1] if i + 1 < len(parts) else ""
            screen.append({
                "text": text.strip(),
                "underline": modifier == "_" * 16,
                "highlight": modifier == "*" * 16
            })

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
            "volume": volume
        }

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScannerGUI()
    gui.show()
    sys.exit(app.exec())
