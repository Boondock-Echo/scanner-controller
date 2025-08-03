"""
Core utilities package.

This package contains fundamental utilities for command processing,
scanner communication, and core functionality that is used across
the entire application.
"""

# Define which symbols to export when using "from utilities.core import *"
__all__ = ["clear_serial_buffer", "ScannerCommand"]

# Function Imports
# ---------------
# Import core scanner functionality
try:
    from utilities.core.command_library import ScannerCommand
    from utilities.core.serial_utils import clear_serial_buffer
except ImportError:  # pragma: no cover - during refactoring
    import sys

    print("Warning: Could not import required utilities")
    print(f"Python path: {sys.path}")
