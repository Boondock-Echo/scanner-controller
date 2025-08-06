import importlib
import os
import sys
import types
import builtins

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _create_soapy_module():
    module = types.ModuleType("SoapySDR")

    class Device:
        def __init__(self, args):
            self.freq = 0.0
            self.gain = 0.0

        def getFrequency(self, direction, channel):  # pragma: no cover - simple
            return self.freq

        def setFrequency(self, direction, channel, freq):  # pragma: no cover - simple
            self.freq = freq

        def getGain(self, direction, channel):  # pragma: no cover - simple
            return self.gain

        def setGain(self, direction, channel, gain):  # pragma: no cover - simple
            self.gain = gain

    module.Device = Device
    module.SOAPY_SDR_RX = 0
    return module


def _create_pyrtlsdr_module():
    module = types.ModuleType("pyrtlsdr")

    class RtlSdr:
        def __init__(self, **kwargs):
            self.center_freq = 0.0
            self.gain = 0.0

    module.RtlSdr = RtlSdr
    return module


def test_rtlsdr_adapter_soapy(monkeypatch):
    fake_soapy = _create_soapy_module()
    monkeypatch.setitem(sys.modules, "SoapySDR", fake_soapy)
    monkeypatch.delitem(sys.modules, "pyrtlsdr", raising=False)
    monkeypatch.delitem(
        sys.modules, "scanner_controller.adapters.sdr.rtlsdr_adapter", raising=False
    )
    module = importlib.import_module("scanner_controller.adapters.sdr.rtlsdr_adapter")
    adapter = module.RTLSDRAdapter()
    assert adapter.write_frequency(None, 123.0) == 123.0
    assert adapter.read_frequency() == 123.0
    assert adapter.write_volume(None, 10.0) == 10.0
    assert adapter.read_volume() == 10.0


def test_rtlsdr_adapter_pyrtlsdr(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == "SoapySDR":
            raise ImportError
        return real_import(name, globals, locals, fromlist, level)

    monkeypatch.setattr(builtins, "__import__", fake_import)
    fake_pyrtlsdr = _create_pyrtlsdr_module()
    monkeypatch.setitem(sys.modules, "pyrtlsdr", fake_pyrtlsdr)
    monkeypatch.delitem(
        sys.modules, "scanner_controller.adapters.sdr.rtlsdr_adapter", raising=False
    )
    module = importlib.import_module("scanner_controller.adapters.sdr.rtlsdr_adapter")
    adapter = module.RTLSDRAdapter()
    assert adapter.write_frequency(None, 456.0) == 456.0
    assert adapter.read_frequency() == 456.0
    assert adapter.write_volume(None, 20.0) == 20.0
    assert adapter.read_volume() == 20.0
