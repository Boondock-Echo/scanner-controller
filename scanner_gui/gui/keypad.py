"""
This module is part of the scanner_gui package.

This module provides a function to build a keypad GUI component using PyQt6.
"""

# keypad.py

from typing import Callable

from PyQt6.QtWidgets import QGridLayout, QGroupBox, QPushButton


def buildKeypad(callback: Callable[[str], None]) -> QGroupBox:
    """
    Build keypad GUI component.

    Args:
        callback (Callable[[str], None]): A function to be called when a button
        is pressed, receiving the button's label as an argument.

    Returns:
        QGroupBox: A group box containing the keypad layout.
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
