# keypad.py

"""
Keypad module.

This module provides functionality related to keypad.
"""

from typing import Callable

# Third-party imports
from PyQt6.QtWidgets import QGridLayout, QGroupBox, QPushButton


def buildKeypad(callback: Callable[[str], None]) -> QGroupBox:
    """
    Build the keypad widget with number buttons.

    Creates a grid layout with numerical keys and connects button press
    events to the provided callback function.

    Args:
        callback: Function to call when a key is pressed, receives the key
        as a string

    Returns:
        QGroupBox containing the keypad grid
    """
    grid = QGridLayout()
    keys = ["1", "2", "3", "4", "5", "6", "7", "8", "9", ".", "0", "E"]

    for i, key in enumerate(keys):
        btn = QPushButton(key)
        btn.setFixedSize(60, 60)
        btn.clicked.connect(lambda _, k=key: callback(k))
        grid.addWidget(btn, i // 3, i % 3)

    gridGroup = QGroupBox("Keypad")
    gridGroup.setLayout(grid)
    return gridGroup
