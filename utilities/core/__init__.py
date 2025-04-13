"""
Scanner Controller Core Package.

This package provides essential functionality for the scanner controller
application, including low-level serial communication, device control commands,
and core utilities that are fundamental to the operation of the scanner
hardware.

The package ensures proper path configuration and re-exports key functionality
from other modules to provide a unified interface for core operations.
"""

# Standard library imports for filesystem and path management
import os
import sys

# Define which symbols to export when using "from utilities.core import *"
__all__ = ["clear_serial_buffer", "scanner_command"]

# Path Configuration
# ------------------
# Ensure that the root project directory is in the Python path
# This allows imports to work regardless of how the application is launched
script_dir = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Directory Creation
# ------------------
# Create utilities/core directory if it doesn't exist
# This handles first-time setup and ensures the package structure is intact
core_dir = os.path.join(script_dir, "utilities", "core")
if not os.path.exists(core_dir):
    os.makedirs(core_dir)

# Function Imports
# ---------------
# Import core scanner functionality from shared utilities
# These functions provide the primary interface for scanner communications
try:
    # Import essential scanner functions for re-export
    # - clear_serial_buffer: Clears any pending data in the serial connection
    # - scanner_command: Sends formatted commands to the scanner hardware
    from utilities.core.shared_utils import clear_serial_buffer, scanner_command
except ImportError:
    # This exception handling is for development/refactoring scenarios
    # where the file structure may be in transition
    import sys

    print("Warning: Could not import from utilities.core.shared_utils")
    print("If you've already moved files, update this import path")
    print(f"Python path: {sys.path}")
    print("Affected functionality: clear_serial_buffer, scanner_command")
