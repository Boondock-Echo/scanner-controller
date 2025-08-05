"""Tests for Close Call command formatting methods."""

import os
import sys
import types

# Ensure utilities can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide a minimal serial stub
serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
sys.modules.setdefault("serial", serial_stub)

from scanner_controller.adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402


def test_close_call_commands(monkeypatch):
    """Adapter methods should format Close Call commands correctly."""
    adapter = BCD325P2Adapter()

    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: f"CMD:{cmd}")

    assert adapter.get_close_call(None) == "CMD:CLC"
    assert adapter.set_close_call(None, "1,0") == "CMD:CLC,1,0"
    assert adapter.set_close_call(None, [1, 0]) == "CMD:CLC,1,0"
    assert adapter.jump_mode(None, "CC_MODE") == "CMD:JPM,CC_MODE,"
    assert (
        adapter.jump_mode(None, "SVC_MODE", "Racing")
        == "CMD:JPM,SVC_MODE,Racing"
    )
    assert adapter.jump_to_number_tag(None, "1", "2") == "CMD:JNT,1,2"
    assert adapter.jump_to_number_tag(None) == "CMD:JNT,,"
