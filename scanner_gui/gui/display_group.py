"""
Create a scanner GUI using PyQt6.

This module provides a function to build the display group
for the scanner GUI.
"""

# displayGroup.py

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QGroupBox, QLabel, QVBoxLayout


def buildDisplayGroup(font_lcd, displayLabels: list) -> QGroupBox:
    """
    Build a display group for the scanner GUI.

    Args:
        font_lcd: The font to be used for the display labels.
        displayLabels (list): A list to store the QLabel objects.

    Returns:
        QGroupBox: A group box containing the display labels.
    """
    displayGroupLayout = QVBoxLayout()

    for _ in range(6):
        lbl = QLabel("".ljust(16))
        lbl.setFont(font_lcd)
        lbl.setObjectName("DisplayLine")
        lbl.setProperty("highlight", False)
        lbl.setProperty("underline", False)
        displayLabels.append(lbl)
        # Remove duplicate widget addition - each label was being added twice
        displayGroupLayout.addWidget(
            lbl, alignment=Qt.AlignmentFlag.AlignCenter
        )

    displayGroup = QGroupBox("Display")
    displayGroup.setLayout(displayGroupLayout)
    return displayGroup
