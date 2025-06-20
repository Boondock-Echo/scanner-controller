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
import pytest


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

    def fake_stream(ser, c=5):
        for i in range(c):
            yield (0, 145.0 + 0.5 * i, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", fake_stream)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "5")
    lines = output.splitlines()
    assert all(len(line) == 5 for line in lines[:-1])


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
    assert calls[2] == "START"
    assert calls[-1] == "EPG"


def test_configure_band_scope_sets_width(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True

    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: "OK")
    monkeypatch.setattr(adapter, "start_scanning", lambda ser: None)

    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)

    adapter.configure_band_scope(None, "air")
    assert adapter.band_scope_width == 4803

    def fake_stream(ser, c=adapter.band_scope_width):
        for i in range(c):
            yield (0, 100.0 + i, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", fake_stream)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "5")
    lines = output.splitlines()
    assert all(len(line) <= 80 for line in lines)


def test_band_scope_output_wrapped(monkeypatch):
    adapter = BCD325P2Adapter()

    # Set a width larger than the terminal width to trigger wrapping
    adapter.band_scope_width = 160

    def fake_stream(ser, c=160):
        for i in range(c):
            yield (0, 145.0 + 0.1 * i, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", fake_stream)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "160")
    lines = output.splitlines()

    # Output should be wrapped so no line exceeds 80 characters
    assert len(lines) == 3
    assert all(len(line) <= 80 for line in lines[:-1])


def test_band_scope_no_data(monkeypatch):
    adapter = BCD325P2Adapter()

    def empty_stream(ser, c=5):
        yield from []

    monkeypatch.setattr(adapter, "stream_custom_search", empty_stream)

    commands, _ = build_command_table(adapter, None)
    result = commands["band scope"](None, adapter, "5")

    assert result == "No band scope data received"


def test_band_scope_baseline(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.band_scope_width = 3

    def stream_stub(ser, c=3):
        yield (10, 100.0, 0)
        yield (20, 101.0, 0)
        yield (40, 102.0, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    captured = {}

    import utilities.core.command_registry as cr

    def fake_render(pairs, width):
        captured["pairs"] = pairs
        return "graph"

    monkeypatch.setattr(cr, "render_band_scope_waterfall", fake_render)

    commands, _ = build_command_table(adapter, None)
    result = commands["band scope"](None, adapter, "3")

    assert result.splitlines()[0] == "graph"
    expected = [
        (100.0, 0.0),
        (101.0, 10 / 1023.0),
        (102.0, 30 / 1023.0),
    ]
    assert captured["pairs"] == pytest.approx(expected)


def test_band_scope_log_scaling(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.band_scope_width = 3

    def stream_stub(ser, c=3):
        yield (10, 100.0, 0)
        yield (20, 101.0, 0)
        yield (40, 102.0, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    captured = {}
    import utilities.core.command_registry as cr

    def fake_render(pairs, width):
        captured["pairs"] = pairs
        return "graph"

    monkeypatch.setattr(cr, "render_band_scope_waterfall", fake_render)

    commands, _ = build_command_table(adapter, None)
    result = commands["band scope"](None, adapter, "3 log")

    assert result.splitlines()[0] == "graph"
    import math

    baseline = 10
    max_db = 20 * math.log10(1023 - baseline + 1)
    expected = [
        (100.0, 0.0),
        (101.0, 20 * math.log10(10 + 1) / max_db),
        (102.0, 20 * math.log10(30 + 1) / max_db),
    ]
    assert captured["pairs"] == pytest.approx(expected)


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
