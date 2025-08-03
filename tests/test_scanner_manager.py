"""Tests for functions in :mod:`utilities.scanner.manager`."""

import os
import sys
import types

# Ensure ``utilities`` is importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide a minimal serial stub before importing the module
serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
serial_tools_stub = types.ModuleType("serial.tools")
list_ports_stub = types.ModuleType("serial.tools.list_ports")
list_ports_stub.comports = lambda *a, **k: []
serial_tools_stub.list_ports = list_ports_stub
serial_stub.tools = serial_tools_stub
sys.modules.setdefault("serial", serial_stub)
sys.modules.setdefault("serial.tools", serial_tools_stub)
sys.modules.setdefault("serial.tools.list_ports", list_ports_stub)

from utilities.scanner import manager  # noqa: E402
from utilities.scanner.connection_manager import ConnectionManager  # noqa: E402


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
    cm = ConnectionManager()
    assert manager.connect_to_scanner(cm, "abc") == (
        "STATUS:ERROR|CODE:INVALID_SCANNER_ID|MESSAGE:"
        "Scanner_ID_must_be_a_number"
    )


def test_connect_to_scanner_no_scanners(monkeypatch):
    """Return an error when no scanners are detected."""
    monkeypatch.setattr(manager, "find_all_scanner_ports", lambda: [])
    cm = ConnectionManager()
    assert (
        manager.connect_to_scanner(cm, "1")
        == "STATUS:ERROR|CODE:NO_SCANNERS_FOUND"
    )


def test_connect_to_scanner_id_out_of_range(monkeypatch):
    """Return an error when the ID is outside the detected range."""
    monkeypatch.setattr(
        manager, "find_all_scanner_ports", lambda: [("COM1", "X")]
    )
    cm = ConnectionManager()
    assert (
        manager.connect_to_scanner(cm, "2")
        == "STATUS:ERROR|CODE:INVALID_SCANNER_ID|MAX_ID:1"
    )


def test_connect_to_scanner_unknown_uniden_model(monkeypatch):
    """Return GenericUnidenAdapter when model prefix matches Uniden."""
    from adapters.uniden.generic_adapter import GenericUnidenAdapter

    class DummySerial:
        def __init__(self, *a, **k):
            self.is_open = True

        def close(self):
            self.is_open = False

    monkeypatch.setattr(manager.serial, "Serial", lambda *a, **k: DummySerial())
    monkeypatch.setattr(
        manager, "find_all_scanner_ports", lambda: [("COM1", "BC999XLT")]
    )

    cm = ConnectionManager()
    ser, adapter, commands, help_text = manager.connect_to_scanner(cm, "1")
    assert isinstance(adapter, GenericUnidenAdapter)
    assert isinstance(ser, DummySerial)


def test_generic_uniden_read_volume(monkeypatch):
    """read_volume should parse numeric volume from response."""
    from adapters.uniden.generic_adapter import GenericUnidenAdapter

    adapter = GenericUnidenAdapter(machine_mode=True)
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: b"VOL,7")
    assert adapter.read_volume(None) == 7


def test_generic_uniden_write_volume(monkeypatch):
    """write_volume should return True when 'OK' is received."""
    from adapters.uniden.generic_adapter import GenericUnidenAdapter

    adapter = GenericUnidenAdapter(machine_mode=True)
    adapter.commands.pop("VOL", None)
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: b"OK")
    assert adapter.write_volume(None, 5) is True


def test_generic_uniden_read_squelch(monkeypatch):
    """read_squelch should parse numeric squelch from response."""
    from adapters.uniden.generic_adapter import GenericUnidenAdapter

    adapter = GenericUnidenAdapter(machine_mode=True)
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: b"SQL,3")
    assert adapter.read_squelch(None) == 3


def test_generic_uniden_write_squelch(monkeypatch):
    """write_squelch should return True when 'OK' is received."""
    from adapters.uniden.generic_adapter import GenericUnidenAdapter

    adapter = GenericUnidenAdapter(machine_mode=True)
    adapter.commands.pop("SQL", None)
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: b"OK")
    assert adapter.write_squelch(None, 2) is True
