"""Tests for reading global lockout data from scanner_controller.adapters."""

import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

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

from scanner_controller.adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402
from scanner_controller.adapters.uniden.bc125at_adapter import BC125ATAdapter  # noqa: E402


def _prepare_adapter(adapter, monkeypatch, responses):
    monkeypatch.setattr(adapter, "enter_programming_mode", lambda ser: None)
    monkeypatch.setattr(adapter, "exit_programming_mode", lambda ser: None)
    monkeypatch.setattr(
        adapter,
        "send_command",
        lambda ser, cmd: responses.pop(0) if responses else b"GLF,100",
    )


def test_read_global_lockout_timeout(monkeypatch):
    adapter = BCD325P2Adapter()
    responses = [b"GLF,100", b"GLF,200"]  # No sentinel
    _prepare_adapter(adapter, monkeypatch, responses)
    result = adapter.read_global_lockout(None, timeout=0.01)
    assert "Timed out" in result


def test_read_global_lockout_success(monkeypatch):
    adapter = BC125ATAdapter()
    responses = [b"GLF,1", b"GLF,2", b"GLF,-1"]
    _prepare_adapter(adapter, monkeypatch, responses)
    result = adapter.read_global_lockout(None)
    assert "GLF,1" in result and "GLF,2" in result
