"""
This module provides the audio controls for the scanner GUI.

It includes a function to build a PyQt6 QGroupBox containing volume and squelch
sliders.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout


def build_audio_controls(vol_slider, sql_slider) -> QGroupBox:
    """
    Build a QGroupBox containing volume and squelch sliders.

    Args:
        volSlider: A QSlider for controlling the volume.
        sqlSlider: A QSlider for controlling the squelch.

    Returns:
        QGroupBox: A group box containing the sliders.
    """
    vol_layout = QVBoxLayout()
    vol_label = QLabel("VOL")
    vol_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Don't set ranges or values here - they're already set in scanner_gui.py
    # and will be updated with actual scanner values after connection
    vol_layout.addWidget(vol_label)
    vol_layout.addWidget(vol_slider)

    sql_layout = QVBoxLayout()
    sql_label = QLabel("SQL")
    sql_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

    # Don't set ranges or values here - they're already set in scanner_gui.py
    # and will be updated with actual scanner values after connection
    sql_layout.addWidget(sql_label)
    sql_layout.addWidget(sql_slider)

    sliders_layout = QHBoxLayout()
    sliders_layout.addLayout(vol_layout)
    sliders_layout.addLayout(sql_layout)

    audio_group = QGroupBox("Audio")
    audio_group.setLayout(sliders_layout)
    return audio_group
