"""Tests for band_scope_logger.record_band_scope directory creation."""

import os
import sys
import types

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
serial_tools_stub = types.ModuleType("serial.tools")
list_ports_stub = types.ModuleType("serial.tools.list_ports")
serial_tools_stub.list_ports = list_ports_stub
serial_stub.tools = serial_tools_stub
sys.modules.setdefault("serial", serial_stub)
sys.modules.setdefault("serial.tools", serial_tools_stub)
sys.modules.setdefault("serial.tools.list_ports", list_ports_stub)

from utilities.scanner.band_scope_logger import record_band_scope  # noqa: E402


def test_record_band_scope_creates_nested_path(tmp_path):
    """record_band_scope creates missing parent directories."""
    out_file = tmp_path / "nested" / "scope" / "data.csv"
    record_band_scope([(100.0, 0.5)], "summary", "csv", str(out_file))
    assert out_file.exists()
