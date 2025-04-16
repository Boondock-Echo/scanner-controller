"""
Create a scanner GUI using PyQt6.

This module provides a function to build the display group
for the scanner GUI.
It includes a function to update the frequency display.
It also includes a function to build signal meters using PyQt6.
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
        displayGroupLayout.addWidget(
            lbl, alignment=Qt.AlignmentFlag.AlignCenter
        )
        displayGroupLayout.addWidget(
            lbl, alignment=Qt.AlignmentFlag.AlignCenter
        )

    displayGroup = QGroupBox("Display")
    displayGroup.setLayout(displayGroupLayout)
    return displayGroup


def update_frequency_display(self, frequency):
    """
    Update the frequency display in the GUI.

    Updates the frequency display in the GUI.
    """
    if frequency is None:
        self.frequency_label.setText("Freq: Error")
    else:
        self.frequency_label.setText(f"Freq: {frequency:.3f} MHz")
