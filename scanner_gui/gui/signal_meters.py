# signalMeters.py

"""
Signal meter widget module.

This module provides functions to build signal meter widgets for displaying
RSSI and squelch levels.
"""

import logging

from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout


def build_signal_meters(rssi_bar, squelch_bar):
    """
    Build signal meter group containing RSSI and squelch bars.

    Args:
        rssi_bar (QProgressBar): Progress bar for RSSI display
        squelch_bar (QProgressBar): Progress bar for squelch display

    Returns:
        QGroupBox: Group box containing the signal meters
    """
    layout = QVBoxLayout()
    layout.setContentsMargins(2, 2, 2, 2)
    layout.setSpacing(2)

    # Configure RSSI bar
    rssi_bar.setObjectName("rssiBar")
    rssi_bar.setMinimum(0)
    rssi_bar.setMaximum(100)
    rssi_layout = QHBoxLayout()
    rssi_layout.setContentsMargins(0, 0, 0, 0)
    rssi_layout.addWidget(QLabel("RSSI"))
    rssi_layout.addWidget(rssi_bar)
    layout.addLayout(rssi_layout)

    # Configure squelch bar
    squelch_bar.setObjectName("squelchBar")
    squelch_bar.setMinimum(0)
    squelch_bar.setMaximum(100)
    squelch_layout = QHBoxLayout()
    squelch_layout.setContentsMargins(0, 0, 0, 0)
    squelch_layout.addWidget(QLabel("SQL"))
    squelch_layout.addWidget(squelch_bar)
    layout.addLayout(squelch_layout)

    # Log for debugging
    logging.debug(
        f"Signal meters built with existing bars: {rssi_bar}, {squelch_bar}"
    )

    meters = QGroupBox("Signal")
    meters.setLayout(layout)
    return meters
