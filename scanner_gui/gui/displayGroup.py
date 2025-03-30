# displayGroup.py

from PyQt6.QtWidgets import QVBoxLayout, QLabel, QGroupBox
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

def buildDisplayGroup(font_lcd, displayLabels: list) -> QGroupBox:
    displayGroupLayout = QVBoxLayout()
    
    for _ in range(6):
        lbl = QLabel("".ljust(16))
        lbl.setFont(font_lcd)
        lbl.setObjectName("DisplayLine")
        lbl.setProperty("highlight", False)
        lbl.setProperty("underline", False)
        displayLabels.append(lbl)
        displayGroupLayout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

    displayGroup = QGroupBox("Display")
    displayGroup.setLayout(displayGroupLayout)
    return displayGroup
