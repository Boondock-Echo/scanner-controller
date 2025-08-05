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

from scanner_controller.adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402
from scanner_controller.utilities.core.command_registry import build_command_table  # noqa: E402


def test_presets_load():
    presets = importlib.import_module(
        "scanner_controller.config.band_scope_presets"
    ).BAND_SCOPE_PRESETS
    assert "air" in presets
    assert "race" in presets
    assert isinstance(presets["air"], tuple)
    assert len(presets["air"]) == 4


def test_band_select_air_command(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: "OK")
    # Disable BSP validator to avoid preset span restrictions
    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)

    commands, _ = build_command_table(adapter, None)
    result = commands["band select"](None, adapter, "air")
    assert result == "OK"


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


def test_custom_search_parses_short_frequency(monkeypatch):
    adapter = BCD325P2Adapter()

    data_lines = ["CSC,10,250200,1", "CSC,OK"]

    from scanner_controller.adapters.uniden.bcd325p2 import custom_search as cs

    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd, delay=0: "")
    monkeypatch.setattr(cs, "send_command", lambda ser, cmd, delay=0: "")
    monkeypatch.setattr(
        cs, "wait_for_data", lambda ser, max_wait=0.5: bool(data_lines)
    )
    monkeypatch.setattr(
        cs, "read_response", lambda ser, timeout=1.0: data_lines.pop(0)
    )

    results = list(adapter.stream_custom_search(None, 1))

    assert results == [(10, 25.02, 1)]


def test_band_scope_auto_width(monkeypatch):
    adapter = BCD325P2Adapter()

    monkeypatch.setattr(adapter, "write_frequency", lambda ser, f: None)
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    adapter.sweep_band_scope(None, "146M", "2M", "0.5M", "0.5M")
    assert adapter.band_scope_width == 5

    counts = []

    def fake_stream(ser, c=5, debug=False):
        counts.append(c)
        for i in range(c):
            yield (0, 145.0 + 0.5 * i, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", fake_stream)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "5 hits")
    lines = output.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("center=")
    assert counts[0] == adapter.band_scope_width * 5


def test_configure_band_scope_wraps_programming(monkeypatch):
    adapter = BCD325P2Adapter()
    calls = []

    def send_command_stub(ser, cmd):
        calls.append(cmd)
        return "OK"

    monkeypatch.setattr(adapter, "send_command", send_command_stub)
    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)
    monkeypatch.setattr(adapter.commands["CSP"], "validator", None)
    monkeypatch.setattr(adapter.commands["CSG"], "validator", None)
    monkeypatch.setattr(
        adapter, "start_scanning", lambda ser: calls.append("START")
    )

    result = adapter.configure_band_scope(None, "air")

    assert calls[0] == "PRG"
    assert calls[1].startswith("BSP")
    assert calls[2].startswith("CSP")
    assert calls[3] == "CSG,0111111111"
    assert calls[4] == "EPG"
    assert calls[-1] == "START"
    assert result == "OK"


def test_configure_band_scope_csp_format(monkeypatch):
    adapter = BCD325P2Adapter()
    calls = []

    def send_command_stub(ser, cmd):
        calls.append(cmd)
        return "OK"

    monkeypatch.setattr(adapter, "send_command", send_command_stub)
    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)
    monkeypatch.setattr(adapter.commands["CSP"], "validator", None)
    monkeypatch.setattr(adapter.commands["CSG"], "validator", None)
    monkeypatch.setattr(adapter, "start_scanning", lambda ser: None)

    adapter.configure_band_scope(None, "air")

    csp_cmd = next(cmd for cmd in calls if cmd.startswith("CSP"))
    assert ",1080000," in csp_cmd
    assert ",1360000," in csp_cmd
    assert ",833," in csp_cmd


