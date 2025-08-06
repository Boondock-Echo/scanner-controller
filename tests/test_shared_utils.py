"""Tests for utilities shared across adapters."""
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

from scanner_controller.utilities.core.serial_utils import read_response


def _install_dummy_sdr_modules(monkeypatch):
    """Install minimal SoapySDR and rtlsdr modules for testing."""

    class DummySoapyDevice:
        @staticmethod
        def enumerate():
            return [{"label": "Mock Soapy"}]

    dummy_soapy = SimpleNamespace(Device=DummySoapyDevice)
    monkeypatch.setitem(sys.modules, "SoapySDR", dummy_soapy)

    class DummyRtlSdr:
        @staticmethod
        def get_devices():
            return ["0: Mock RTL"]

    dummy_rtl = SimpleNamespace(RtlSdr=DummyRtlSdr)
    monkeypatch.setitem(sys.modules, "rtlsdr", dummy_rtl)


def test_read_response_restores_timeout():
    """Ensure read_response restores the original timeout."""
    ser = MagicMock()
    ser.timeout = 5
    ser.read_until.return_value = b"RES\r"

    read_response(ser, timeout=0.1)
    assert ser.timeout == 5


def test_diagnose_connection_issues_lists_sdr_devices(monkeypatch, capsys):
    """Ensure SDR pseudo-ports appear in diagnostic output."""

    _install_dummy_sdr_modules(monkeypatch)
    dummy_list_ports = SimpleNamespace(comports=lambda: [])
    dummy_tools = SimpleNamespace(list_ports=dummy_list_ports)
    dummy_serial = SimpleNamespace(tools=dummy_tools)
    monkeypatch.setitem(sys.modules, "serial", dummy_serial)
    monkeypatch.setitem(sys.modules, "serial.tools", dummy_tools)
    monkeypatch.setitem(sys.modules, "serial.tools.list_ports", dummy_list_ports)
    monkeypatch.setattr("glob.glob", lambda pattern: [])

    from scanner_controller.utilities.core.shared_utils import diagnose_connection_issues

    diagnose_connection_issues()
    captured = capsys.readouterr().out
    assert "SoapySDR: Mock Soapy" in captured
    assert "RTL-SDR: 0: Mock RTL" in captured
