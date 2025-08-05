"""Tests for the SDR MultiChannelManager."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import types

# Provide a minimal serial stub for modules that expect it
serial_stub = types.ModuleType("serial")


class DummySerial:
    def __init__(self, *a, **k):
        self.is_open = True

    def close(self):  # pragma: no cover - trivial
        self.is_open = False


serial_stub.Serial = DummySerial
serial_tools_stub = types.ModuleType("serial.tools")
list_ports_stub = types.ModuleType("serial.tools.list_ports")
list_ports_stub.comports = lambda *a, **k: []
serial_tools_stub.list_ports = list_ports_stub
serial_stub.tools = serial_tools_stub
sys.modules["serial.tools"] = serial_tools_stub
sys.modules["serial.tools.list_ports"] = list_ports_stub
sys.modules["serial"] = serial_stub

from scanner_controller.utilities.scanner.connection_manager import ConnectionManager
from scanner_controller.utilities.sdr.multichannel_manager import MultiChannelManager, monitor_frequencies


class DummyAdapter:
    supports_ddc = True

    def __init__(self, machine_mode: bool = False):
        self.machine_mode = machine_mode
        self.freqs = []

    def send_command(self, ser, cmd):
        return cmd

    def write_frequency(self, ser, freq):
        self.freqs.append(freq)
        return freq

    def read_frequency(self, ser):
        return self.freqs[-1] if self.freqs else 0.0

    def read_volume(self, ser):
        return 0

    def write_volume(self, ser, value):
        return value

    def read_squelch(self, ser):
        return 0

    def write_squelch(self, ser, value):
        return value


def test_monitor_frequencies_registers_virtual_connections():
    adapter = DummyAdapter()
    cm = ConnectionManager()
    manager = MultiChannelManager(adapter)
    conn_ids = manager.monitor_frequencies([100.0, 200.0], cm)
    assert len(conn_ids) == 2
    # Both channels should share the same adapter when supports_ddc is True
    assert cm.get(conn_ids[0])[1] is adapter
    assert cm.get(conn_ids[1])[1] is adapter
    assert cm._hardware_refs[adapter] == 2
    cm.close_connection(conn_ids[0])
    assert adapter in cm._hardware_refs
    cm.close_connection(conn_ids[1])
    assert adapter not in cm._hardware_refs


def test_monitor_frequencies_spawns_new_adapters():
    class NoDDCAdapter(DummyAdapter):
        supports_ddc = False

    adapter = NoDDCAdapter()
    cm = ConnectionManager()
    manager = MultiChannelManager(adapter)
    conn_ids = manager.monitor_frequencies([50.0, 75.0], cm)
    assert len(conn_ids) == 2
    first_adapter = cm.get(conn_ids[0])[1]
    second_adapter = cm.get(conn_ids[1])[1]
    assert first_adapter is not second_adapter
    assert cm._hardware_refs[first_adapter] == 1
    assert cm._hardware_refs[second_adapter] == 1


def test_top_level_helper_uses_provided_adapter():
    adapter = DummyAdapter()
    cm = ConnectionManager()
    ids = monitor_frequencies([10.0], adapter=adapter, connection_manager=cm)
    assert ids and cm.get(ids[0])[1] is adapter
