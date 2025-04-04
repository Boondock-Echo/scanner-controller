# scanner_adapters/aordv1Adapter.py

from scanner_library.aordv1CommandLibrary import commands
from utilities.scanner_utils import send_command
from scanner_adapters.base_adapter import BaseScannerAdapter


class AORDV1Adapter(BaseScannerAdapter):
    def readVolume(self, ser):
        cmd = commands["AG"]  # Audio Gain: 00–99
        response = send_command(ser, cmd.buildCommand())
        raw = int(response)
        return raw / 99.0

    def writeVolume(self, ser, value):
        cmd = commands["AG"]
        scaled = max(0, min(99, int(round(value * 99))))
        return send_command(ser, cmd.buildCommand(scaled))

    def readSquelch(self, ser):
        cmd = commands["SQ"]
        response = send_command(ser, cmd.buildCommand())
        return response  # May need to be parsed further

    def writeSquelch(self, ser, value):
        cmd = commands["SQ"]
        # Just pass through value as-is; SQ may expect a mode string like "1", "2", etc.
        return send_command(ser, cmd.buildCommand(value))

    def readFrequency(self, ser):
        cmd = commands["RF"]
        response = send_command(ser, cmd.buildCommand())
        return response.strip()  # Returns MHz as string (e.g., "145.50000")

    def writeFrequency(self, ser, value):
        cmd = commands["RF"]
        freq_str = f"{float(value):.5f}"  # Format to 5 decimal places
        return send_command(ser, cmd.buildCommand(freq_str))

    def readRSSI(self, ser):
        cmd = commands["RX"]
        response = send_command(ser, cmd.buildCommand())
        return response  # May contain signal info

    def readSMeter(self, ser):
        cmd = commands["RX"]
        response = send_command(ser, cmd.buildCommand())
        return response  # Same as readRSSI for now

    def readModel(self, ser):
        cmd = commands["WI"]
        return send_command(ser, cmd.buildCommand())

    def readSWVer(self, ser):
        cmd = commands["VR"]
        return send_command(ser, cmd.buildCommand())