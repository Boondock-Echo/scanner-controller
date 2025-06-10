import os
import sys
import types
import re

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
sys.modules.setdefault("serial", serial_stub)

from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402
from utilities.core.command_registry import build_command_table  # noqa: E402


def test_band_sweep_registered_and_output(monkeypatch, capsys):
    adapter = BCD325P2Adapter()

    data = [
        (512, 162.55, 1),
        (256, 163.55, 0),
    ]

    def fake_stream(ser, count=1024):
        for rssi, freq, sql in data[:count]:
            yield rssi, freq, sql

    monkeypatch.setattr(adapter, "stream_custom_search", fake_stream)

    commands, help_text = build_command_table(adapter, None)

    assert "band sweep" in commands
    assert "band sweep" in help_text

    commands["band sweep"](None, adapter, "2")
    out_lines = capsys.readouterr().out.strip().splitlines()

    assert len(out_lines) == 2
    for line in out_lines:
        assert re.match(r"^[0-9]+\.\d{4}, [01]\.\d{3}$", line)
