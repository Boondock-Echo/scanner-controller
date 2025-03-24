# scannerAdapters/bcd325p2Adapter.py

from scannerLibrary.bcd325p2CommandLibrary import commands
from scannerUtils import send_command
from scannerAdapters.baseAdapter import BaseScannerAdapter


class BCD325P2Adapter(BaseScannerAdapter):
    def readVolume(self, ser):
        cmd = commands["VOL"]
        response = send_command(ser, cmd.buildCommand())
        raw = int(response)
        return raw / 15.0  # 0–15 range

    def writeVolume(self, ser, value):
        cmd = commands["VOL"]
        scaled = max(0, min(15, int(round(value * 15))))
        return send_command(ser, cmd.buildCommand(scaled))

    def readSquelch(self, ser):
        cmd = commands["SQL"]
        send_command(ser, "PRG")
        response = send_command(ser, cmd.buildCommand())
        send_command(ser, "EPG")
        raw = int(response)
        return raw / 15.0

    def writeSquelch(self, ser, value):
        cmd = commands["SQL"]
        scaled = max(0, min(15, int(round(value * 15))))
        send_command(ser, "PRG")
        response = send_command(ser, cmd.buildCommand(scaled))
        send_command(ser, "EPG")
        return response
    
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

    def readFrequency(self, ser):
        # Like SDS100, no simple VFO-style frequency readout
        return "Not Supported"

    def writeFrequency(self, ser, value):
        return "Not Supported"

    def readRSSI(self, ser):
        return "Not Supported"

    def readSMeter(self, ser):
        return "Not Supported"

    def readModel(self, ser):
        return send_command(ser, commands["MDL"].buildCommand())

    def readSWVer(self, ser):
        return send_command(ser, commands["VER"].buildCommand())
