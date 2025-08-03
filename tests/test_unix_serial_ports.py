"""Tests ConnectionManager with Unix-style serial port names."""

import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide a minimal serial stub used by the tested modules
serial_stub = types.ModuleType("serial")


class DummySerial:
    def __init__(self, port, *a, **k):
        self.port = port
        self.is_open = True

    def close(self):
        self.is_open = False


serial_stub.Serial = DummySerial
serial_tools_stub = types.ModuleType("serial.tools")
list_ports_stub = types.ModuleType("serial.tools.list_ports")
list_ports_stub.comports = lambda *a, **k: []
serial_tools_stub.list_ports = list_ports_stub
serial_stub.tools = serial_tools_stub
sys.modules["serial"] = serial_stub
sys.modules["serial.tools"] = serial_tools_stub
sys.modules["serial.tools.list_ports"] = list_ports_stub

from utilities.scanner.connection_manager import ConnectionManager  # noqa: E402
import utilities.scanner.connection_manager as cm_module  # noqa: E402


class DummyAdapter:
    """Minimal adapter for testing."""


def _patch_manager(monkeypatch):
    monkeypatch.setattr(cm_module.serial, "Serial", DummySerial, raising=False)
    monkeypatch.setattr(
        cm_module, "get_scanner_adapter", lambda model, machine_mode=False: DummyAdapter()
    )
    monkeypatch.setattr(
        cm_module,
        "build_command_table",
        lambda adapter, ser: (
            {"ping": lambda ser_, adapter_: f"pong:{ser_.port}"},
            {"ping": "ping"},
        ),
    )


def test_unix_style_serial_ports(monkeypatch):
    """Unix-style serial ports are handled correctly."""
    cm = ConnectionManager()
    _patch_manager(monkeypatch)

    id0 = cm.open_connection("/dev/ttyUSB0", "X")
    id1 = cm.open_connection("/dev/ttyUSB1", "X")

    # Ensure connections tracked properly
    assert id0 == 1
    assert id1 == 2
    assert len(cm.list_all()) == 2
    assert cm.get(id0)[0].port == "/dev/ttyUSB0"
    assert cm.get(id1)[0].port == "/dev/ttyUSB1"

    # Bound commands should operate on the correct serial instance
    result0 = cm.get(id0)[2]["ping"]()
    result1 = cm.get(id1)[2]["ping"]()
    assert result0 == "pong:/dev/ttyUSB0"
    assert result1 == "pong:/dev/ttyUSB1"
    assert cm.active_id == id1

    # Closing the active connection switches to remaining one
    cm.close_connection(id1)
    assert cm.active_id == id0

    # Closing last connection clears active_id
    cm.close_connection(id0)
    assert cm.active_id is None
    assert cm.list_all() == []
