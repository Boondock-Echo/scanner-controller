import types

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

    # Patch wait_for_data and read_response to simulate a scanner replying
    monkeypatch.setattr(backend, "wait_for_data", lambda ser, max_wait=0.3: True)
    monkeypatch.setattr(backend, "read_response", lambda ser, timeout=1.0: "MDL,MOCK")

    # Prepare a generator for comports
    def fake_comports():
        yield types.SimpleNamespace(device="/dev/ttyUSB0", description="Mock Port")

    monkeypatch.setattr(backend.list_ports, "comports", fake_comports)

    detected = backend.find_all_scanner_ports()
    assert detected == [("/dev/ttyUSB0", "MOCK")]
