"""Tests for :func:`utilities.command.help_utils.process_adapter_commands`."""

import os
import sys
import types

sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # noqa: E402

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


# ``utilities`` is importable when ``pytest`` is run from the repository root.
from scanner_controller.utilities.command.help_utils import process_adapter_commands  # noqa: E402


class DummyCmd:
    """Simple command object used for grouping tests."""

    def __init__(self, module=None):
        """Store the originating module name, if provided."""
        self.source_module = module


class DummyAdapter:
    """Adapter with a basic command mapping for tests."""

    def __init__(self):
        """Initialize with a couple of dummy commands."""
        self.commands = {
            "foo": DummyCmd("foo_commands"),
            "bar": DummyCmd(),
            "get volume": DummyCmd("volume_commands"),
        }


def test_process_adapter_commands_basic():
    """Verify command categorization based on module presence."""
    general = {"Get Commands": ["get volume"]}
    categories, groups = process_adapter_commands(DummyAdapter(), general)

    assert "Foo" in categories
    assert "Other" in categories
    assert groups == {"Foo": ["foo"], "Other": ["bar"]}
    assert "Volume" not in groups
