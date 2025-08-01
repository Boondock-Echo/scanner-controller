"""Tests for close_call_search."""

import io
import os
import sys
import time
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
serial_tools_stub = types.ModuleType("serial.tools")
list_ports_stub = types.ModuleType("serial.tools.list_ports")
list_ports_stub.comports = lambda *a, **k: []
serial_tools_stub.list_ports = list_ports_stub
serial_stub.tools = serial_tools_stub
sys.modules.setdefault("serial.tools", serial_tools_stub)
sys.modules.setdefault("serial.tools.list_ports", list_ports_stub)
sys.modules.setdefault("serial", serial_stub)

from config.close_call_bands import CLOSE_CALL_BANDS  # noqa: E402
from utilities.scanner.close_call_search import close_call_search  # noqa: E402


class DummyAdapter:
    def __init__(self):
        self.mask = None
        self.jumped = None

    def set_close_call(self, ser, params):
        self.mask = params

    def jump_mode(self, ser, mode):
        self.jumped = mode

    def read_frequency(self, ser):
        raise NotImplementedError

    def read_rssi(self, ser):
        return 0.5


def test_search_max_hits(monkeypatch):
    adapter = DummyAdapter()
    calls = [130.0, 131.0, 132.0]

    def freq_stub(ser):
        return calls.pop(0)

    monkeypatch.setattr(adapter, "read_frequency", freq_stub)

    hits, completed = close_call_search(
        adapter, None, "air", max_hits=2, input_stream=io.StringIO("")
    )

    assert len(hits) == 2
    assert completed
    assert adapter.mask == CLOSE_CALL_BANDS["air"]


def test_search_max_time(monkeypatch):
    adapter = DummyAdapter()
    calls = [130.0, 131.0, 132.0]

    def freq_stub(ser):
        return calls.pop(0)

    monkeypatch.setattr(adapter, "read_frequency", freq_stub)

    t = {"i": 0}

    def time_stub():
        t["i"] += 0.05
        return t["i"]

    monkeypatch.setattr(time, "time", time_stub)

    hits, completed = close_call_search(
        adapter, None, "air", max_time=0.25, input_stream=io.StringIO("")
    )

    assert len(hits) == 2
    assert completed


class DummyInput:
    def __init__(self, responses):
        self.responses = list(responses)

    def read(self, n=1):
        if self.responses:
            return self.responses.pop(0)
        return ""


def test_search_user_cancel(monkeypatch):
    adapter = DummyAdapter()
    calls = [130.0, 131.0, 132.0]

    def freq_stub(ser):
        return calls.pop(0)

    monkeypatch.setattr(adapter, "read_frequency", freq_stub)

    input_stream = DummyInput(["", "q"])
    hits, completed = close_call_search(
        adapter, None, "air", max_hits=5, input_stream=input_stream
    )

    assert len(hits) == 1
    assert not completed
