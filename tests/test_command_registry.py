"""Tests for build_command_table scanning commands."""

import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide minimal serial stub
serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
sys.modules.setdefault("serial", serial_stub)

from utilities.core.command_registry import build_command_table  # noqa: E402
from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402


def test_scan_start_stop_registered(monkeypatch):
    """``build_command_table`` registers scan start/stop for BCD325P2."""
    adapter = BCD325P2Adapter()
    # Stub out send_key to avoid serial I/O
    monkeypatch.setattr(adapter, "send_key", lambda ser, seq: f"KEY:{seq}")

    commands, help_text = build_command_table(adapter, None)

    assert "scan start" in commands
    assert "scan stop" in commands
    assert help_text["scan start"] == "Start scanner scanning process."
    assert help_text["scan stop"] == "Stop scanner scanning process."

    # Ensure commands use adapter methods
    assert commands["scan start"]() == "KEY:S"
    assert commands["scan stop"]() == "KEY:H"


def test_bsp_and_bsv_commands_present(monkeypatch):
    """Battery save (BSV) and Band Scope (BSP) commands exist after build."""
    adapter = BCD325P2Adapter()
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: cmd)

    commands, _ = build_command_table(adapter, None)

    assert "bsv" in commands
    assert "bsp" in commands
