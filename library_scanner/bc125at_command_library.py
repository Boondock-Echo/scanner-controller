from utilities.scanner_utils_uniden import send_command
from adapter_scanner.base_adapter import BaseScannerAdapter
import library_scanner.bc125at_command_library
import time
from utilities.shared_utils import scanner_command
from utilities.validators import validate_enum, validate_cin  # Correct imports

# ------------------------------------------------------------------------------
# Command Definitions
# ------------------------------------------------------------------------------

commands = {
    "BAV": scanner_command(
        name="BAV",
        help="""
        Shows battery voltage (10mV units).
        example usage:
        >>> BAV
        <<< BAV,558
        """
    ),

    "BLT": scanner_command(
        name="BLT",
        validator=validate_enum("BLT", ["AO", "AF", "KY", "KS", "SQ"]),
        requires_prg=True,
        help="""
        Sets the backlight mode.
        (requires PRG mode)
        Valid values:
        AO - Always On
        AF - After keypress
        KY - Key press only
        KS - Key press + squelch
        SQ - Squelch only
        """
    ),

    "BPL": scanner_command(
        name="BPL",
        validator=validate_enum("BPL", ["0", "1"]),
        requires_prg=True,
        help="""
        Unknown. Likely selects the bandplan.
        Valid values:
        0: unknown
        1: unknown
        2: unknown
        """
    ),

    "BSV": scanner_command(
        name="BSV",
        valid_range=(0, 14),
        requires_prg=True,
        help="""
        NiCd battery Saver Mode
        increase the charge time based on the mAh of the batteries
        1-14
        NiCd battery values TBD.
        """
    ),

    "CLC": scanner_command(
        name="CLC",
        requires_prg=True,
        help="Configure Close Call mode (priority, override, alert tones, etc.)"
    ),

    "CIN": scanner_command(
        name="CIN",
        validator=validate_cin,
        help="""Reads or writes a memory channel.

        Read:
        CIN,<index>

        Write:
        CIN,<index>,<name>,<frequency>,<mod>,<ctcss/dcs>,<delay>,<lockout>,<priority>

        Field details:
        index     : 1–500
        name      : up to 16 characters
        frequency : e.g., 462525 (in kHz)
        mod       : AUTO, AM, FM, NFM
        ctcss/dcs : 0–231 (tone code)
        delay     : -10, -5, 0–5
        lockout   : 0 = unlocked, 1 = locked out
        priority  : 0 = off, 1 = on"""
    ),

    "COM": scanner_command(
        name="COM",
        help="Possibly related to COM port config (undocumented). Use with caution.",
        requires_prg=True
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

    "DCH": scanner_command(
        name="DCH",
        requires_prg=True,
        help="Delete a channel. Format: DCH,<index>"
    ),

    "EPG": scanner_command(
        name="EPG",
        help="Exit programming mode."
    ),

    "ESN": scanner_command(
        name="ESN",
        help="Get scanner ESN (serial number). Returns long identifier."
    ),

    "FWM": scanner_command(
        name="FWM",
        help="Firmware maintenance command (unknown purpose)."
    ),

    "GLF": scanner_command(
        name="GLF",
        help="Get global lockout frequency. Repeated calls return next item until GLF,-1.",
        requires_prg=True
    ),

    "GLG": scanner_command(
        name="GLG",
        help="Reception status dump (format undocumented, experimental)"
    ),

    "JNT": scanner_command(
        name="JNT",
        help="Jump to channel number tag (undocumented, returns JNT,ERR)."
    ),

    "JPM": scanner_command(
        name="JPM",
        help="Jump mode command (undocumented, returns JPM,ERR)."
    ),

    "KBP": scanner_command(
        name="KBP",
        set_format="KBP,{level},{lock}",
        help="Sets key beep (0:Auto, 99:Off) and key lock (0:Off, 1:On).",
        requires_prg=True
    ),

    "KEY": scanner_command(
        name="KEY",
        set_format="KEY,{value}",
        help="Simulate keypad input. E.g., KEY,1,P for pressing '1'."
    ),

    "LOF": scanner_command(
        name="LOF",
        help="Lock out a frequency (in kHz). Format: LOF,<frequency>",
        requires_prg=True
    ),

    "MDL": scanner_command(
        name="MDL",
        help="Returns scanner model (e.g., BC125AT)."
    ),

    "MMM": scanner_command(
        name="MMM",
        help="Mystery memory mode (not documented)."
    ),

    "MNU": scanner_command(
        name="MNU",
        help="Enters menu system (not supported in remote mode)."
    ),

    "MRD": scanner_command(
        name="MRD",
        help="Reads memory register (debug/test use)."
    ),

    "MWR": scanner_command(
        name="MWR",
        help="Write memory register (debug/test use)."
    ),

    "PDI": scanner_command(
        name="PDI",
        help="Possibly peripheral device interface. Undocumented."
    ),

    "PRG": scanner_command(
        name="PRG",
        help="Enter programming mode."
    ),

    "PRI": scanner_command(
        name="PRI",
        valid_range=(0, 3),
        help="Sets priority mode (0:Off, 1:On, 2:Plus, 3:DND).",
        requires_prg=True
    ),

    "PWR": scanner_command(
        name="PWR",
        help="Returns RSSI and current frequency. Format: PWR,<rssi>,<freq>"
    ),

    "QSH": scanner_command(
        name="QSH",
        help="Quick search hold mode (seems broken on BC125AT. I've tried 42k permutations of commands)\nNext possibility is that it's a chained command or only available in certain modes."
    ),

    "SCG": scanner_command(
        name="SCG",
        help="Quick group lockout bitmask. Format: SCG,xxxxxxxxxx (each digit is 0 or 1)",
        requires_prg=True
    ),

    "SCO": scanner_command(
        name="SCO",
        help="Search/Close Call Options. Format: SCO,<delay>,<code_search>",
        requires_prg=True
    ),

    "SQL": scanner_command(
        name="SQL",
        valid_range=(0, 15),
        help="Set squelch level (0–15)."
    ),

    "SSG": scanner_command(
        name="SSG",
        help="Service search group (bitmask of 10 categories).",
        requires_prg=True
    ),

    "STS": scanner_command(
        name="STS",
        help="Returns scanner status snapshot (multi-field dump)."
    ),

    "SUM": scanner_command(
        name="SUM",
        help="Mystery summary command (appears in logs, unknown use)."
    ),

    "TST": scanner_command(
        name="TST",
        help="Enter test mode (be careful!)."
    ),

    "ULF": scanner_command(
        name="ULF",
        help="Unlock a global lockout frequency. Format: ULF,<frequency>",
        requires_prg=True
    ),

    "VER": scanner_command(
        name="VER",
        help="Returns firmware version."
    ),

    "VOL": scanner_command(
        name="VOL",
        valid_range=(0, 15),
        help="Set volume level (0–15)."
    ),

    "WIN": scanner_command(
        name="WIN",
        help="Returns window voltage + frequency (used internally)."
    ),

    "WXS": scanner_command(
        name="WXS",
        help="NOAA weather settings. WXS,<alert_priority> (0=Off, 1=On)",
        requires_prg=True
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
    
    # ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------

def getHelp(command):
    """
    Returns the help string for the specified command (case-insensitive).
    Returns None if command is not defined.
    """
    cmd = commands.get(command.upper())
    return cmd.help if cmd else None

def listCommands():
    """
    Returns a sorted list of all available command names.
    """
    return sorted(commands.keys())