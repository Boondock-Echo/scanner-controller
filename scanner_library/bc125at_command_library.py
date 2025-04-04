from scanner_library.bcd325p2CommandLibrary import commands
from utilities.scanner_utils_uniden import send_command
from scanner_adapters.base_adapter import BaseScannerAdapter
import scanner_library.bc125at_command_library
import time

class BC125ATAdapter(BaseScannerAdapter):
    def __init__(self, machineMode=False):
        self.machineMode = machineMode

    def feedback(self, success, message):
        if self.machineMode:
            return "OK" if success else "ERROR"
        return message

    def getHelp(self, command):
        try:
            return scanner_library.bc125at_command_library.getHelp(command)
        except Exception as e:
            return self.feedback(False, f"❌\t[getHelp Error] {e}")

    def enter_quick_frequency_hold(self, ser, freq_mhz):
        try:
            send_command(ser, "PRG")
            time.sleep(0.2)
            send_command(ser, "EPG")
            time.sleep(0.2)
            send_command(ser, "KEY,S,P")
            time.sleep(0.1)
            send_command(ser, "KEY,S,P")
            time.sleep(0.1)
            send_command(ser, "KEY,H,P")
            time.sleep(0.1)
            freq_str = f"{freq_mhz:.3f}"
            for char in freq_str:
                if char in "0123456789.":
                    send_command(ser, f"KEY,{char},P")
                    time.sleep(0.05)
            send_command(ser, "KEY,H,P")
            time.sleep(0.3)
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                actual_freq = int(parts[2]) / 10000.0
                if abs(actual_freq - freq_mhz) < 0.005:
                    return self.feedback(True, f"✅ Frequency {freq_str} MHz entered and confirmed via PWR ({actual_freq:.5f} MHz)")
                else:
                    return self.feedback(False, f"⚠️ Entered {freq_str} MHz, but PWR returned {actual_freq:.5f} MHz")
            return self.feedback(False, f"❌ PWR returned unexpected: {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [enter_quick_frequency_hold Error] {e}")

    def writeFrequency(self, ser, freq_mhz):
        try:
            send_command(ser, "PRG")
            send_command(ser, "EPG")
            time.sleep(0.1)
            for _ in range(2):
                send_command(ser, "KEY,S")
                time.sleep(0.2)
                send_command(ser, "KEY,H")
            freq_str = f"{float(freq_mhz):.3f}"
            for char in freq_str:
                if char in "0123456789.":
                    send_command(ser, f"KEY,{char}")
                    time.sleep(0.1)
            send_command(ser, "KEY,E")
            return self.feedback(True, f"✅ Frequency {freq_str} MHz entered via keypress")
        except Exception as e:
            return self.feedback(False, f"❌ [writeFrequency Error] {e}")

    def sendKey(self, ser, keySeq):
        if not keySeq:
            return self.feedback(False, "❌ No key(s) provided.")

        responses = []
        for char in keySeq:
            if char not in "0123456789<>^.EMFHSLP":
                responses.append(f"{char} → skipped (invalid key)")
                continue
            try:
                response = send_command(ser, f"KEY,{char},P")
                responses.append(f"✅ {char} → {response}")
            except Exception as e:
                responses.append(f"❌ {char} → ERROR: {e}")
        return "\n".join(responses)