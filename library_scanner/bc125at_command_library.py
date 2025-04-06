from utilities.scanner_utils_uniden import send_command
from adapter_scanner.base_adapter import BaseScannerAdapter
import library_scanner.bc125at_command_library
import time
from utilities.shared_utils import scanner_command

# ------------------------------------------------------------------------------
# Command Definitions
# ------------------------------------------------------------------------------

commands = {
    "MDL": scanner_command("MDL", help="Returns the scanner model (e.g., BCD325P2)."),
    "VER": scanner_command("VER", help="Returns the firmware version."),
    "PRG": scanner_command("PRG", help="Enter programming mode."),
    "EPG": scanner_command("EPG", help="Exit programming mode."),

    "VOL": scanner_command(
        name="VOL",
        valid_range=(0, 15),
        help="Set volume level (0-15)."
    ),

    "SQL": scanner_command(
        name="SQL",
        valid_range=(0, 15),
        help="Set squelch level (0-15)."
    ),

    "BAV": scanner_command(
        name="BAV",
        help="Returns battery voltage in 100's of milliVolts\n529 = 5.29 Volts."
    ),

    "WIN": scanner_command(
        name="WIN",
        help="Returns window voltage and frequency."
    ),

    "PWR": scanner_command(
        name="PWR",
        help="Returns RSSI and frequency. Format: PWR,<rssi>,<freq>"
    ),

    "STS": scanner_command(
        name="STS",
        help="Returns status display content and various system flags."
    ),

    "GLG": scanner_command(
        name="GLG",
        help="Get reception status — includes TGID, modulation, squelch, etc."
    ),

    "KEY": scanner_command(
        name="KEY",
        set_format="KEY,{value}",
        help="Simulates a keypress. Example: KEY,1,P sends the '1' key."
    ),

    "KBP": scanner_command(
        name="KBP",
        set_format="KBP,{value}",
        requires_prg=True,
        help="Set key beep and key lock. Format: KBP,<level>,<lock>,<safe>"
    ),

    "CLR": scanner_command(
        name="CLR",
        requires_prg=True,
        help="Clear all scanner memory. (Warning: cannot be undone.)"
    ),

    "CNT": scanner_command(
        name="CNT",
        valid_range=(1, 15),
        requires_prg=True,
        help="Set LCD contrast (1–15)."
    ),

    "DCH": scanner_command(
        name="DCH",
        requires_prg=True,
        help="Delete a channel. Format: DCH,<index>"
    ),

    "CIN": scanner_command(
        name="CIN",
        requires_prg=True,
        help="Get or set channel info. Format: CIN,<index>[,...]"
    ),

    "SCO": scanner_command(
        name="SCO",
        requires_prg=True,
        help="Search/Close Call settings. Many parameters including AGC, DLY, ATT."
    ),

    "GLF": scanner_command(
        name="GLF",
        requires_prg=True,
        help="Get next Global Lockout Frequency. Repeat until GLF,-1"
    ),

    "ULF": scanner_command(
        name="ULF",
        requires_prg=True,
        help="Unlock a frequency from the Global Lockout list. Format: ULF,<freq>"
    ),

    "LOF": scanner_command(
        name="LOF",
        requires_prg=True,
        help="Lock out a frequency (in kHz). Format: LOF,<frequency>"
    ),

    "CLC": scanner_command(
        name="CLC",
        requires_prg=True,
        help="Configure Close Call mode (priority, override, alert tones, etc.)"
    ),

    "CSG": scanner_command(
        name="CSG",
        requires_prg=True,
        help="Custom Search Group status (bitmask of 10 ranges)."
    ),

    "CSP": scanner_command(
        name="CSP",
        requires_prg=True,
        help="Custom search parameters. Format: CSP,<index>,<low>,<high>,..."
    ),

    "WXS": scanner_command(
        name="WXS",
        requires_prg=True,
        help="NOAA weather alert and AGC configuration."
    ),
}


class BC125ATAdapter(BaseScannerAdapter):
    def __init__(self, machineMode=False):
        self.machineMode = machineMode

    def feedback(self, success, message):
        if self.machineMode:
            return "OK" if success else "ERROR"
        return message

    def getHelp(self, command):
        try:
            return library_scanner.bc125at_command_library.getHelp(command)
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