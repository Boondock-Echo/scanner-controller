# signalMeters.py

from PyQt6.QtWidgets import QGroupBox, QProgressBar, QVBoxLayout


def buildSignalMeters(rssiBar: QProgressBar, squelchBar: QProgressBar) -> QGroupBox:
    rssiBar.setRange(0, 100)
    rssiBar.setTextVisible(True)
    rssiBar.setFormat("RSSI: %p%")

    squelchBar.setRange(0, 100)
    squelchBar.setTextVisible(True)
    squelchBar.setFormat("SQL: %p%")

    signalGroupLayout = QVBoxLayout()
    signalGroupLayout.addWidget(rssiBar)
    signalGroupLayout.addWidget(squelchBar)

    signalGroup = QGroupBox("Signal Meters")
    signalGroup.setLayout(signalGroupLayout)
    return signalGroup
