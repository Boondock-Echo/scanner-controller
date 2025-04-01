# bcd325p2CommandLibrary.py

"""
BCD325P2 Command Library (refactored)

This file defines the BCD325P2-specific command structure, using the
shared ScannerCommand class from scannerUtils.py.

It supports:
- The BCD325P2Adapter for building commands
- The main program for contextual help (via getHelp)
"""
from utilities.shared_utils import ScannerCommand, validate_enum


# ------------------------------------------------------------------------------
# Command Definitions
# ------------------------------------------------------------------------------

commands = {
    "MDL": ScannerCommand("MDL", help="Returns the scanner model (e.g., BCD325P2)."),
    "VER": ScannerCommand("VER", help="Returns the firmware version."),
    "PRG": ScannerCommand("PRG", help="Enter programming mode."),
    "EPG": ScannerCommand("EPG", help="Exit programming mode."),

    "VOL": ScannerCommand(
        name="VOL",
        valid_range=(0, 15),
        help="Set volume level (0-15)."
    ),

    "SQL": ScannerCommand(
        name="SQL",
        valid_range=(0, 15),
        help="Set squelch level (0-15)."
    ),

    "BAV": ScannerCommand(
        name="BAV",
        help="Returns battery voltage in 100's of milliVolts\n529 = 5.29 Volts."
    ),

    "WIN": ScannerCommand(
        name="WIN",
        help="Returns window voltage and frequency."
    ),

    "PWR": ScannerCommand(
        name="PWR",
        help="Returns RSSI and frequency. Format: PWR,<rssi>,<freq>"
    ),

    "STS": ScannerCommand(
        name="STS",
        help="Returns status display content and various system flags."
    ),

    "GLG": ScannerCommand(
        name="GLG",
        help="Get reception status — includes TGID, modulation, squelch, etc."
    ),

    "KEY": ScannerCommand(
        name="KEY",
        set_format="KEY,{value}",
        help="Simulates a keypress. Example: KEY,1,P sends the '1' key."
    ),

    "KBP": ScannerCommand(
        name="KBP",
        set_format="KBP,{value}",
        requires_prg=True,
        help="Set key beep and key lock. Format: KBP,<level>,<lock>,<safe>"
    ),

    "CLR": ScannerCommand(
        name="CLR",
        requires_prg=True,
        help="Clear all scanner memory. (Warning: cannot be undone.)"
    ),

    "CNT": ScannerCommand(
        name="CNT",
        valid_range=(1, 15),
        requires_prg=True,
        help="Set LCD contrast (1–15)."
    ),

    "DCH": ScannerCommand(
        name="DCH",
        requires_prg=True,
        help="Delete a channel. Format: DCH,<index>"
    ),

    "CIN": ScannerCommand(
        name="CIN",
        requires_prg=True,
        help="Get or set channel info. Format: CIN,<index>[,...]"
    ),

    "SCO": ScannerCommand(
        name="SCO",
        requires_prg=True,
        help="Search/Close Call settings. Many parameters including AGC, DLY, ATT."
    ),

    "GLF": ScannerCommand(
        name="GLF",
        requires_prg=True,
        help="Get next Global Lockout Frequency. Repeat until GLF,-1"
    ),

    "ULF": ScannerCommand(
        name="ULF",
        requires_prg=True,
        help="Unlock a frequency from the Global Lockout list. Format: ULF,<freq>"
    ),

    "LOF": ScannerCommand(
        name="LOF",
        requires_prg=True,
        help="Lock out a frequency (in kHz). Format: LOF,<frequency>"
    ),

    "CLC": ScannerCommand(
        name="CLC",
        requires_prg=True,
        help="Configure Close Call mode (priority, override, alert tones, etc.)"
    ),

    "CSG": ScannerCommand(
        name="CSG",
        requires_prg=True,
        help="Custom Search Group status (bitmask of 10 ranges)."
    ),

    "CSP": ScannerCommand(
        name="CSP",
        requires_prg=True,
        help="Custom search parameters. Format: CSP,<index>,<low>,<high>,..."
    ),

    "WXS": ScannerCommand(
        name="WXS",
        requires_prg=True,
        help="NOAA weather alert and AGC configuration."
    ),
}

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
