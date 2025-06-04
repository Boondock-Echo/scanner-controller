"""Tests for functions in :mod:`utilities.scanner.manager`."""

import os
import sys
import types

# Ensure ``utilities`` is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide a minimal serial stub before importing the module
serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
sys.modules.setdefault("serial", serial_stub)

from utilities.scanner import manager  # noqa: E402


def test_scan_for_scanners_no_devices(monkeypatch):
    """Return an error string when no scanners are found."""
    monkeypatch.setattr(manager, "find_all_scanner_ports", lambda: [])
    assert manager.scan_for_scanners() == "STATUS:ERROR|CODE:NO_SCANNERS_FOUND"


def test_scan_for_scanners_multiple(monkeypatch):
    """Format output correctly for multiple detected scanners."""
    monkeypatch.setattr(
        manager,
        "find_all_scanner_ports",
        lambda: [("COM1", "ModelA"), ("COM2", "ModelB")],
    )
    result = manager.scan_for_scanners()
    assert result == (
        "STATUS:OK|SCANNERS_FOUND:2|"
        "SCANNER:1|PORT:COM1|MODEL:ModelA|"
        "SCANNER:2|PORT:COM2|MODEL:ModelB"
    )


def test_connect_to_scanner_invalid_input(monkeypatch):
    """Return an error when the scanner ID is not a number."""
    assert manager.connect_to_scanner("abc") == (
        "STATUS:ERROR|CODE:INVALID_SCANNER_ID|MESSAGE:"
        "Scanner_ID_must_be_a_number"
    )


def test_connect_to_scanner_no_scanners(monkeypatch):
    """Return an error when no scanners are detected."""
    monkeypatch.setattr(manager, "find_all_scanner_ports", lambda: [])
    assert (
        manager.connect_to_scanner("1") == "STATUS:ERROR|CODE:NO_SCANNERS_FOUND"
    )


def test_connect_to_scanner_id_out_of_range(monkeypatch):
    """Return an error when the ID is outside the detected range."""
    monkeypatch.setattr(
        manager, "find_all_scanner_ports", lambda: [("COM1", "X")]
    )
    assert (
        manager.connect_to_scanner("2")
        == "STATUS:ERROR|CODE:INVALID_SCANNER_ID|MAX_ID:1"
    )
