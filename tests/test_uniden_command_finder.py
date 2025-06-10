"""Tests for utilities.research.uniden_command_finder.find_scanner_port."""

import os
import sys

# Add repository root to import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import utilities.research.uniden_command_finder as ucf  # noqa: E402


class DummySerial:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    def reset_input_buffer(self):
        pass

    def reset_output_buffer(self):
        pass

    def write(self, data):
        self.written = data


class Port:
    def __init__(self, device):
        self.device = device


def test_find_scanner_port_found(monkeypatch):
    """Return the port when a scanner responds."""
    monkeypatch.setattr(ucf.list_ports, "comports", lambda: [Port("COM1")])
    monkeypatch.setattr(ucf.serial, "Serial", lambda *a, **k: DummySerial())
    monkeypatch.setattr(ucf, "read_response", lambda ser: "MDL,BCD325P2")
    monkeypatch.setattr(ucf.time, "sleep", lambda *a, **k: None)

    assert ucf.find_scanner_port(max_attempts=1) == "COM1"


def test_find_scanner_port_none(monkeypatch):
    """Return ``None`` when the scanner is not found within the limit."""
    monkeypatch.setattr(ucf.list_ports, "comports", lambda: [])
    monkeypatch.setattr(ucf.serial, "Serial", lambda *a, **k: DummySerial())
    monkeypatch.setattr(ucf.time, "sleep", lambda *a, **k: None)

    assert ucf.find_scanner_port(max_attempts=2) is None

