"""
This module provides the audio controls for the scanner GUI.

It includes a function to build a PyQt6 QGroupBox containing volume and squelch
sliders.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout


def buildAudioControls(volSlider, sqlSlider) -> QGroupBox:
    """
    Build a QGroupBox containing volume and squelch sliders.

    Args:
        volSlider: A QSlider for controlling the volume.
        sqlSlider: A QSlider for controlling the squelch.

    Returns:
        QGroupBox: A group box containing the sliders.
    """
    volLayout = QVBoxLayout()
    volLabel = QLabel("VOL")
    volLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Don't set ranges or values here - they're already set in scanner_gui.py
    # and will be updated with actual scanner values after connection
    volLayout.addWidget(volLabel)
    volLayout.addWidget(volSlider)

    sqlLayout = QVBoxLayout()
    sqlLabel = QLabel("SQL")
    sqlLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Don't set ranges or values here - they're already set in scanner_gui.py
    # and will be updated with actual scanner values after connection
    sqlLayout.addWidget(sqlLabel)
    sqlLayout.addWidget(sqlSlider)

    slidersLayout = QHBoxLayout()
    slidersLayout.addLayout(volLayout)
    slidersLayout.addLayout(sqlLayout)

    audioGroup = QGroupBox("Audio")
    audioGroup.setLayout(slidersLayout)
    return audioGroup
