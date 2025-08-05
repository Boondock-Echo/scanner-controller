"""Tests for close_call_search."""

import io
import os
import sys
import time
import types
import pytest

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

from scanner_controller.config.close_call_bands import CLOSE_CALL_BANDS  # noqa: E402
from scanner_controller.utilities.scanner.close_call_search import close_call_search  # noqa: E402


class DummyAdapter:
    def __init__(self):
        self.set_calls = []
        self.jump_calls = []
        self.commands = []
        self.scanned = False

    def get_close_call(self, ser):
        return "ORIG"

    def set_close_call(self, ser, params):
        self.set_calls.append(params)

    def jump_mode(self, ser, mode):
        self.jump_calls.append(mode)
        if mode == "":
            return "SCN_MODE"

    def start_scanning(self, ser):
        self.scanned = True

    def read_frequency(self, ser):
        raise NotImplementedError

    def read_rssi(self, ser):
        return 0.5

    def send_command(self, ser, cmd):
        self.commands.append(cmd)


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
    assert adapter.set_calls == [CLOSE_CALL_BANDS["air"], "ORIG"]
    assert adapter.jump_calls == ["", "CC_MODE"]
    assert adapter.scanned


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
        adapter, None, "air", max_hits=5, input_stream=input_stream, lockout=True
    )

    assert len(hits) == 1
    assert not completed
    assert adapter.commands == ["LOF,130.0", "ULF,130.0"]


def test_lockout_unlocks(monkeypatch):
    adapter = DummyAdapter()
    calls = [130.0, 131.0]

    def freq_stub(ser):
        return calls.pop(0)

    monkeypatch.setattr(adapter, "read_frequency", freq_stub)

    close_call_search(adapter, None, "air", max_hits=2, lockout=True, input_stream=io.StringIO(""))

    assert adapter.commands == ["LOF,130.0", "LOF,131.0", "ULF,130.0", "ULF,131.0"]


def test_out_of_range_hit(monkeypatch):
    adapter = DummyAdapter()
    calls = [105.0, 130.0]

    def freq_stub(ser):
        return calls.pop(0)

    monkeypatch.setattr(adapter, "read_frequency", freq_stub)

    hits, completed = close_call_search(
        adapter, None, "air", max_hits=1, input_stream=io.StringIO("")
    )

    assert [h[1] for h in hits] == [130.0]
    assert completed
    assert adapter.commands == ["LOF,105.0", "ULF,105.0"]


@pytest.mark.parametrize("key", ["q", "\r"])
def test_user_cancel_windows(monkeypatch, key):
    adapter = DummyAdapter()
    calls = [130.0, 131.0]

    def freq_stub(ser):
        return calls.pop(0)

    monkeypatch.setattr(adapter, "read_frequency", freq_stub)

    class MSVCRTStub:
        def __init__(self, key):
            self.key = key
            self.count = 0

        def kbhit(self):
            self.count += 1
            if self.count == 1:
                return False
            return True

        def getwch(self):
            return self.key

    monkeypatch.setattr(sys, "platform", "win32")
    msvcrt_stub = MSVCRTStub(key)
    module = types.ModuleType("msvcrt")
    module.kbhit = msvcrt_stub.kbhit
    module.getwch = msvcrt_stub.getwch
    monkeypatch.setitem(sys.modules, "msvcrt", module)

    hits, completed = close_call_search(
        adapter, None, "air", max_hits=5, input_stream=io.StringIO("")
    )

    assert len(hits) == 1
    assert not completed
