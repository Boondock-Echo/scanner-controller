# signalMeters.py

"""
Signalmeters module.

This module provides functionality related to signalmeters.
"""

from PyQt6.QtWidgets import QGroupBox, QProgressBar, QVBoxLayout

"""
    buildSignalMeters function.

    Provides functionality for buildSignalMeters.
    """


def buildSignalMeters(
    rssiBar: QProgressBar, squelchBar: QProgressBar
) -> QGroupBox:
    """Build a group box containing signal meter progress bars.

    Creates a signal meters group with RSSI and squelch bars configured
    for display with percentages.

    Args:
        rssiBar: Progress bar for displaying RSSI values
        squelchBar: Progress bar for displaying squelch values

    Returns:
        QGroupBox containing the configured signal meters
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
