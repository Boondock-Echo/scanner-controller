# controlKeys.py

from typing import Callable

from PyQt6.QtWidgets import QGroupBox, QPushButton, QVBoxLayout


def buildControlKeys(callback: Callable[[str], None]) -> QGroupBox:
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
