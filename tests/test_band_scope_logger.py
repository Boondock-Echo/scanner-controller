"""Tests for band_scope_logger.record_band_scope."""

import json
import os
import sqlite3
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
sys.modules.setdefault("serial.tools", serial_tools_stub)
sys.modules.setdefault("serial.tools.list_ports", list_ports_stub)
sys.modules.setdefault("serial", serial_stub)

from utilities.scanner.band_scope_logger import record_band_scope  # noqa: E402


class DummyAdapter:
    """Simple adapter stub used for testing."""

    def __init__(self):
        """Store call history and band scope width."""
        self.configure_calls = []
        self.stream_calls = []
        self.band_scope_width = 5

    def configure_band_scope(self, ser, preset):
        """Record invocation of the configuration routine."""
        self.configure_calls.append(preset)
        return "OK"

    def stream_custom_search(self, ser, count, debug=False):
        """Yield ``count`` sequential test records."""
        self.stream_calls.append(count)
        for i in range(count):
            yield (i, 100.0 + i, 0)


def test_record_band_scope_csv(tmp_path):
    """CSV output contains all expected lines."""
    adapter = DummyAdapter()
    base = tmp_path / "scope"
    record_band_scope(
        adapter, None, "air", sweeps=2, format="csv", path=str(base)
    )
    assert adapter.configure_calls == ["air"]
    assert adapter.stream_calls == [10]
    csv_file = base.with_suffix(".csv")
    lines = csv_file.read_text().strip().splitlines()
    assert lines[0] == "rssi,freq"
    assert len(lines) == 11
    assert lines[1] == "0,100.0"


def test_record_band_scope_json(tmp_path):
    """JSON output serializes records as objects."""
    adapter = DummyAdapter()
    base = tmp_path / "scope"
    record_band_scope(
        adapter, None, "air", sweeps=1, format="json", path=str(base)
    )
    json_file = base.with_suffix(".json")
    data = json.loads(json_file.read_text())
    assert len(data) == 5
    assert data[0] == {"rssi": 0, "freq": 100.0}


def test_record_band_scope_sqlite(tmp_path):
    """SQLite output persists rows to the database."""  # noqa: D403
    adapter = DummyAdapter()
    base = tmp_path / "scope"
    record_band_scope(
        adapter, None, "air", sweeps=1, format="sqlite", path=str(base)
    )
    db_file = base.with_suffix(".db")
    conn = sqlite3.connect(db_file)
    rows = conn.execute("SELECT rssi, frequency FROM band_scope").fetchall()
    conn.close()
    assert len(rows) == 5
    assert rows[0] == (0, 100.0)
