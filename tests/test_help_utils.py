"""Tests for :func:`utilities.command.help_utils.process_adapter_commands`."""

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import types

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


from utilities.command.help_utils import process_adapter_commands


class DummyCmd:
    def __init__(self, module=None):
        self.source_module = module


class DummyAdapter:
    def __init__(self):
        self.commands = {
            "foo": DummyCmd("foo_commands"),
            "bar": DummyCmd(),
            "get volume": DummyCmd("volume_commands"),
        }


def test_process_adapter_commands_basic():
    general = {"Get Commands": ["get volume"]}
    categories, groups = process_adapter_commands(DummyAdapter(), general)

    assert "Foo" in categories
    assert "Other" in categories
    assert groups == {"Foo": ["foo"], "Other": ["bar"]}
    assert "Volume" not in groups
