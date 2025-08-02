"""Tests for :mod:`utilities.scanner.band_scope_logger`."""

import os
import sys
import csv
import json
import sqlite3
import types

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

from utilities.scanner.band_scope_logger import (  # noqa: E402
    FREQ_FIELD,
    record_band_scope,
)


RECORDS = [(10.0, 0.1), (20.0, 0.2)]
SUMMARY = "test summary"


def test_csv_field_name(tmp_path):
    """CSV output uses the expected frequency field name."""
    out = tmp_path / "out.csv"
    record_band_scope(RECORDS, SUMMARY, "csv", out)
    with open(out) as fh:
        reader = csv.DictReader(fh)
        assert reader.fieldnames == [FREQ_FIELD, "rssi"]
        rows = [row for row in reader if row["rssi"]]
    assert len(rows) == len(RECORDS)
    assert float(rows[0][FREQ_FIELD]) == RECORDS[0][0]


def test_json_field_name(tmp_path):
    """JSON output uses the expected frequency field name."""
    out = tmp_path / "out.json"
    record_band_scope(RECORDS, SUMMARY, "json", out)
    with open(out) as fh:
        data = json.load(fh)
    assert FREQ_FIELD in data["records"][0]
    assert data["records"][0][FREQ_FIELD] == RECORDS[0][0]


def test_db_field_name(tmp_path):
    """Verify SQLite output uses the expected frequency field name."""
    out = tmp_path / "out.db"
    record_band_scope(RECORDS, SUMMARY, "db", out)
    conn = sqlite3.connect(out)
    cur = conn.cursor()
    cur.execute("PRAGMA table_info(band_scope)")
    cols = [info[1] for info in cur.fetchall()]
    assert FREQ_FIELD in cols
    cur.execute(f"SELECT {FREQ_FIELD}, rssi FROM band_scope")
    rows = cur.fetchall()
    conn.close()
    assert len(rows) == len(RECORDS)
    assert rows[0][0] == RECORDS[0][0]
