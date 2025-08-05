"""Tests for program flag handling in adapters."""

import os
import sys
import types
import pytest

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

from scanner_controller.adapters.uniden.bc125at_adapter import BC125ATAdapter  # noqa: E402
from scanner_controller.adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402
import scanner_controller.utilities.core.serial_utils as serial_utils  # noqa: E402


@pytest.mark.parametrize("adapter_cls", [BC125ATAdapter, BCD325P2Adapter])
def test_prg_toggles_flag(monkeypatch, adapter_cls):
    adapter = adapter_cls()
    adapter.in_program_mode = False
    monkeypatch.setattr(serial_utils, "send_command", lambda ser, cmd: "OK")

    resp = adapter.send_command(None, "PRG")
    assert resp == b"OK"
    assert adapter.in_program_mode


@pytest.mark.parametrize("adapter_cls", [BC125ATAdapter, BCD325P2Adapter])
def test_epg_toggles_flag(monkeypatch, adapter_cls):
    adapter = adapter_cls()
    adapter.in_program_mode = True
    monkeypatch.setattr(serial_utils, "send_command", lambda ser, cmd: "OK")

    resp = adapter.send_command(None, "EPG")
    assert resp == b"OK"
    assert not adapter.in_program_mode
