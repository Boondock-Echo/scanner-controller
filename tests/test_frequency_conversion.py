"""Tests for frequency conversion helper methods."""

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


@pytest.mark.parametrize(
    "band,low,high",
    [
        ("air", 108.0, 136.0),
        ("race", 455.0, 465.0),
        ("marine", 156.0, 162.0),
        ("railroad", 159.5, 161.5),
        ("ham2m", 144.0, 148.0),
        ("ham70cm", 420.0, 450.0),
        ("weather", 162.4, 162.55),
        ("cb", 26.965, 27.405),
        ("frs", 462.5625, 467.7125),
        ("public_safety", 150.0, 174.0),
        ("mil_air", 225.0, 400.0),
    ],
)
@pytest.mark.parametrize("adapter_cls", [BCD325P2Adapter, BC125ATAdapter])
def test_preset_to_mhz(adapter_cls, band, low, high):
    adapter = adapter_cls()
    from config.band_scope_presets import BAND_SCOPE_PRESETS

    low_str, high_str, _, _ = BAND_SCOPE_PRESETS[band]
    assert adapter._to_mhz(low_str) == pytest.approx(low)
    assert adapter._to_mhz(high_str) == pytest.approx(high)
