"""Tests for close_call_logger.record_close_calls."""

import os
import sqlite3
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
from utilities.scanner.close_call_logger import record_close_calls  # noqa: E402


class DummyAdapter:
    def __init__(self):
        self.mask = None
        self.lof_sent = None

    def set_close_call(self, ser, params):
        self.mask = params

    def jump_mode(self, ser, mode):
        self.jumped = mode

    def read_frequency(self, ser):
        raise NotImplementedError

    def read_rssi(self, ser):
        return 0.5

    def send_command(self, ser, cmd):
        self.lof_sent = cmd


def test_band_mask_and_db_write(tmp_path, monkeypatch):
    adapter = DummyAdapter()
    db = tmp_path / "cc.db"

    calls = [130.0]

    def freq_stub(ser):
        return calls.pop(0)

    monkeypatch.setattr(adapter, "read_frequency", freq_stub)

    record_close_calls(adapter, None, "air", db_path=str(db), max_records=1)

    assert adapter.mask == CLOSE_CALL_BANDS["air"]

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM close_calls").fetchone()[0]
    conn.close()
    assert count == 1


def test_lockout_sends_lof(tmp_path, monkeypatch):
    adapter = DummyAdapter()
    db = tmp_path / "cc.db"

    calls = [162.5]

    def freq_stub(ser):
        return calls.pop(0)

    monkeypatch.setattr(adapter, "read_frequency", freq_stub)

    record_close_calls(
        adapter, None, "air", db_path=str(db), lockout=True, max_records=1
    )

    assert adapter.lof_sent == "LOF,162.5"


def test_max_time_limits_logging(tmp_path, monkeypatch):
    adapter = DummyAdapter()
    db = tmp_path / "cc.db"

    calls = [130.0, 131.0, 132.0]

    def freq_stub(ser):
        return calls.pop(0)

    monkeypatch.setattr(adapter, "read_frequency", freq_stub)

    t = {"i": 0}

    def time_stub():
        t["i"] += 0.05
        return t["i"]

    monkeypatch.setattr(time, "time", time_stub)

    record_close_calls(adapter, None, "air", db_path=str(db), max_time=0.25)

    conn = sqlite3.connect(db)
    count = conn.execute("SELECT COUNT(*) FROM close_calls").fetchone()[0]
    conn.close()
    assert count == 2
