# audioControls.py

"""
Audiocontrols module.

This module provides functionality related to audiocontrols.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout


def buildAudioControls(volSlider, sqlSlider) -> QGroupBox:
    """
    Build and return a QGroupBox containing volume and squelch sliders.

    Args:
        volSlider: A QSlider for controlling volume.
        sqlSlider: A QSlider for controlling squelch.

    Returns:
        QGroupBox: A group box containing the sliders.
    """
    volLayout = QVBoxLayout()
    volLabel = QLabel("Vol")
    volLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    volSlider.setRange(0, 100)
    volSlider.setValue(50)
    volLayout.addWidget(volLabel)
    volLayout.addWidget(volSlider)

    sqlLayout = QVBoxLayout()
    sqlLabel = QLabel("SQL")
    sqlLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
    sqlSlider.setRange(0, 100)
    sqlSlider.setValue(30)
    sqlLayout.addWidget(sqlLabel)
    sqlLayout.addWidget(sqlSlider)

    slidersLayout = QHBoxLayout()
    slidersLayout.addLayout(volLayout)
    slidersLayout.addLayout(sqlLayout)

    audioGroup = QGroupBox("Audio")
    audioGroup.setLayout(slidersLayout)

    return audioGroup
