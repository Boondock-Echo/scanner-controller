"""Tests for BC125AT band scope CLI command."""

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


def test_bc125at_band_scope_cli(monkeypatch):
    adapter = BC125ATAdapter()
    calls = []

    def configure_stub(ser, preset):
        calls.append(("configure", preset))
        adapter.band_scope_width = 1
        adapter.last_center = 145.0
        adapter.last_span = 1.0
        adapter.last_step = 0.5
        adapter.last_mod = "FM"
        return "OK"

    def stream_stub(ser, count, debug=False):
        calls.append(("stream", count))
        yield (10, 145.0, 0)

    monkeypatch.setattr(adapter, "configure_band_scope", configure_stub)
    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)

    commands, help_text = build_command_table(adapter, None)

    assert "band scope" in commands
    assert "band scope" in help_text

    output = commands["band scope"](None, adapter, "air")
    lines = output.splitlines()

    assert calls[0] == ("configure", "air")
    assert calls[1] == ("stream", adapter.band_scope_width)
    assert lines[0] == "145.0000, 0.010"
    assert (
        lines[1]
        == "center=145.000 min=145.000 max=145.000 span=1M step=500k mod=FM"
    )
