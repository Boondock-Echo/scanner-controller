"""
This module provides a function to build a rotary knob widget using PyQt6.

The rotary knob includes buttons for rotating left, rotating right, and
pressing the knob.
"""

# rotaryKnob.py
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton


def buildRotaryKnob(
    knobPressedCallback=None, rotateLeftCallback=None, rotateRightCallback=None
) -> QGroupBox:
    """
    Build a rotary knob widget with optional callbacks for button actions.

    Args:
        knobPressedCallback (callable, optional): Function to call when the knob
        is pressed.
        rotateLeftCallback (callable, optional): Function to call when the left
        button is clicked.
        rotateRightCallback (callable, optional): Function to call when the
        right button is clicked.

    Returns:
        QGroupBox: A group box containing the rotary knob widget.
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

    # Create buttons using a helper function instead of duplicating code
    if rotateLeftCallback:
        mainLayout.addWidget(
            _create_knob_button(
                "scanner_gui/icons/arrow-left.svg",
                (20, 63),
                (20, 60),
                buttonStyle,
                rotateLeftCallback,
            )
        )

    if knobPressedCallback:
        mainLayout.addWidget(
            _create_knob_button(
                "scanner_gui/icons/rotary-knob.svg",
                (58, 58),
                (60, 60),
                buttonStyle,
                knobPressedCallback,
            )
        )

    if rotateRightCallback:
        mainLayout.addWidget(
            _create_knob_button(
                "scanner_gui/icons/arrow-right.svg",
                (20, 63),
                (20, 60),
                buttonStyle,
                rotateRightCallback,
            )
        )

    knobGroup = QGroupBox("Rotary Knob")
    knobGroup.setLayout(mainLayout)
    return knobGroup


def _create_knob_button(icon_path, icon_size, button_size, style, callback):
    """Create a knob button with the specified properties."""
    button = QPushButton()
    button.setIcon(QIcon(icon_path))
    button.setIconSize(QSize(*icon_size))
    button.setFixedSize(*button_size)
    button.setStyleSheet(style)
    button.clicked.connect(callback)
    return button
