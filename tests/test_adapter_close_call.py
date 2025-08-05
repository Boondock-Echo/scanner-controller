"""Tests for Uniden adapter scan controls and close call helpers."""

import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide minimal serial stub
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
import pytest


@pytest.mark.parametrize("adapter_cls", [BCD325P2Adapter, BC125ATAdapter])
def test_scan_controls_return_raw(monkeypatch, adapter_cls):
    """start_scanning and stop_scanning return raw responses."""
    adapter = adapter_cls()
    monkeypatch.setattr(adapter, "send_key", lambda ser, seq: f"KEY:{seq}")

    assert adapter.start_scanning(None) == "KEY:S"
    assert adapter.stop_scanning(None) == "KEY:H"


def test_close_call_helpers_raw(monkeypatch):
    """Close Call helper methods pass through send_command."""
    adapter = BCD325P2Adapter()
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: f"CMD:{cmd}")

    assert adapter.get_close_call(None) == "CMD:CLC"
    assert adapter.set_close_call(None, [0, 1, 2]) == "CMD:CLC,0,1,2"
    assert adapter.set_close_call(None, "0,1,2") == "CMD:CLC,0,1,2"
    assert adapter.jump_mode(None, "SCN_MODE", "5") == "CMD:JPM,SCN_MODE,5"
    assert adapter.jump_mode(None, "CC_MODE") == "CMD:JPM,CC_MODE,"
    assert adapter.jump_to_number_tag(None, "1", "2") == "CMD:JNT,1,2"
    assert adapter.jump_to_number_tag(None) == "CMD:JNT,,"
