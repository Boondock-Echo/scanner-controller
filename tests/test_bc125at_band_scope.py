import os
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
sys.modules.setdefault("serial", serial_stub)
sys.modules.setdefault("serial.tools", serial_tools_stub)
sys.modules.setdefault("serial.tools.list_ports", list_ports_stub)

from adapters.uniden.bc125at_adapter import BC125ATAdapter  # noqa: E402


def test_bc125at_sweep_parses_units(monkeypatch):
    adapter = BC125ATAdapter()
    monkeypatch.setattr(adapter, "enter_quick_frequency_hold", lambda ser, f: None)
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    result = adapter.sweep_band_scope(None, "144M", "2M", "500k", "500k")
    assert result[0][0] == 143.0


def test_bc125at_band_scope_auto_width(monkeypatch):
    adapter = BC125ATAdapter()
    monkeypatch.setattr(adapter, "enter_quick_frequency_hold", lambda ser, f: None)
    monkeypatch.setattr(adapter, "read_rssi", lambda ser: 0)
    adapter.sweep_band_scope(None, "146M", "2M", "0.5M", "0.5M")
    assert adapter.band_scope_width == 5
