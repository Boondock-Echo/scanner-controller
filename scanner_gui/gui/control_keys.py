"""
Control Keys Module.

This module provides a function to build a control keys group box
with buttons for a PyQt6 GUI application.
"""

# controlKeys.py

from typing import Callable

from PyQt6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout


def buildControlKeys(callback: Callable[[str], None]) -> QGroupBox:
    """
    Build a control keys group box with buttons.

    Args:
        callback (Callable[[str], None]): A function to handle button clicks.
                                          The function receives the first
                                          character of the button label as an
                                          argument.

    Returns:
        QGroupBox: A group box containing the control keys buttons.
    """
    sideButtonLayout = QVBoxLayout()
    labels = ["Hold", "Scan", "L/O", "Menu", "Func"]

    for label in labels:
        btn = QPushButton(label)
        btn.setFixedSize(80, 40)
        btn.clicked.connect(lambda _, k=label: callback(k[0]))
        sideButtonLayout.addWidget(btn)

    buttonGroup = QGroupBox("Control Keys")
    buttonGroup.setLayout(sideButtonLayout)
    return buttonGroup
