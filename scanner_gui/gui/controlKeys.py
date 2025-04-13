# controlKeys.py

"""
Controlkeys module.

This module provides functionality related to controlkeys.
"""

from typing import Callable

from PyQt6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout


def buildControlKeys(callback: Callable[[str], None]) -> QGroupBox:
    """
    Build and return a QGroupBox containing control key buttons.

    Args:
        callback: A callable that takes a string argument, triggered on
        button click.

    Returns:
        QGroupBox: A group box containing the control key buttons.
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
