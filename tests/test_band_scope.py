"""Tests for band scope command behavior and presets."""

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


def test_band_select_air_command(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: cmd)
    # Disable BSP validator to avoid preset span restrictions
    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)

    commands, _ = build_command_table(adapter, None)
    result = commands["band select"](None, adapter, "air")
    assert result == "BSP,01220000,833,40M,0"


def test_band_select_registered(monkeypatch):
    adapter = BCD325P2Adapter()
    monkeypatch.setattr(adapter, "configure_band_scope", lambda ser, *a: "")
    commands, help_text = build_command_table(adapter, None)

    assert "band select" in commands
    assert "band select" in help_text
    assert "band set" in commands
    assert "band set" in help_text


def test_band_set_alias(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: cmd)

    commands, _ = build_command_table(adapter, None)
    result_alias = commands["band set"](None, adapter, "air")
    result_select = commands["band select"](None, adapter, "air")
    assert result_alias == result_select


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



def test_band_scope_auto_width(monkeypatch):
    adapter = BCD325P2Adapter()

    monkeypatch.setattr(adapter, "write_frequency", lambda ser, f: None)
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    adapter.sweep_band_scope(None, "146M", "2M", "0.5M", "0.5M")
    assert adapter.band_scope_width == 5

    def fake_stream(ser, c=5):
        for i in range(c):
            yield (0, 145.0 + 0.5 * i, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", fake_stream)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "5")
    lines = output.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("center=")


def test_configure_band_scope_wraps_programming(monkeypatch):
    adapter = BCD325P2Adapter()
    calls = []

    def send_command_stub(ser, cmd):
        calls.append(cmd)
        return "OK"

    monkeypatch.setattr(adapter, "send_command", send_command_stub)
    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)
    monkeypatch.setattr(
        adapter, "start_scanning", lambda ser: calls.append("START")
    )

    adapter.configure_band_scope(None, "air")

    assert calls[0] == "PRG"
    assert calls[1].startswith("BSP")
    assert calls[2] == "EPG"
    assert calls[-1] == "START"


def test_configure_band_scope_sets_width(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True

    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: "OK")
    monkeypatch.setattr(adapter, "start_scanning", lambda ser: None)

    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)

    adapter.configure_band_scope(None, "air")
    assert adapter.band_scope_width == 4803

    adapter.in_program_mode = False

    def fake_stream(ser, c=adapter.band_scope_width):
        for i in range(c):
            yield (0, 100.0 + i, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", fake_stream)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "5")
    lines = output.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("center=")



def test_band_scope_no_data(monkeypatch):
    adapter = BCD325P2Adapter()

    def empty_stream(ser, c=5):
        yield from []

    monkeypatch.setattr(adapter, "stream_custom_search", empty_stream)

    commands, _ = build_command_table(adapter, None)
    result = commands["band scope"](None, adapter, "5")

    assert result == "No band scope data received"



def test_band_scope_summary_line(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.band_scope_width = 3
    adapter.last_center = 146.0
    adapter.last_span = 2.0
    adapter.last_step = 0.5
    adapter.last_mod = "FM"

    def stream_stub(ser, c=3):
        yield (10, 145.0, 0)
        yield (20, 146.0, 0)
        yield (30, 147.0, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "3")
    lines = output.splitlines()
    assert lines[:3] == ["145.0000", "146.0000", "147.0000"]
    assert lines[-1].startswith("center=")
    assert "min=145.000" in lines[-1]
    assert "max=147.000" in lines[-1]
    assert "span=2M" in lines[-1]
    assert "step=500k" in lines[-1]
    assert "mod=FM" in lines[-1]


def test_band_scope_in_program_mode(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True

    called = []

    def stream_stub(ser, c=3):
        called.append(True)
        yield (10, 145.0, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, _ = build_command_table(adapter, None)
    result = commands["band scope"](None, adapter, "3")

    assert (
        result
        == "Scanner is in programming mode. Run 'send EPG' then 'band scope start'."
    )
    assert not called


def test_band_scope_list_hits(monkeypatch):
    adapter = BCD325P2Adapter()

    def stream_stub(ser, c=1024):
        yield (0, 145.0, 0)
        yield (50, 146.0, 1)
        yield (0, 147.0, 0)
        yield (30, 148.0, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "list")
    lines = output.splitlines()
    assert lines[:2] == ["146.0000", "148.0000"]
    assert lines[-1].startswith("center=")
