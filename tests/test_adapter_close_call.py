"""Tests for BCD325P2Adapter close call helpers and scan controls."""

import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide minimal serial stub
serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
sys.modules.setdefault("serial", serial_stub)

from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402


def test_scan_controls_return_raw(monkeypatch):
    """start_scanning and stop_scanning return raw responses."""
    adapter = BCD325P2Adapter()
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
