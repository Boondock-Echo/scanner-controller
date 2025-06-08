"""
Scanner GUI module for controlling scanner devices.

This module provides a graphical user interface for interacting with various
scanner models, including the Uniden BC125AT.
"""

# Import the controller directly
from .controller import ScannerController, controller_registry

# Import ScannerGUI using the safe getter function
from .main import get_scanner_gui

# Get the ScannerGUI class safely
ScannerGUI = get_scanner_gui()

__all__ = ['ScannerGUI', 'ScannerController', 'controller_registry']
