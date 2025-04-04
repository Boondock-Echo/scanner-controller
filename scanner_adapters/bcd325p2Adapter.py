from scanner_library.bcd325p2CommandLibrary import commands
from utilities.scanner_utils import send_command  # Ensure correct import
from scanner_adapters.base_adapter import BaseScannerAdapter

def hex32(value):
    """Convert an integer to a 32-bit hexadecimal string with '0x' prefix."""
    return f"0x{value & 0xFFFFFFFF:08x}"

def update_progress(current, total):
    """Display a progress bar for long-running operations."""
    percent = min(100, int(current * 100 / total))
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = '█' * filled_length + '░' * (bar_length - filled_length)
    print(f"\rProgress: |{bar}| {percent}% Complete", end='', flush=True)
    if current == total:
        print()

class BCD325P2Adapter(BaseScannerAdapter):
    def __init__(self, machineMode=False):
        self.machineMode = machineMode

    def feedback(self, success, message):
        if self.machineMode:
            return "OK" if success else "ERROR"
        return message

    def getHelp(self, command):
        from scanner_library import bcd325p2CommandLibrary
        try:
            return bcd325p2CommandLibrary.getHelp(command)
        except Exception as e:
            return self.feedback(False, f"⚠️ [getHelp Error] {e}")

    def enterProgrammingMode(self, ser):
        return send_command(ser, commands["PRG"].buildCommand())

    def exitProgrammingMode(self, ser):
        return send_command(ser, commands["EPG"].buildCommand())

    def readVolume(self, ser):
        try:
            response = send_command(ser, commands["VOL"].buildCommand())
            _, val = response.split(",")
            return int(val) / 15.0
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readVolume Error] {e}")

    def writeVolume(self, ser, value):
        try:
            level = max(0, min(15, int(round(value * 15))))
            response = send_command(ser, commands["VOL"].buildCommand(level))
            return self.feedback("OK" in response, f"✅\tVolume set to {level} → {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[writeVolume Error] {e}")

    def readSquelch(self, ser):
        try:
            response = send_command(ser, commands["SQL"].buildCommand())
            _, val = response.split(",")
            scaledSquelch = round(int(val) / 15.0, 2)
            return self.feedback(True, f"✅\tSquelch: {scaledSquelch}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readSquelch Error] {e}")

    def writeSquelch(self, ser, value):
        try:
            level = max(0, min(15, int(round(value * 15))))
            response = send_command(ser, commands["SQL"].buildCommand(level))
            return self.feedback("OK" in response, f"✅\tSquelch set to {level} → {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[writeSquelch Error] {e}")

    def readModel(self, ser):
        try:
            return send_command(ser, commands["MDL"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readModel Error] {e}")

    def readSWVer(self, ser):
        try:
            return send_command(ser, commands["VER"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readSWVer Error] {e}")

    def readRSSI(self, ser):
        try:
            response = send_command(ser, commands["PWR"].buildCommand())
            parts = response.split(",")
            if len(parts) == 3:
                return round(int(parts[1]) / 1023.0, 3)
            return self.feedback(False, f"⚠️\tUnexpected PWR response: {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readRSSI Error] {e}")

    def readBatteryVoltage(self, ser):
        try:
            response = send_command(ser, commands["BAV"].buildCommand())
            _, val = response.split(",")
            voltage = (3.2 * int(val) * 2) / 1023
            return round(voltage, 3)
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readBatteryVoltage Error] {e}")

    def readWindowVoltage(self, ser):
        try:
            return send_command(ser, commands["WIN"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readWindowVoltage Error] {e}")

    def readStatus(self, ser):
        try:
            return send_command(ser, commands["STS"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readStatus Error] {e}")

    def readSMeter(self, ser):
        return self.feedback(False, "⚠️\tSMeter not supported on BCD325P2")

    def readFrequency(self, ser):
        try:
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                freq_mhz = (int(parts[2]) * 100) / 1_000_000
                # return round(freq_mhz, 5)
                return self.feedback(False, f"✅\tFrequency: {freq_mhz} MHz")
            return self.feedback(False, f"⚠️\tUnexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readFrequency Error] {e}")

    def writeFrequency(self, ser, freq):
        return self.feedback(False, "⚠️\tFrequency input not supported via direct command.")

    def sendKey(self, ser, keySeq):
        if not keySeq:
            return self.feedback(False, "⚠️\tNo key(s) provided.")

        responses = []
        for char in keySeq:
            if (char not in "0123456789<>^.EMFHSLP"):
                responses.append(f"{char} → skipped (invalid key)")
                continue
            try:
                response = send_command(ser, f"KEY,{char},P")
                responses.append(f"{char} → {response}")
            except Exception as e:
                responses.append(f"⚠️\t{char} → ERROR: {e}")
        return "\n".join(responses)

    def writeKeyBeep(self, ser, level=99, lock=0, safe=0):
        try:
            self.enterProgrammingMode(ser)
            payload = f"{level},{lock},{safe}"
            response = send_command(ser, f"KBP,{payload}")
            self.exitProgrammingMode(ser)
            return self.feedback("OK" in response, f"✅\tKey beep set → {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[writeKeyBeep Error] {e}")

    def dumpMemoryToFile(self, ser, filename="memorydump.txt", start=0x00010000, end=0x0001FFFF, step=16):
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
                        f.write(f"⚠️\t# Unexpected: {response}\n")
                        invalid_streak += 1
                    if invalid_streak >= MAX_INVALID:
                        return self.feedback(False, f"⚠️\t\nAborted early — {MAX_INVALID} invalids.")
                    update_progress(i, total_steps)
            send_command(ser, "EPG")
            return self.feedback(True, f"✅\t{valid_count} MRD entries written to {filename}")
        except Exception as e:
            try: send_command(ser, "EPG")
            except: pass
            return self.feedback(False, f"⚠️\t[Memory Dump Error] {e}")

    def enter_quick_frequency_hold(self, ser, freq_mhz):
        # example: QSH,00893000,,FMB,0,0,,0,1011111111111111,0,,1,0,0
        # example: QSH,00893000
        try:
            freq_str = f"{float(freq_mhz):08.5f}"
            freqHectoHertz = round(int(freq_mhz*1_000_000/100))
            command = f"QSH,{freqHectoHertz}"
            response = send_command(ser, command)
            if response.startswith("QSH,OK"):
                return self.feedback(True, f"Entered frequency hold at {freq_str} MHz")
            return self.feedback(False, f"⚠️\tFailed to enter frequency hold: {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[enter_quick_frequency_hold Error] {e}")

    def readGlobalLockout(self, ser):
        try:
            self.enterProgrammingMode(ser)
            results = []
            while True:
                response = send_command(ser, commands["GLF"].buildCommand())
                if response.strip() == "GLF,-1":
                    break
                results.append(response.strip())
            self.exitProgrammingMode(ser)
            return "\n".join(results)
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readGlobalLockout Error] {e}")

    def readChannelInfo(self, ser, index):
        try:
            self.enterProgrammingMode(ser)
            response = send_command(ser, f"CIN,{index}")
            self.exitProgrammingMode(ser)
            return response
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readChannelInfo Error] {e}")

    def writeChannelInfo(self, ser, index, name, freq_khz, mod, ctcss, delay, lockout, priority):
        try:
            self.enterProgrammingMode(ser)
            parts = [
                str(index),
                name[:16],
                str(freq_khz),
                mod.upper(),
                str(ctcss),
                str(delay),
                str(lockout),
                str(priority),
                "0",  # ATT
                "0",  # ALT
                "0",  # ALTL
                "", "", "", "",  # RSV
                "0",  # AUDIO_TYPE
                "0",  # P25NAC
                "0",  # NUMBER_TAG
                "OFF",  # ALT_COLOR
                "0",  # ALT_PATTERN
                "0"   # VOL_OFFSET
            ]
            response = send_command(ser, f"CIN,{','.join(parts)}")
            self.exitProgrammingMode(ser)
            return self.feedback("OK" in response, f"✅\tChannel {index} written → {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[writeChannelInfo Error] {e}")

    def send_command(self, ser, cmd):
        """
        Wrapper for the send_command function to maintain consistency.
        """
        return send_command(ser, cmd)
