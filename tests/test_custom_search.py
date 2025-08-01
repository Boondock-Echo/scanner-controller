"""Tests for custom search data streaming."""

import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
sys.modules.setdefault("serial", serial_stub)

from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402
from utilities.core.command_registry import build_command_table  # noqa: E402


def test_band_scope_command_registered(monkeypatch):
    adapter = BCD325P2Adapter()
    counts = []

    def fake_stream(ser, c=1024, debug=False):
        counts.append(c)
        for i in range(int(c)):
            yield (0, 100.0 + i % 5, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", fake_stream)
    adapter.band_scope_width = 5

    commands, help_text = build_command_table(adapter, None)

    assert "band scope" in commands
    assert "band scope" in help_text
    output = commands["band scope"](None, adapter, "10 hits")
    lines = output.splitlines()
    assert len(lines) == 1
    assert lines[0].startswith("center=")
    assert counts[0] == adapter.band_scope_width * 10


def test_band_scope_collects(monkeypatch):
    adapter = BCD325P2Adapter()
    data_lines = ["CSC,10,01620000,1", "CSC,11,01630000,0", "CSC,OK"]

    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd, delay=0: "")

    from adapters.uniden.bcd325p2 import custom_search as cs

    monkeypatch.setattr(cs, "send_command", lambda ser, cmd, delay=0: "")
    monkeypatch.setattr(
        cs, "wait_for_data", lambda ser, max_wait=0.5: bool(data_lines)
    )
    monkeypatch.setattr(
        cs, "read_response", lambda ser, timeout=1.0: data_lines.pop(0)
    )

    results = list(adapter.stream_custom_search(None, 2))

    assert results == [(10, 162.0, 1), (11, 163.0, 0)]
