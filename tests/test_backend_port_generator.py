import sys
import types

# Provide a minimal serial module so backend can be imported without pyserial
serial_stub = types.SimpleNamespace()
serial_stub.Serial = object
serial_stub.tools = types.SimpleNamespace(list_ports=types.SimpleNamespace(comports=lambda: []))
sys.modules.setdefault("serial", serial_stub)
sys.modules.setdefault("serial.tools", serial_stub.tools)
sys.modules.setdefault("serial.tools.list_ports", serial_stub.tools.list_ports)

from utilities.scanner import backend


class DummySerial:
    def __init__(self, port, *args, **kwargs):
        self.port = port
        self.in_waiting = 1

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def write(self, data):
        self.last_write = data

    def reset_input_buffer(self):
        pass


def test_find_all_scanner_ports_handles_generator(monkeypatch):
    """find_all_scanner_ports should handle generator returned by comports."""

    # Patch serial.Serial
    monkeypatch.setattr(backend.serial, "Serial", DummySerial, raising=False)
    monkeypatch.setattr(backend, "hid", None)

    # Patch wait_for_data and read_response to simulate a scanner replying
    monkeypatch.setattr(backend, "wait_for_data", lambda ser, max_wait=0.3: True)
    monkeypatch.setattr(backend, "read_response", lambda ser, timeout=1.0: "MDL,MOCK")

    # Prepare a generator for comports
    def fake_comports():
        yield types.SimpleNamespace(device="/dev/ttyUSB0", description="Mock Port")

    monkeypatch.setattr(backend.list_ports, "comports", fake_comports)

    detected = backend.find_all_scanner_ports()
    assert detected == [("/dev/ttyUSB0", "MOCK")]


def test_find_all_scanner_ports_hid(monkeypatch):
    """find_all_scanner_ports should detect HID devices when no serial ports found."""

    monkeypatch.setattr(backend.list_ports, "comports", lambda: [])
    monkeypatch.setattr(backend.time, "sleep", lambda *a, **k: None)

    class DummyHID:
        def open_path(self, path):
            self.path = path

        def write(self, data):
            self.last_write = data

        def read(self, size, timeout=500):
            return list(b"MDL,MOCK")

        def close(self):
            pass

    class DummyHIDModule:
        def device(self):
            return DummyHID()

    monkeypatch.setattr(backend, "hid", DummyHIDModule())
    monkeypatch.setattr(backend.glob, "glob", lambda pattern: ["/dev/usb/hiddev0"])

    detected = backend.find_all_scanner_ports(max_retries=1)
    assert detected == [("/dev/usb/hiddev0", "MOCK")]
