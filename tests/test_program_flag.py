"""Tests for program flag handling in adapters."""

import os
import sys
import types

# Ensure project modules can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide a minimal serial stub
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

from adapters.uniden.bc125at_adapter import BC125ATAdapter  # noqa: E402
import utilities.core.serial_utils as serial_utils  # noqa: E402


def test_prg_toggles_flag(monkeypatch):
    adapter = BC125ATAdapter()
    adapter.in_program_mode = False
    monkeypatch.setattr(serial_utils, "send_command", lambda ser, cmd: "OK")

    resp = adapter.send_command(None, "PRG")
    assert resp == b"OK"
    assert adapter.in_program_mode


def test_epg_toggles_flag(monkeypatch):
    adapter = BC125ATAdapter()
    adapter.in_program_mode = True
    monkeypatch.setattr(serial_utils, "send_command", lambda ser, cmd: "OK")

    resp = adapter.send_command(None, "EPG")
    assert resp == b"OK"
    assert not adapter.in_program_mode
