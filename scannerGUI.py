import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QGridLayout, QHBoxLayout, QSlider, QProgressBar, QFrame, QComboBox
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
        self.setStyleSheet("background-color: #222; color: white;")
        self.font_main = QFont("Courier", 16)
        self.font_lcd = QFont("Courier", 18, QFont.Weight.Bold)

        self.ser = None
        self.adapter = None
        self.scanner_ports = findAllScannerPorts()

        self.initUI()
        if self.scanner_ports:
            self.connectScanner(self.scanner_ports[0][0], self.scanner_ports[0][1])
            self.updateDisplay()

            self.timer = QTimer()
            self.timer.timeout.connect(self.updateDisplay)
            self.timer.start(3000)

    def initUI(self):
        layout = QVBoxLayout()

        # Dropdown to select scanner
        self.portSelector = QComboBox()
        for port, model in self.scanner_ports:
            self.portSelector.addItem(f"{model} ({port})", (port, model))
        self.portSelector.currentIndexChanged.connect(self.onPortSelected)
        layout.addWidget(self.portSelector)

        # Header label
        self.modelLabel = QLabel("Model: ---")
        self.modelLabel.setFont(self.font_main)
        layout.addWidget(self.modelLabel, alignment=Qt.AlignmentFlag.AlignCenter)

        # LCD-style display
        self.display = QLabel("Freq: -----.--- MHz")
        self.display.setFont(self.font_lcd)
        self.display.setStyleSheet("background-color: #333; padding: 8px;")
        layout.addWidget(self.display, alignment=Qt.AlignmentFlag.AlignCenter)

        # RSSI bar
        self.rssiBar = QProgressBar()
        self.rssiBar.setRange(0, 100)
        self.rssiBar.setTextVisible(True)
        self.rssiBar.setFormat("RSSI: %p%")

        # Squelch bar
        self.squelchBar = QProgressBar()
        self.squelchBar.setRange(0, 100)
        self.squelchBar.setTextVisible(True)
        self.squelchBar.setFormat("SQL: %p%")

        barLayout = QVBoxLayout()
        barLayout.addWidget(self.rssiBar)
        barLayout.addWidget(self.squelchBar)
        layout.addLayout(barLayout)

        # Side buttons
        sideButtonLayout = QHBoxLayout()
        for label in ["Hold", "Scan", "L/O", "Menu", "Func"]:
            btn = QPushButton(label)
            btn.setFixedSize(80, 40)
            btn.clicked.connect(lambda _, k=label: self.sendKey(k[0]))
            sideButtonLayout.addWidget(btn)
        layout.addLayout(sideButtonLayout)

        # Sliders for Volume and Squelch in a compact layout
        sliderLayout = QHBoxLayout()

        volLayout = QVBoxLayout()
        volLabel = QLabel("Vol")
        volLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.volSlider = QSlider(Qt.Orientation.Vertical)
        self.volSlider.setFixedHeight(80)
        self.volSlider.setRange(0, 100)
        self.volSlider.setValue(50)
        self.volSlider.sliderReleased.connect(self.setVolume)
        volLayout.addWidget(volLabel)
        volLayout.addWidget(self.volSlider)
        sliderLayout.addLayout(volLayout)

        sqlLayout = QVBoxLayout()
        sqlLabel = QLabel("SQL")
        sqlLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sqlSlider = QSlider(Qt.Orientation.Vertical)
        self.sqlSlider.setFixedHeight(80)
        self.sqlSlider.setRange(0, 100)
        self.sqlSlider.setValue(30)
        self.sqlSlider.sliderReleased.connect(self.setSquelch)
        sqlLayout.addWidget(sqlLabel)
        sqlLayout.addWidget(self.sqlSlider)
        sliderLayout.addLayout(sqlLayout)

        layout.addLayout(sliderLayout)

        # Keypad grid
        grid = QGridLayout()
        keys = [
            "1", "2", "3",
            "4", "5", "6",
            "7", "8", "9",
            "<", "0", ">"
        ]

        for i, key in enumerate(keys):
            btn = QPushButton(key)
            btn.setFixedSize(60, 60)
            btn.clicked.connect(lambda _, k=key: self.sendKey(k))
            grid.addWidget(btn, i // 3, i % 3)

        layout.addLayout(grid)
        self.setLayout(layout)

    def connectScanner(self, port, model):
        if self.ser:
            self.ser.close()
        self.ser = serial.Serial(port, BAUDRATE, timeout=1)
        self.adapter = getScannerInterface(model)
        self.modelLabel.setText(f"Model: {model}")

    def onPortSelected(self, index):
        port, model = self.portSelector.itemData(index)
        self.connectScanner(port, model)
        self.updateDisplay()

    def updateDisplay(self):
        try:
            result = self.adapter.readFrequency(self.ser)
            self.display.setText(result.split("\t")[-1])
        except Exception:
            self.display.setText("Freq: Error")

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

    def sendKey(self, key):
        self.adapter.sendKey(self.ser, key)

    def setVolume(self):
        value = self.volSlider.value() / 100.0
        self.adapter.writeVolume(self.ser, value)

    def setSquelch(self):
        value = self.sqlSlider.value() / 100.0
        self.adapter.writeSquelch(self.ser, value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = ScannerGUI()
    gui.show()
    sys.exit(app.exec())
