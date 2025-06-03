"""
Scanner utilities package.

This package provides utilities specific to scanner management,
detection, and control that are not specific to any single scanner model.
"""

from utilities.scanner.factory import get_scanner_adapter
from utilities.scanner.manager import (
    connect_to_scanner,
    handle_switch_command,
    scan_for_scanners,
)

__all__ = [
    "connect_to_scanner",
    "handle_switch_command",
    "scan_for_scanners",
    "get_scanner_adapter",
]
