import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide minimal serial stub
serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
sys.modules.setdefault("serial", serial_stub)

import importlib
from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402
from utilities.core.command_registry import build_command_table  # noqa: E402


def test_presets_load():
    presets = importlib.import_module(
        "config.band_scope_presets"
    ).BAND_SCOPE_PRESETS
    assert "air" in presets
    assert "race" in presets
    assert isinstance(presets["air"], tuple)
    assert len(presets["air"]) == 4


def test_band_scope_air_command(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: cmd)

    commands, _ = build_command_table(adapter, None)
    result = commands["band scope"]("air")
    assert result == "BSP,00125000,833,20M,0"


def test_band_sweep_registered(monkeypatch):
    adapter = BCD325P2Adapter()
    monkeypatch.setattr(adapter, "sweep_band_scope", lambda ser, c, s, st: [])
    commands, help_text = build_command_table(adapter, None)

    assert "band sweep" in commands
    assert "band sweep" in help_text


def test_band_sweep_returns_pairs(monkeypatch):
    adapter = BCD325P2Adapter()

    def sweep_stub(ser, c, s, st):
        return [(100.0, 0.5), (101.0, 0.6)]

    monkeypatch.setattr(adapter, "sweep_band_scope", sweep_stub)
    commands, _ = build_command_table(adapter, None)

    result = commands["band sweep"]("100 2 1")
    assert result == [(100.0, 0.5), (101.0, 0.6)]


def test_band_sweep_parses_units(monkeypatch):
    adapter = BCD325P2Adapter()

    monkeypatch.setattr(adapter, "write_frequency", lambda ser, f: None)
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    result = adapter.sweep_band_scope(None, "144M", "2M", "500k")
    assert result[0][0] == 143.0