def test_configure_band_scope_sets_width(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True

    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: "OK")
    monkeypatch.setattr(adapter, "start_scanning", lambda ser: None)

    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)

    result = adapter.configure_band_scope(None, "air")
    assert adapter.band_scope_width == 4803
    assert result == "OK"

    adapter.in_program_mode = False

    def fake_stream(ser, c=adapter.band_scope_width, debug=False):
        for i in range(c):
            yield (0, 100.0 + i, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", fake_stream)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "5 hits")
    lines = output.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("center=")


def test_band_scope_no_data(monkeypatch):
    adapter = BCD325P2Adapter()

    def empty_stream(ser, c=5, debug=False):
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

    counts = []

    def stream_stub(ser, c=3, debug=False):
        counts.append(c)
        yield (10, 145.0, 0)
        yield (20, 146.0, 0)
        yield (30, 147.0, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, _ = build_command_table(adapter, None)
    output = commands["band scope"](None, adapter, "3")
    lines = output.splitlines()
    assert lines[:3] == [
        "145.0000, 0.010",
        "146.0000, 0.020",
        "147.0000, 0.029",
    ]
    assert lines[-1].startswith("center=")
    assert "min=145.000" in lines[-1]
    assert "max=147.000" in lines[-1]
    assert "span=2M" in lines[-1]
    assert "step=500k" in lines[-1]
    assert "mod=FM" in lines[-1]
    assert counts[0] == adapter.band_scope_width * 3


def test_band_scope_in_program_mode(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True

    called = []

    def stream_stub(ser, c=3, debug=False):
        called.append(True)
        yield (10, 145.0, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, _ = build_command_table(adapter, None)
    result = commands["band scope"](None, adapter, "3")

    assert (
        result
        == "Scanner is in programming mode. Run 'send EPG' then rerun 'band scope'."
    )
    assert not called


def test_band_scope_modes(monkeypatch):
    adapter = BCD325P2Adapter()

    counts = []

    def stream_stub(ser, c=1024, debug=False):
        counts.append(c)
        yield (0, 145.0, 0)
        yield (50, 146.0, 1)
        yield (0, 147.0, 0)
        yield (30, 148.0, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, _ = build_command_table(adapter, None)

    # Default (list) mode
    output_default = commands["band scope"](None, adapter, "")
    output_list = commands["band scope"](None, adapter, "list")
    lines_default = output_default.splitlines()
    assert lines_default[:4] == [
        "145.0000, 0.000",
        "146.0000, 0.049",
        "147.0000, 0.000",
        "148.0000, 0.029",
    ]
    assert lines_default[-1].startswith("center=")
    assert output_default == output_list

    # Hits mode filters entries 20% above mean RSSI
    output_hits = commands["band scope"](None, adapter, "hits")
    lines_hits = output_hits.splitlines()
    assert lines_hits[:2] == ["146.0000, 0.049", "148.0000, 0.029"]
    assert lines_hits[-1].startswith("center=")

    assert counts == [1024, 1024, 1024]


def test_band_scope_preset_invocation(monkeypatch):
    adapter = BCD325P2Adapter()

    calls = {}

    def configure_stub(ser, preset):
        calls["preset"] = preset
        adapter.band_scope_width = 5
        return "OK"

    def stream_stub(ser, c, debug=False):
        calls["count"] = c
        yield (10, 100.0, 0)

    monkeypatch.setattr(adapter, "configure_band_scope", configure_stub)
    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, _ = build_command_table(adapter, None)
    commands["band scope"](None, adapter, "air")

    assert calls["preset"] == "air"
    assert calls["count"] == adapter.band_scope_width


def test_band_scope_preset_with_sweeps(monkeypatch):
    adapter = BCD325P2Adapter()

    calls = {}

    def configure_stub(ser, preset):
        calls["preset"] = preset
        adapter.band_scope_width = 5
        return "OK"

    def stream_stub(ser, c, debug=False):
        calls["count"] = c
        yield (10, 144.0, 0)

    monkeypatch.setattr(adapter, "configure_band_scope", configure_stub)
    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, _ = build_command_table(adapter, None)
    commands["band scope"](None, adapter, "ham2m 2")

    assert calls["preset"] == "ham2m"
    assert calls["count"] == adapter.band_scope_width * 2


def test_band_scope_accepts_non_exact_ok_response(monkeypatch):
    adapter = BCD325P2Adapter()

    calls = {"stream": 0}

    def configure_stub(ser, preset):
        adapter.band_scope_width = 5
        return "BSP,OK"

    def stream_stub(ser, c, debug=False):
        calls["stream"] += 1
        yield (10, 100.0, 0)

    monkeypatch.setattr(adapter, "configure_band_scope", configure_stub)
    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, _ = build_command_table(adapter, None)
    commands["band scope"](None, adapter, "air")

    assert calls["stream"] == 1


def test_band_scope_respects_preset_range(monkeypatch):
    adapter = BCD325P2Adapter()
    adapter.in_program_mode = True
    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd: "OK")
    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)
    monkeypatch.setattr(adapter, "start_scanning", lambda ser: None)

    commands, _ = build_command_table(adapter, None)
    commands["band select"](None, adapter, "ham2m")
    adapter.in_program_mode = False

    def stream_stub(ser, c=1024, debug=False):
        SIGNAL_LOW = 10  # Low signal strength
        SIGNAL_MEDIUM = 20  # Medium signal strength
        SIGNAL_HIGH = 30  # High signal strength

        yield (SIGNAL_LOW, 144.0, 0)
        yield (SIGNAL_MEDIUM, 146.0, 0)
        yield (SIGNAL_HIGH, 148.0, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    output = commands["band scope"](None, adapter, "list")
    lines = output.splitlines()
    hits = [float(h.split(",")[0]) for h in lines[:-1]]
    assert all(144.0 <= f <= 148.0 for f in hits)
    assert "min=144.000" in lines[-1]
    assert "max=148.000" in lines[-1]


def test_configure_band_scope_reports_errors(monkeypatch):
    adapter = BCD325P2Adapter()

    def send_command_stub(ser, cmd):
        if cmd.startswith("CSP"):
            return "ERR"
        return "OK"

    monkeypatch.setattr(adapter, "send_command", send_command_stub)
    monkeypatch.setattr(adapter.commands["BSP"], "validator", None)
    monkeypatch.setattr(adapter, "start_scanning", lambda ser: None)

    result = adapter.configure_band_scope(None, "air")
    assert result.startswith("CSP error")
