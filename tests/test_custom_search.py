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
    monkeypatch.setattr(
        adapter,
        "stream_custom_search",
        lambda ser, c=1024: [(0, 100.0 + i % 5, 0) for i in range(int(c))],
    )

    commands, help_text = build_command_table(adapter, None)

    assert "band scope" in commands
    assert "band scope" in help_text
    output = commands["band scope"](None, adapter, "10 5")
    lines = output.splitlines()
    assert len(lines) == 2
    assert all(len(line) == 5 for line in lines)


def test_band_scope_collects(monkeypatch):
    adapter = BCD325P2Adapter()
    data_lines = ["CSC,10,162.0,1", "CSC,11,163.0,0", "CSC,OK"]

    monkeypatch.setattr(adapter, "send_command", lambda ser, cmd, delay=0: "")

    from adapters.uniden.bcd325p2 import custom_search as cs

    monkeypatch.setattr(cs, "send_command", lambda ser, cmd, delay=0: "")
    monkeypatch.setattr(
        cs, "wait_for_data", lambda ser, max_wait=0.5: bool(data_lines)
    )
    monkeypatch.setattr(
        cs, "read_response", lambda ser, timeout=1.0: data_lines.pop(0)
    )

    results = adapter.stream_custom_search(None, 2)

    assert results == [(10, 162.0, 1), (11, 163.0, 0)]
