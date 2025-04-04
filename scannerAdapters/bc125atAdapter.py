from utilities.shared_utils import scanner_command
from utilities.scanner_utils import send_command  # Correct location for send_command
from scanner_adapters.base_adapter import BaseScannerAdapter
from scanner_library.commands.bc125at_commands import commands  # Import commands from the correct library
from utilities.validators import validate_enum, validate_cin  # Correct imports
#from scanner_adapters.scanner_utils import send_command  # Correct location for send_command    

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
            return commands.getHelp(command)
        except Exception as e:
            return self.feedback(False, f"⚠️ [getHelp Error] {e}")

    def dumpMemoryToFile(self, ser, filename="memorydump.txt", start=0x00000000, end=0x0000FFFF, step=16):
        import sys

        def hex32(i): return f"{i:08X}"

        def update_progress(current, total):
            percent = int(100 * current / total)
            if percent > update_progress.last_shown:
                update_progress.last_shown = percent
                bar = "#" * (percent // 2)
                sys.stdout.write(f"\rProgress: [{bar:<50}] {percent}%")
                sys.stdout.flush()
        update_progress.last_shown = -1

        try:
            send_command(ser, "PRG")
            total_steps = ((end - start) // step) + 1
            valid_count, invalid_streak = 0, 0
            MAX_INVALID = 4096
            with open(filename, "w") as f:
                for i in range(total_steps):
                    addr = start + i * step
                    cmd = f"MRD,{hex32(addr)}"
                    response = send_command(ser, cmd)
                    if response.startswith("MRD,"):
                        f.write(response + "\n")
                        valid_count += 1
                        invalid_streak = 0
                    elif "ERR" in response or "NG" in response:
                        invalid_streak += 1
                    else:
                        f.write(f"⚠️ # Unexpected: {response}\n")
                        invalid_streak += 1
                    if invalid_streak >= MAX_INVALID:
                        return self.feedback(False, f"⚠️ \nAborted early — {MAX_INVALID} invalids.")
                    update_progress(i, total_steps)
            send_command(ser, "EPG")
            return self.feedback(True, f"{valid_count} MRD entries written to {filename}")
        except Exception as e:
            try: send_command(ser, "EPG")
            except: pass
            return self.feedback(False, f"[Memory Dump Error] {e}")

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
            return self.feedback(False, f"⚠️ PWR returned unexpected: {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️ [enter_quick_frequency_hold Error] {e}")

    def writeKeyBeep(self, ser, level=99, lock=0):
        try:
            send_command(ser, "PRG")
            cmd = commands["KBP"]
            response = send_command(ser, cmd.buildCommand(f"{level},{lock}"))
            send_command(ser, "EPG")
            return self.feedback(True, f"✅ Set key beep to {level}, lock to {lock} → {response}")
        except Exception as e:
            return self.feedback(False, f"[writeKeyBeep Error] {e}")

    def readVolume(self, ser):
        try:
            response = send_command(ser, commands["VOL"].buildCommand())
            _, value = response.split(",", 1)
            return float(int(value.strip()) / 15.0)
        except Exception as e:
            return self.feedback(False, f"⚠️ [readVolume Error] {e}")

    def writeVolume(self, ser, value):
        try:
            if not (0.0 <= value <= 1.0):
                return self.feedback(False, "⚠️ Volume must be between 0.0 and 1.0")
            scaled = int(round(value * 15))
            response = send_command(ser, commands["VOL"].buildCommand(scaled))
            return self.feedback("OK" in response, f"✅ Volume set to {value:.2f} → {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️ [writeVolume Error] {e}")

    def readSquelch(self, ser):
        try:
            response = send_command(ser, commands["SQL"].buildCommand())
            _, value = response.split(",", 1)
            return float(int(value.strip()) / 15.0)
        except Exception as e:
            return self.feedback(False, f"⚠️ [readSquelch Error] {e}")

    def writeSquelch(self, ser, value):
        try:
            if not (0.0 <= value <= 1.0):
                return self.feedback(False, "⚠️ Squelch must be between 0.0 and 1.0")
            scaled = int(round(value * 15))
            send_command(ser, "PRG")
            response = send_command(ser, commands["SQL"].buildCommand(scaled))
            send_command(ser, "EPG")
            return self.feedback("OK" in response, f"✅Squelch set to {value:.2f} → {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️ [writeSquelch Error] {e}")

    def readFrequency(self, ser):
        try:
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                freq_mhz = (int(parts[2]) * 100) / 1_000_000
                return round(freq_mhz, 5)
            return self.feedback(False, f"✅ Unexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️ [readFrequency Error] {e}")

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
            return self.feedback(False, f"⚠️ [writeFrequency Error] {e}")

    def readRSSI(self, ser):
        try:
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                return round(int(parts[1]) / 1023.0, 3)
            return self.feedback(False, f"⚠️ Unexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️ [readRSSI Error] {e}")

    def sendKey(self, ser, keySeq):
        if not keySeq:
            return self.feedback(False, "⚠️ No key(s) provided.")

        responses = []
        for char in keySeq:
            if char not in "0123456789<>^.EMFHSLP":
                responses.append(f"{char} → skipped (invalid key)")
                continue
            try:
                response = send_command(ser, f"KEY,{char},P")
                responses.append(f"✅ {char} → {response}")
            except Exception as e:
                responses.append(f"⚠️ {char} → ERROR: {e}")
        return "\n".join(responses)

    def readModel(self, ser):
        try:
            return send_command(ser, commands["MDL"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️ [readModel Error] {e}")

    def readSWVer(self, ser):
        try:
            return send_command(ser, commands["VER"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️ [readSWVer Error] {e}")

    def readSMeter(self, ser):
        return self.feedback(False, "⚠️ SMeter not supported")