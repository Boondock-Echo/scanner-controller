import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
sys.modules.setdefault("serial", serial_stub)

from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402
from utilities.core.command_registry import build_command_table  # noqa: E402


def test_custom_search_command_registered(monkeypatch):
    adapter = BCD325P2Adapter()
    monkeypatch.setattr(adapter, "stream_custom_search", lambda ser, c=1024: [()])

    commands, help_text = build_command_table(adapter, None)

    assert "custom search" in commands
    assert "custom search" in help_text
    assert commands["custom search"]("5") == [()]


def test_stream_custom_search_collects(monkeypatch):
    adapter = BCD325P2Adapter()
    data_lines = [
        "CSC,10,162.0,1",
        "CSC,11,163.0,0",
        "CSC,OK",
    ]

    monkeypatch.setattr(
        adapter,
        "send_command",
        lambda ser, cmd: "",
    )

    from adapters.uniden.bcd325p2 import custom_search as cs

    monkeypatch.setattr(cs, "send_command", lambda ser, cmd: "")
    monkeypatch.setattr(cs, "wait_for_data", lambda ser, max_wait=0.5: bool(data_lines))
    monkeypatch.setattr(cs, "read_response", lambda ser, timeout=1.0: data_lines.pop(0))

    results = adapter.stream_custom_search(None, 2)

    assert results == [(10, 162.0, 1), (11, 163.0, 0)]
