# scanner_adapters/sds100Adapter.py

from scanner_library.sds100CommandLibrary import commands
from scanner_adapters.scanner_utils_uniden import send_command
from scanner_adapters.base_adapter import BaseScannerAdapter


class SDS100Adapter(BaseScannerAdapter):
    def readVolume(self, ser):
        cmd = commands["VOL"]
        response = send_command(ser, cmd.buildCommand())
        try:
            _, value = response.split(",", 1)
            raw = int(value.strip())
            return round(raw / 29.0, 2)
        except Exception:
            return f"Invalid response: {response}"

    def writeVolume(self, ser, value):
        cmd = commands["VOL"]
        scaled = max(0, min(29, int(round(value * 29))))
        return send_command(ser, cmd.buildCommand(scaled))

    def readSquelch(self, ser):
        cmd = commands["VOL"]
        response = send_command(ser, cmd.buildCommand())
        try:
            _, value = response.split(",", 1)
            raw = int(value.strip())
            return round(raw / 19.0, 2)  # SDS100 uses 0–19 range
        except Exception:
            return f"Invalid response: {response}"

    def writeSquelch(self, ser, value):
        cmd = commands["SQL"]
        scaled = max(0, min(19, int(round(value * 19))))
        send_command(ser, "PRG")
        response = send_command(ser, cmd.buildCommand(scaled))
        send_command(ser, "EPG")
        return response

    def readFrequency(self, ser):
        # No known universal 'read VFO frequency' command for SDS100
        return "Not Supported"

    def writeFrequency(self, ser, value):
        # SDS100 sets frequencies via CIN or channel programming, not VFO
        return "Not Supported"

    def readRSSI(self, ser):
        # No RSSI command available
        return "Not Supported"

    def readSMeter(self, ser):
        # No S-meter data available
        return "Not Supported"

    def readModel(self, ser):
        return send_command(ser, commands["MDL"].buildCommand())

    def readSWVer(self, ser):
        return send_command(ser, commands["VER"].buildCommand())
    
    def sendKey(self, ser, keySeq):
        if not keySeq:
            return "No key(s) provided."

        cmd_base = commands.get("KEY")
        if not cmd_base:
            return "KEY command not supported on this scanner."

        responses = []
        for char in keySeq:
            if char not in "0123456789<>^.EMFHSLP":
                responses.append(f"{char} → skipped (invalid key)")
                continue
            try:
                response = send_command(ser, f"KEY,{char},P")
                responses.append(f"{char} → {response}")
                #time.sleep(0.1)  # Small delay between key presses
            except Exception as e:
                responses.append(f"{char} → ERROR: {e}")
        return "\n".join(responses)