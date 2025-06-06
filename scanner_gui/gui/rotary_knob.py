"""
This module provides a function to build a rotary knob widget using PyQt6.

The rotary knob includes buttons for rotating left, rotating right, and
pressing the knob.
"""

# rotaryKnob.py
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QGroupBox, QHBoxLayout, QPushButton


def build_rotary_knob(
    knob_pressed_callback=None,
    rotate_left_callback=None,
    rotate_right_callback=None,
) -> QGroupBox:
    """
    Build a rotary knob widget with optional callbacks for button actions.

    Args:
        knob_pressed_callback (callable, optional): Function to call when the knob
        is pressed.
        rotate_left_callback (callable, optional): Function to call when the left
        button is clicked.
        rotate_right_callback (callable, optional): Function to call when the
        right button is clicked.

    Returns:
        QGroupBox: A group box containing the rotary knob widget.
    """
    main_layout = QHBoxLayout()
    main_layout.setSpacing(10)
    main_layout.setContentsMargins(5, 5, 5, 5)

    button_style = """
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
    if rotate_left_callback:
        main_layout.addWidget(
            _create_knob_button(
                "scanner_gui/icons/arrow-left.svg",
                (20, 63),
                (20, 60),
                button_style,
                rotate_left_callback,
            )
        )

    if knob_pressed_callback:
        main_layout.addWidget(
            _create_knob_button(
                "scanner_gui/icons/rotary-knob.svg",
                (58, 58),
                (60, 60),
                button_style,
                knob_pressed_callback,
            )
        )

    if rotate_right_callback:
        main_layout.addWidget(
            _create_knob_button(
                "scanner_gui/icons/arrow-right.svg",
                (20, 63),
                (20, 60),
                button_style,
                rotate_right_callback,
            )
        )

    knob_group = QGroupBox("Rotary Knob")
    knob_group.setLayout(main_layout)
    return knob_group


def _create_knob_button(icon_path, icon_size, button_size, style, callback):
    """Create a knob button with the specified properties."""
    button = QPushButton()
    button.setIcon(QIcon(icon_path))
    button.setIconSize(QSize(*icon_size))
    button.setFixedSize(*button_size)
    button.setStyleSheet(style)
    button.clicked.connect(callback)
    return button
