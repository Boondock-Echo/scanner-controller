import scanner_library
from scanner_library.bcd325p2CommandLibrary import commands
from scanner_library.bc125atCommandLibrary import commands
import time

class BaseScannerAdapter:
    def readVolume(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def writeVolume(self, ser, value):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readSquelch(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def writeSquelch(self, ser, value):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readFrequency(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def writeFrequency(self, ser, value):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readRSSI(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readSMeter(self, ser): return "Not Supported"

    def readModel(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readSWVer(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

class BC125ATAdapter(BaseScannerAdapter):
    def __init__(self, machineMode=False):
        self.machineMode = machineMode

    def feedback(self, success, message):
        if self.machineMode:
            return "OK" if success else "ERROR"
        return message

    def getHelp(self, command):
        try:
            return scanner_library.bc125atCommandLibrary.getHelp(command)
        except Exception as e:
            return self.feedback(False, f"❌\t[getHelp Error] {e}")

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
            from scanner_adapters.scanner_utils import send_command
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
                        f.write(f"❌ # Unexpected: {response}\n")
                        invalid_streak += 1
                    if invalid_streak >= MAX_INVALID:
                        return self.feedback(False, f"❌ \nAborted early — {MAX_INVALID} invalids.")
                    update_progress(i, total_steps)
            send_command(ser, "EPG")
            return self.feedback(True, f"{valid_count} MRD entries written to {filename}")
        except Exception as e:
            try: 
                send_command(ser, "EPG")
            except: 
                pass
            return self.feedback(False, f"[Memory Dump Error] {e}")

    def writeKeyBeep(self, ser, level=99, lock=0):
        try:
            from scanner_adapters.scanner_utils import send_command
            send_command(ser, "PRG")
            cmd = commands["KBP"]
            response = send_command(ser, cmd.buildCommand(f"{level},{lock}"))
            send_command(ser, "EPG")
            return self.feedback(True, f"✅ Set key beep to {level}, lock to {lock} → {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [writeKeyBeep Error] {e}")

    def writeVolume(self, ser, value):
        try:
            from scanner_adapters.scanner_utils import send_command
            if not (0.0 <= value <= 1.0):
                return self.feedback(False, "⚠️ Volume must be between 0.0 and 1.0")
            scaled = int(round(value * 15))
            response = send_command(ser, commands["VOL"].buildCommand(scaled))
            return self.feedback("OK" in response, f"✅ Volume set to {value:.2f} → {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [writeVolume Error] {e}")
    
    def readVolume(self, ser):
        try:
            from scanner_adapters.scanner_utils import send_command
            response = send_command(ser, commands["VOL"].buildCommand())
            _, value = response.split(",", 1)
            volume = float(int(value.strip()) / 15.0)
            return self.feedback(True, f"✅ Volume level: {volume:.2f}")
        except Exception as e:
            return self.feedback(False, f"❌ [readVolume Error] {e}")

    def readSquelch(self, ser):
        try:
            from scanner_adapters.scanner_utils import send_command
            response = send_command(ser, commands["SQL"].buildCommand())
            _, value = response.split(",", 1)
            squelch = float(int(value.strip()) / 15.0)
            return self.feedback(True, f"✅ Squelch level: {squelch:.2f}")
        except Exception as e:
            return self.feedback(False, f"❌ [readSquelch Error] {e}")

    def writeSquelch(self, ser, value):
        try:
            from scanner_adapters.scanner_utils import send_command
            if not (0.0 <= value <= 1.0):
                return self.feedback(False, "❌ Squelch must be between 0.0 and 1.0")
            scaled = int(round(value * 15))
            send_command(ser, "PRG")
            response = send_command(ser, commands["SQL"].buildCommand(scaled))
            send_command(ser, "EPG")
            return self.feedback("OK" in response, f"✅Squelch set to {value:.2f} → {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [writeSquelch Error] {e}")

    def readFrequency(self, ser):
        try:
            from scanner_adapters.scanner_utils import send_command
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                freq_mhz = (int(parts[2]) * 100) / 1_000_000
                return self.feedback(True, f"✅ Frequency: {round(freq_mhz, 5)} MHz")
            return self.feedback(False, f"❌ Unexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [readFrequency Error] {e}")

    def writeFrequency(self, ser, freq_mhz):
        try:
            from scanner_adapters.scanner_utils import send_command
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

    def readRSSI(self, ser):
        try:
            from scanner_adapters.scanner_utils import send_command
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                rssi = round(int(parts[1]) / 1023.0, 3)
                return self.feedback(True, f"✅ RSSI: {rssi}")
            return self.feedback(False, f"❌ Unexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [readRSSI Error] {e}")
    
    def readModel(self, ser):
        try:
            from scanner_adapters.scanner_utils import send_command
            model = send_command(ser, commands["MDL"].buildCommand())
            return self.feedback(True, f"✅ Model: {model}")
        except Exception as e:
            return self.feedback(False, f"❌ [readModel Error] {e}")

    def readSWVer(self, ser):
        try:
            from scanner_adapters.scanner_utils import send_command
            version = send_command(ser, commands["VER"].buildCommand())
            return self.feedback(True, f"✅ Software Version: {version}")
        except Exception as e:
            return self.feedback(False, f"❌ [readSWVer Error] {e}")

    def readSMeter(self, ser):
        return self.feedback(False, "❌ SMeter not supported")    
        
        
"""
    # Removing for now -- different command set for SDS100
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
"""
