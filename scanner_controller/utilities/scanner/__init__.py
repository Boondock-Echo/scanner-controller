"""
Scanner utilities package.

This package provides utilities specific to scanner management,
detection, and control that are not specific to any single scanner model.
"""

from scanner_controller.utilities.scanner.factory import get_scanner_adapter
from scanner_controller.utilities.scanner.manager import (
    connect_to_scanner,
    scan_for_scanners,
    switch_scanner,
)

__all__ = [
    "connect_to_scanner",
    "scan_for_scanners",
    "switch_scanner",
    "get_scanner_adapter",
]
