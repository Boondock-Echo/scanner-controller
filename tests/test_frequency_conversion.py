import types
import sys
import pytest

# Stub serial module before importing adapters
serial_stub = types.ModuleType("serial")
serial_stub.Serial = lambda *a, **k: None
sys.modules.setdefault("serial", serial_stub)

from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter
from adapters.uniden.bc125at_adapter import BC125ATAdapter

@pytest.mark.parametrize("adapter_cls", [BCD325P2Adapter, BC125ATAdapter])
def test_numeric_conversion(adapter_cls):
    adapter = adapter_cls()
    assert adapter._to_mhz("833") == pytest.approx(0.00833)
    assert adapter._to_mhz("01440000") == pytest.approx(144.0)
    assert adapter._to_khz("833") == pytest.approx(8.33)
    assert adapter._to_khz("01440000") == pytest.approx(144000.0)
