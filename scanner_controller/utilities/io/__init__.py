"""
IO utilities package.

This package provides input/output related functionality, including
readline setup, serial communication, and other I/O operations.
"""

from scanner_controller.utilities.io.readline_setup import initialize_readline

__all__ = ["initialize_readline"]
