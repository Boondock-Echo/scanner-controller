# signalMeters.py

"""
Signal Meters Module.

This module provides a function to build signal meter widgets
using PyQt6, including RSSI and squelch progress bars.
"""

from PyQt6.QtWidgets import QGroupBox, QProgressBar, QVBoxLayout


def buildSignalMeters(
    rssiBar: QProgressBar, squelchBar: QProgressBar
) -> QGroupBox:
    """
    Build a signal meter group box containing RSSI and squelch progress bars.

    Args:
        rssiBar (QProgressBar): The progress bar for RSSI
            (Received Signal Strength Indicator).
        squelchBar (QProgressBar): The progress bar for squelch level.

    Returns:
        QGroupBox: A group box containing the signal meter widgets.
    """
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
