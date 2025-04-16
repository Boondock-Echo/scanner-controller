# BCD325P2 command definitions for Uniden scanners

"""
Bcd325P2 Commands module.

This module provides functionality related to bcd325p2 commands.
"""


# Application imports
from utilities.core.shared_utils import scanner_command

# Define all commands for the BCD325P2 scanner
commands = {
    "MDL": scanner_command(
        "MDL", help="Returns the scanner model (e.g., BCD325P2)."
    ),
    "VER": scanner_command("VER", help="Returns the firmware version."),
    "PRG": scanner_command("PRG", help="Enter programming mode."),
    "EPG": scanner_command("EPG", help="Exit programming mode."),
    "VOL": scanner_command(
        name="VOL", valid_range=(0, 15), help="Set volume level (0-15)."
    ),
    "SQL": scanner_command(
        name="SQL", valid_range=(0, 15), help="Set squelch level (0-15)."
    ),
    "BAV": scanner_command(
        name="BAV",
        help="Returns battery voltage in 100's of milliVolts\n"
        "529 = 5.29 Volts.",
    ),
    "WIN": scanner_command(
        name="WIN", help="Returns window voltage and frequency."
    ),
    "PWR": scanner_command(
        name="PWR",
        help="""
        Returns RSSI and frequency.
        Format: PWR,<rssi>,<freq>
        """,
    ),
    "STS": scanner_command(
        name="STS",
        help="Returns status display content and various system flags.",
    ),
    "GLG": scanner_command(
        name="GLG",
        help="Get reception status — includes TGID, modulation, squelch, "
        "etc.",
    ),
    "KEY": scanner_command(
        name="KEY",
        set_format="KEY,{value}",
        help="Simulates a keypress. Example: KEY,1,P sends the '1' " "key.",
    ),
    "KBP": scanner_command(
        name="KBP",
        set_format="KBP,{value}",
        requires_prg=True,
        help="Set key beep and key lock. Format: KBP,<level>,<lock>," "<safe>",
    ),
    "CLR": scanner_command(
        name="CLR",
        requires_prg=True,
        help="Clear all scanner memory. (Warning: cannot be undone.)",
    ),
    "CNT": scanner_command(
        name="CNT",
        valid_range=(1, 15),
        requires_prg=True,
        help="Set LCD contrast (1–15).",
    ),
    "DCH": scanner_command(
        name="DCH",
        requires_prg=True,
        help="Delete a channel. Format: DCH,<index>",
    ),
    "CIN": scanner_command(
        name="CIN",
        requires_prg=True,
        help="Get or set channel info. Format: CIN,<index>[,...]",
    ),
    "SCO": scanner_command(
        name="SCO",
        requires_prg=True,
        help="""
        Search/Close Call settings. Many parameters including AGC,
        DLY, ATT.""",
    ),
    "GLF": scanner_command(
        name="GLF",
        requires_prg=True,
        help="Get next Global Lockout Frequency. Repeat until GLF,-1",
    ),
    "ULF": scanner_command(
        name="ULF",
        requires_prg=True,
        help="""
        Unlock a frequency from the Global Lockout list. Format: ULF,<freq>""",
    ),
    "LOF": scanner_command(
        name="LOF",
        requires_prg=True,
        help="Lock out a frequency (in kHz). Format: LOF,<frequency>",
    ),
    "CLC": scanner_command(
        name="CLC",
        requires_prg=True,
        help="""
        Configure Close Call mode (priority, override, alert tones, etc.)
        """,
    ),
    "QSH": scanner_command(
        name="QSH", help="Quick search/hold mode. Format: QSH,<freq_kHz>"
    ),
}
