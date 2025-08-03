"""Tests for BC125AT band scope functionality."""

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

from adapters.uniden.bc125at_adapter import BC125ATAdapter  # noqa: E402
from utilities.core.command_registry import build_command_table  # noqa: E402


def test_bc125at_sweep_parses_units(monkeypatch):
    adapter = BC125ATAdapter()
    monkeypatch.setattr(
        adapter, "enter_quick_frequency_hold", lambda ser, f: None
    )
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    result = adapter.sweep_band_scope(None, "144M", "2M", "500k", "500k")
    assert result[0][0] == 143.0


def test_bc125at_band_scope_auto_width(monkeypatch):
    adapter = BC125ATAdapter()
    monkeypatch.setattr(
        adapter, "enter_quick_frequency_hold", lambda ser, f: None
    )
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    adapter.sweep_band_scope(None, "146M", "2M", "0.5M", "0.5M")
    assert adapter.band_scope_width == 5


def test_bc125at_configure_band_scope_wraps_programming(monkeypatch):
    adapter = BC125ATAdapter()
    calls = []

    def send_command_stub(ser, cmd):
        calls.append(cmd)
        return "OK"

    monkeypatch.setattr(adapter, "send_command", send_command_stub)
    monkeypatch.setattr(
        adapter, "enter_quick_frequency_hold", lambda ser, f: None
    )
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    monkeypatch.setattr(adapter, "start_scanning", lambda ser: calls.append("START"))

    result = adapter.configure_band_scope(None, "air")

    assert calls[0] == "PRG"
    assert calls[1] == "EPG"
    assert calls[-1] == "START"
    assert result == "OK"


def test_bc125at_configure_band_scope_sets_width(monkeypatch):
    adapter = BC125ATAdapter()
    adapter.in_program_mode = True

    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: "OK")
    monkeypatch.setattr(
        adapter, "enter_quick_frequency_hold", lambda ser, f: None
    )
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    monkeypatch.setattr(adapter, "start_scanning", lambda ser: None)

    result = adapter.configure_band_scope(None, "air")
    assert adapter.band_scope_width == 3362
    assert result == "OK"


def test_bc125at_band_scope_search_flag(monkeypatch):
    adapter = BC125ATAdapter()
    monkeypatch.setattr(adapter, "_calc_band_scope_width", lambda span, bw: 3)

    pwr_responses = [
        "PWR,10,01080000",
        "PWR,20,01080010",
        "PWR,30,01080020",
    ]

    def send_command_stub(ser, cmd):
        if cmd.startswith("CSP"):
            return "OK"
        if cmd.startswith("CSG"):
            return "OK"
        if cmd == "PWR":
            return pwr_responses.pop(0)
        return "OK"

    monkeypatch.setattr(adapter, "send_command", send_command_stub)
    monkeypatch.setattr(adapter, "start_scanning", lambda ser: None)
    monkeypatch.setattr(adapter, "stop_scanning", lambda ser: None)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "air search")
    lines = output.splitlines()
    assert len(lines) == 4  # 3 records + summary
    assert lines[-1].startswith("center=")
