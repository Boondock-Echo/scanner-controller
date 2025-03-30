# keypad.py

from PyQt6.QtWidgets import QGroupBox, QPushButton, QGridLayout
from typing import Callable

def buildKeypad(callback: Callable[[str], None]) -> QGroupBox:
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
