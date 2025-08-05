"""Tests for the ConnectionManager and REPL commands."""

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

from scanner_controller.utilities.scanner.connection_manager import ConnectionManager  # noqa: E402
from scanner_controller.utilities.command.loop import main_loop  # noqa: E402
import scanner_controller.utilities.scanner.connection_manager as cm_module  # noqa: E402


class DummyAdapter:
    """Minimal adapter for testing."""


def _patch_manager(monkeypatch):
    monkeypatch.setattr(cm_module.serial, "Serial", DummySerial, raising=False)
    monkeypatch.setattr(cm_module, "get_scanner_adapter", lambda model, machine_mode=False: DummyAdapter())
    monkeypatch.setattr(
        cm_module,
        "build_command_table",
        lambda adapter, ser: ({"ping": lambda ser_, adapter_: f"pong:{ser_.port}"}, {"ping": "ping"}),
    )


def _open_two_connections(cm):
    id1 = cm.open_connection("COM1", "X")
    id2 = cm.open_connection("COM2", "X")
    return id1, id2


def test_open_multiple_connections(monkeypatch):
    """Multiple serial connections can be opened and tracked."""
    cm = ConnectionManager()
    _patch_manager(monkeypatch)
    id1, id2 = _open_two_connections(cm)

    assert id1 == 1
    assert id2 == 2
    assert len(cm.list_all()) == 2
    assert cm.get(id1)[0].port == "COM1"
    assert cm.get(id2)[0].port == "COM2"


def test_commands_bound_to_each_connection(monkeypatch):
    """Commands execute on the correct serial instance."""
    cm = ConnectionManager()
    _patch_manager(monkeypatch)
    id1, id2 = _open_two_connections(cm)

    result1 = cm.get(id1)[2]["ping"]()
    result2 = cm.get(id2)[2]["ping"]()

    assert result1 == "pong:COM1"
    assert result2 == "pong:COM2"
    # active connection should remain last opened
    assert cm.active_id == id2


def test_repl_list_use_close(monkeypatch, capsys):
    """REPL commands list, use and close manage connections properly."""
    cm = ConnectionManager()
    _patch_manager(monkeypatch)
    id1, id2 = _open_two_connections(cm)

    inputs = ["list", f"use {id1}", f"close {id1}", "list", "exit"]

    monkeypatch.setattr("builtins.input", lambda prompt="": inputs.pop(0))
    monkeypatch.setattr("utilities.command.loop.initialize_readline", lambda c: None)

    main_loop(cm, machine_mode=False)

    out_lines = capsys.readouterr().out.strip().splitlines()

    assert "[1]  COM1" in out_lines
    assert "[2]* COM2" in out_lines
    assert any("Using connection 1" in line for line in out_lines)
    assert any("Closed connection 1" in line for line in out_lines)
    assert out_lines[-1] == "[2]* COM2"
