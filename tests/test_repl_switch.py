"""Test REPL switch command closes old connection before opening new one."""

import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Minimal serial stub similar to other tests
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
sys.modules.setdefault("serial", serial_stub)
sys.modules.setdefault("serial.tools", serial_tools_stub)
sys.modules.setdefault("serial.tools.list_ports", list_ports_stub)

from utilities.scanner.connection_manager import ConnectionManager  # noqa: E402
from utilities.command.loop import main_loop  # noqa: E402
import utilities.scanner.connection_manager as cm_module  # noqa: E402


class DummyAdapter:
    """Minimal adapter for connection tests."""


def _patch_manager(monkeypatch):
    monkeypatch.setattr(cm_module.serial, "Serial", DummySerial, raising=False)
    monkeypatch.setattr(
        cm_module, "get_scanner_adapter", lambda model, machine_mode=False: DummyAdapter()
    )
    monkeypatch.setattr(
        cm_module,
        "build_command_table",
        lambda adapter, ser: ({"ping": lambda ser_, adapter_: f"pong:{ser_.port}"}, {"ping": "ping"}),
    )


def _open_two_connections(cm):
    id1 = cm.open_connection("COM1", "X")
    id2 = cm.open_connection("COM2", "X")
    return id1, id2


def test_repl_switch(monkeypatch, capsys):
    """Switch command should close the active connection and open a new one."""
    cm = ConnectionManager()
    _patch_manager(monkeypatch)
    id1, id2 = _open_two_connections(cm)

    # remember serial for id2 so we can check closed state
    ser2 = cm.get(id2)[0]

    def fake_connect(scanner_id, machine_mode=False):
        new_id = cm.open_connection("COM3", "X")
        return cm.get(new_id)

    monkeypatch.setattr("utilities.command.loop.connect_to_scanner", fake_connect)

    inputs = ["switch 1", "list", "exit"]
    monkeypatch.setattr("builtins.input", lambda prompt="": inputs.pop(0))
    monkeypatch.setattr("utilities.command.loop.initialize_readline", lambda c: None)

    main_loop(cm, machine_mode=False)

    out_lines = capsys.readouterr().out.strip().splitlines()
    # last 'list' output should show connections 1 and 3, with 3 active
    assert any("[1]" in line and "COM1" in line for line in out_lines)
    assert any("* COM3" in line for line in out_lines)
    # connection id2 should be removed and closed
    assert cm.get(id2) is None
    assert ser2.is_open is False
    assert cm.get(cm.active_id)[0].port == "COM3"

