"""
This module defines commands for the Uniden BC125AT scanner.

Each command is represented as a dictionary entry with its name,
validation rules, and help documentation.
"""

from utilities.shared_utils import scanner_command
from utilities.validators import validate_cin, validate_enum

commands = {
    "BAV": scanner_command(
        name="BAV",
        help="""
        Shows battery voltage (10mV units).
        example usage:
        >>> BAV
        <<< BAV,558
        """,
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
        """,
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
        """,
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
        """,
    ),
    "CLC": scanner_command(
        name="CLC",
        requires_prg=True,
        help="""
        Configure Close Call mode (priority, override, alert tones, etc.)
        """,
    ),
    "CIN": scanner_command(
        name="CIN",
        validator=validate_cin,
        help="""Reads or writes a memory channel.

        Read:
        CIN,<index>

        Write:
        CIN,<index>,<name>,<frequency>,<mod>,
        <ctcss/dcs>,<delay>,<lockout>,<priority>

        Field details:
        index     : 1–500
        name      : up to 16 characters
        frequency : e.g., 462525 (in kHz)
        mod       : AUTO, AM, FM, NFM
        ctcss/dcs : 0–231 (tone code)
        delay     : -10, -5, 0–5
        lockout   : 0 = unlocked, 1 = locked out
        priority  : 0 = off, 1 = on""",
    ),
    "COM": scanner_command(
        name="COM",
        help="""
        Possibly related to COM port config (undocumented). Use with caution.
        """,
        requires_prg=True,
    ),
    "CSG": scanner_command(
        name="CSG",
        requires_prg=True,
        help="Custom Search Group status (bitmask of 10 ranges).",
    ),
    "CSP": scanner_command(
        name="CSP",
        requires_prg=True,
        help="Custom search parameters. Format: CSP,<index>,<low>,<high>,...",
    ),
    "DCH": scanner_command(
        name="DCH",
        requires_prg=True,
        help="Delete a channel. Format: DCH,<index>",
    ),
    "EPG": scanner_command(name="EPG", help="Exit programming mode."),
    "ESN": scanner_command(
        name="ESN",
        help="Get scanner ESN (serial number). Returns long identifier.",
    ),
    "FWM": scanner_command(
        name="FWM", help="Firmware maintenance command (unknown purpose)."
    ),
    "GLF": scanner_command(
        name="GLF",
        help=(
            "Get global lockout frequency. Repeated calls return next item "
            "until GLF,-1."
        ),
        requires_prg=True,
    ),
    "GLG": scanner_command(
        name="GLG",
        help="Reception status dump (format undocumented, experimental)",
    ),
    "JNT": scanner_command(
        name="JNT",
        help="Jump to channel number tag (undocumented, returns JNT,ERR).",
    ),
    "JPM": scanner_command(
        name="JPM", help="Jump mode command (undocumented, returns JPM,ERR)."
    ),
    "KBP": scanner_command(
        name="KBP",
        set_format="KBP,{level},{lock}",
        help="Sets key beep (0:Auto, 99:Off) and key lock (0:Off, 1:On).",
        requires_prg=True,
    ),
    "KEY": scanner_command(
        name="KEY",
        set_format="KEY,{value}",
        help="Simulate keypad input. E.g., KEY,1,P for pressing '1'.",
    ),
    "LOF": scanner_command(
        name="LOF",
        help="Lock out a frequency (in kHz). Format: LOF,<frequency>",
        requires_prg=True,
    ),
    "MDL": scanner_command(
        name="MDL", help="Returns scanner model (e.g., BC125AT)."
    ),
    "MMM": scanner_command(
        name="MMM", help="Mystery memory mode (not documented)."
    ),
    "MNU": scanner_command(
        name="MNU", help="Enters menu system (not supported in remote mode)."
    ),
    "MRD": scanner_command(
        name="MRD", help="Reads memory register (debug/test use)."
    ),
    "MWR": scanner_command(
        name="MWR", help="Write memory register (debug/test use)."
    ),
    "PDI": scanner_command(
        name="PDI", help="Possibly peripheral device interface. Undocumented."
    ),
    "PRG": scanner_command(name="PRG", help="Enter programming mode."),
    "PRI": scanner_command(
        name="PRI",
        valid_range=(0, 3),
        help="Sets priority mode (0:Off, 1:On, 2:Plus, 3:DND).",
        requires_prg=True,
    ),
    "PWR": scanner_command(
        name="PWR",
        help="Returns RSSI and current frequency. Format: PWR,<rssi>,<freq>",
    ),
    "QSH": scanner_command(
        name="QSH", help=("Quick search hold mode seems broken on BC125AT. ")
    ),
    "SCG": scanner_command(
        name="SCG",
        help=(
            "Quick group lockout bitmask. "
            "Format: SCG,xxxxxxxxxx (each digit is 0 or 1)"
        ),
        requires_prg=True,
    ),
    "SCO": scanner_command(
        name="SCO",
        help="Search/Close Call Options. Format: SCO,<delay>,<code_search>",
        requires_prg=True,
    ),
    "SQL": scanner_command(
        name="SQL", valid_range=(0, 15), help="Set squelch level (0–15)."
    ),
    "SSG": scanner_command(
        name="SSG",
        help="Service search group (bitmask of 10 categories).",
        requires_prg=True,
    ),
    "STS": scanner_command(
        name="STS", help="Returns scanner status snapshot (multi-field dump)."
    ),
    "SUM": scanner_command(
        name="SUM",
        help="Mystery summary command (appears in logs, unknown use).",
    ),
    "TST": scanner_command(name="TST", help="Enter test mode (be careful!)."),
    "ULF": scanner_command(
        name="ULF",
        help="Unlock a global lockout frequency. Format: ULF,<frequency>",
        requires_prg=True,
    ),
    "VER": scanner_command(name="VER", help="Returns firmware version."),
    "VOL": scanner_command(
        name="VOL", valid_range=(0, 15), help="Set volume level (0–15)."
    ),
    "WIN": scanner_command(
        name="WIN", help="Returns window voltage + frequency (used internally)."
    ),
    "WXS": scanner_command(
        name="WXS",
        help="NOAA weather settings. WXS,<alert_priority> (0=Off, 1=On)",
        requires_prg=True,
    ),
}


def getHelp(command):
    """
    Return the help string for the specified command (case-insensitive).

    Return None if command is not defined.
    """
    cmd = commands.get(command.upper())
    return cmd.help if cmd else None


def listCommands():
    """
    Return a sorted list of all available command names.

    This function retrieves the keys from the commands dictionary,
    sorts them, and returns the sorted list.
    """
    return sorted(commands.keys())
