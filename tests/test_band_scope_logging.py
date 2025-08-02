"""Tests for band scope logging options."""

import os
import sys
import types
import csv
import json
import sqlite3

# Ensure project root is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Provide minimal serial stub so scanner utilities import without pyserial
serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
serial_tools_stub = types.ModuleType("serial.tools")
list_ports_stub = types.ModuleType("serial.tools.list_ports")
serial_tools_stub.list_ports = list_ports_stub
serial_stub.tools = serial_tools_stub
sys.modules.setdefault("serial", serial_stub)
sys.modules.setdefault("serial.tools", serial_tools_stub)
sys.modules.setdefault("serial.tools.list_ports", list_ports_stub)

from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # noqa: E402
from utilities.core.command_registry import build_command_table  # noqa: E402


def _setup_commands(monkeypatch):
    """Create adapter with deterministic stream and build command table."""
    adapter = BCD325P2Adapter()

    def stream_stub(ser, count=1024, debug=False):
        for i in range(3):
            yield (10 + i, 100.0 + i, 0)

    monkeypatch.setattr(adapter, "stream_custom_search", stream_stub)
    commands, _ = build_command_table(adapter, None)
    return commands, adapter


def test_log_csv(tmp_path, monkeypatch):
    commands, adapter = _setup_commands(monkeypatch)
    out_file = tmp_path / "data.csv"

    result = commands["band scope"](None, adapter, f"log csv {out_file}")

    assert result == str(out_file)
    assert out_file.exists()

    with open(out_file) as fh:
        reader = csv.DictReader(fh)
        rows = [row for row in reader if row["rssi"]]
    assert len(rows) == 3


def test_log_json(tmp_path, monkeypatch):
    commands, adapter = _setup_commands(monkeypatch)
    out_file = tmp_path / "data.json"

    result = commands["band scope"](None, adapter, f"log json {out_file}")

    assert result == str(out_file)
    assert out_file.exists()

    with open(out_file) as fh:
        data = json.load(fh)
    assert len(data["records"]) == 3


def test_log_db(tmp_path, monkeypatch):
    commands, adapter = _setup_commands(monkeypatch)
    out_file = tmp_path / "data.db"

    result = commands["band scope"](None, adapter, f"log db {out_file}")

    assert result == str(out_file)
    assert out_file.exists()

    conn = sqlite3.connect(out_file)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM band_scope")
    (count,) = cur.fetchone()
    conn.close()

    assert count == 3
