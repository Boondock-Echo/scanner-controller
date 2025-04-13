# rotaryKnob.py
"""
Rotaryknob module.

This module provides functionality related to rotaryknob.
"""


from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton

"""
    buildRotaryKnob function.

    Provides functionality for buildRotaryKnob.
    """


def buildRotaryKnob(
    knobPressedCallback=None, rotateLeftCallback=None, rotateRightCallback=None
) -> QGroupBox:
    """Build a rotary knob UI component.

    This function creates a rotary knob UI component with optional callbacks for
    knob press, rotate left, and rotate right actions.

    Args:
        knobPressedCallback (callable, optional): Function to call when the
            knob is pressed.
        rotateLeftCallback (callable, optional): Function to call when the
            knob is rotated left.
        rotateRightCallback (callable, optional): Function to call when the
            knob is rotated right.

    Returns:
        QGroupBox: A group box containing the rotary knob UI component.
    """
    mainLayout = QHBoxLayout()
    mainLayout.setSpacing(10)
    mainLayout.setContentsMargins(5, 5, 5, 5)

    buttonStyle = """
            QPushButton {
                border: none;
                background-color: transparent;
            }
            QPushButton:hover {
                background-color: rgba(100, 255, 100, 30);
                border-radius: 5px;
            }
            QPushButton:pressed {
                background-color: rgba(0, 255, 0, 50);
            }
        """

    if rotateLeftCallback:
        leftButton = QPushButton()
        leftButton.setIcon(QIcon("scanner_gui/icons/arrow-left.svg"))
        leftButton.setIconSize(QSize(20, 63))
        leftButton.setFixedSize(20, 60)
        leftButton.setStyleSheet(buttonStyle)
        leftButton.clicked.connect(rotateLeftCallback)
        mainLayout.addWidget(leftButton)

    if knobPressedCallback:
        knobButton = QPushButton()
        knobButton.setIcon(QIcon("scanner_gui/icons/rotary-knob.svg"))
        knobButton.setIconSize(QSize(58, 58))
        knobButton.setFixedSize(60, 60)
        knobButton.setStyleSheet(buttonStyle)
        knobButton.clicked.connect(knobPressedCallback)
        mainLayout.addWidget(knobButton)

    if rotateRightCallback:
        rightButton = QPushButton()
        rightButton.setIcon(QIcon("scanner_gui/icons/arrow-right.svg"))
        rightButton.setIconSize(QSize(20, 63))
        rightButton.setFixedSize(20, 60)
        rightButton.setStyleSheet(buttonStyle)
        rightButton.clicked.connect(rotateRightCallback)
        mainLayout.addWidget(rightButton)

    knobGroup = QGroupBox("Rotary Knob")
    knobGroup.setLayout(mainLayout)
    return knobGroup
