import os
import sys
import types

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Provide minimal serial stubs so the factory modules import cleanly
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

from utilities.scanner.factory import get_scanner_adapter  # noqa: E402
from utilities.core.adapter_factory import create_adapter  # noqa: E402


def test_uniden_prefix_returns_generic_adapter():
    adapter = get_scanner_adapter("SDS100")
    assert adapter.__class__.__name__ == "GenericUnidenAdapter"


def test_cli_factory_generic_uniden(monkeypatch):
    adapter = create_adapter("sds200", machine_mode=True)
    assert adapter.__class__.__name__ == "GenericUnidenAdapter"
