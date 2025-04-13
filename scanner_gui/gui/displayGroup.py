# displayGroup.py

"""
Displaygroup module.

This module provides functionality related to displaygroup.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QLabel, QVBoxLayout


def buildDisplayGroup(font_lcd, displayLabels: list) -> QGroupBox:
    """
    Build and return a display group.

    Args:
        font_lcd: The font to be used for the display labels.
        displayLabels (list): A list to store the QLabel objects.

    Returns:
        QGroupBox: The constructed display group.
    """
    displayGroupLayout = QVBoxLayout()

    for _ in range(6):
        lbl = QLabel("".ljust(16))
        lbl.setFont(font_lcd)
        lbl.setObjectName("DisplayLine")
        lbl.setProperty("highlight", False)
        lbl.setProperty("underline", False)
        displayLabels.append(lbl)
        displayGroupLayout.addWidget(
            lbl, alignment=Qt.AlignmentFlag.AlignCenter
        )

    displayGroup = QGroupBox("Display")
    displayGroup.setLayout(displayGroupLayout)
    return displayGroup


def update_frequency_display(self, frequency):
    """
    Update the frequency display in the GUI.

    Args:
        frequency (float or None): The frequency value to display.
        If None, an error message is shown.
    """
    if frequency is None:
        self.frequency_label.setText("Freq: Error")
    else:
        self.frequency_label.setText(f"Freq: {frequency:.3f} MHz")
