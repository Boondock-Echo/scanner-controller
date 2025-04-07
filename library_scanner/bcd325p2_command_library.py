from utilities.scanner_utils import send_command
from adapter_scanner.base_adapter import BaseScannerAdapter
from library_scanner.commands.commands_uniden_bcd325p2 import commands  # Import commands from the correct library
from utilities.shared_utils import scanner_command

import library_scanner.bcd325p2_command_library
import time

from utilities.validators import validate_enum, validate_cin  # Correct imports

# ------------------------------------------------------------------------------
# Command Definitions
# ------------------------------------------------------------------------------

"""
BCD325P2 Command Library

This file defines the BCD325P2-specific command structure, using the
shared scanner_command class from scannerUtils.py.

It is used by:
- The BCD325P2Adapter for building commands 

# Search of all 3-letter commands (except PRG, POF) yielded the following:
ABP: ABP,NG       ACC: ACC,NG       ACT: ACT,NG       AGC: AGC,NG       AGT: AGT,NG
AGV: AGV,NG       AOP: AOP,NG       AST: AST,NG       BAV: BAV,480      BBS: BBS,NG
BLT: BLT,NG       BSP: BSP,NG       BSV: BSV,NG       CBP: CBP,NG       CIE: CIE,NG
CIN: CIN,NG       CLA: CLA,NG       CLC: CLC,NG       CLR: CLR,NG       CNT: CNT,NG
COM: COM,NG       CSC: CSC,ERR      CSG: CSG,NG       CSP: CSP,NG       CSY: CSY,NG
DBC: DBC,NG       DCH: DCH,NG       DGR: DGR,NG       DLA: DLA,NG       DSY: DSY,NG
EPG: EPG,OK       ESN: ESN,37902048001926,0F0,1       EWP: EWP,ERR      FSC: FSC,OK
FWD: FWD,NG       FWM: FWM,NG       GCM: GCM,NG       GDO: GDO,NG       GID: GID,,,,,,
GIE: GIE,NG       GIN: GIN,NG       GLF: GLF,-1       GLG: GLG,,,,,,,,,,,, GLI: GLI,NG
JNT: JNT,ERR      JPM: JPM,ERR      KBP: KBP,NG       KEY: KEY,ERR      LCT: LCT,NG
LIH: LIH,NG       LIN: LIN,NG       LIT: LIT,NG       LOF: LOF,NG       LOI: LOI,NG
MCP: MCP,NG       MDL: MDL,BCD325P2 MEM: MEM,NG       MMM: MMM,NG       MNU: MNU,ERR
MRD: MRD,00000000,ERR               MWR: MWR,NG       OMS: OMS,NG       PDI: PDI,NG
POF: POF,OK       PRI: PRI,NG       PRG: PRG,OK       PWR: PWR,241,04623875
QGL: QGL,NG       QSC: QSC,ERR      QSH: QSH,ERR      QSL: QSL,NG       REV: REV,NG
RIE: RIE,NG       RMB: RMB,NG       SCN: SCN,NG       SCO: SCO,NG       SCT: SCT,NG
SGP: SGP,NG       SHK: SHK,NG       SIF: SIF,NG       SIH: SIH,NG       SIN: SIN,NG
SIT: SIT,NG       SLI: SLI,NG       SQL: SQL,1        SSP: SSP,NG       STS: STS,011000,
            ,,Qck Save Grp    ,,FireWatch       ,, 462.3875 DCS331,,S0:----------   
            ,,GRP----------   ,,1,1,0,0,0,0,0,RED,0
SUM: SUM,00ACH    TFQ: TFQ,NG       TIN: TIN,NG       TON: TON,NG       TRN: TRN,NG
TST: TST,NG       ULF: ULF,ERR      ULI: ULI,NG       VER: VER,Version 1.09.12
VOL: VOL,0        WIN: WIN,86,04623875           WXS: WXS,NG
"""


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