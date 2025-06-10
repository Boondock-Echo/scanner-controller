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
from utilities.graph_utils import render_band_scope_waterfall


def test_presets_load():
    presets = importlib.import_module(
        "config.band_scope_presets"
    ).BAND_SCOPE_PRESETS
    assert "air" in presets
    assert "race" in presets
    assert isinstance(presets["air"], tuple)
    assert len(presets["air"]) == 4


def test_band_select_air_command(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: cmd)

    commands, _ = build_command_table(adapter, None)
    result = commands["band select"](None, adapter, "air")
    assert result == "BSP,00125000,833,20M,0"


def test_band_select_registered(monkeypatch):
    adapter = BCD325P2Adapter()
    monkeypatch.setattr(adapter, "configure_band_scope", lambda ser, *a: "")
    commands, help_text = build_command_table(adapter, None)

    assert "band select" in commands
    assert "band select" in help_text


def test_custom_search_returns_pairs(monkeypatch):
    adapter = BCD325P2Adapter()

    def sweep_stub(ser, c, s, st, bw=None):
        return [(100.0, 0.5), (101.0, 0.6)]

    monkeypatch.setattr(adapter, "sweep_band_scope", sweep_stub)
    commands, _ = build_command_table(adapter, None)

    result = commands["custom search"](None, adapter, "100 2 1 1")
    assert result == [(100.0, 0.5), (101.0, 0.6)]


def test_custom_search_parses_units(monkeypatch):
    adapter = BCD325P2Adapter()

    monkeypatch.setattr(adapter, "write_frequency", lambda ser, f: None)
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    result = adapter.sweep_band_scope(None, "144M", "2M", "500k", "500k")
    assert result[0][0] == 143.0


def test_render_band_scope_waterfall_wrap():
    pairs = [
        (100.0, 0.0),
        (101.0, 0.5),
        (102.0, 1.0),
        (100.0, 1.0),
        (101.0, 0.5),
        (102.0, 0.0),
    ]
    output = render_band_scope_waterfall(pairs, width=3)
    lines = output.splitlines()
    assert len(lines) == 2
    assert all(len(line) == 3 for line in lines)


def test_band_scope_auto_width(monkeypatch):
    adapter = BCD325P2Adapter()

    monkeypatch.setattr(adapter, "write_frequency", lambda ser, f: None)
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    adapter.sweep_band_scope(None, "146M", "2M", "0.5M", "0.5M")
    assert adapter.band_scope_width == 5

    monkeypatch.setattr(
        adapter,
        "stream_custom_search",
        lambda ser, c=5: [(0, 145.0 + 0.5 * i, 0) for i in range(c)],
    )

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "5")
    lines = output.splitlines()
    assert all(len(line) == 5 for line in lines)


def test_configure_band_scope_wraps_programming(monkeypatch):
    adapter = BCD325P2Adapter()
    calls = []

    def send_command_stub(ser, cmd):
        calls.append(cmd)
        return "OK"

    monkeypatch.setattr(adapter, "send_command", send_command_stub)

    adapter.configure_band_scope(None, "air")

    assert calls[0] == "PRG"
    assert calls[1].startswith("BSP")
    assert calls[-1] == "EPG"
