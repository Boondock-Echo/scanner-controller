# bc125atCommandLibrary.py

"""
BC125AT Command Library

This file defines the BC125AT-specific command structure, including valid ranges,
query/set formats, help descriptions, and optional validators or parsers.

It is used by:
- The BC125ATAdapter to build and parse commands
- The main program to support contextual help (via getHelp)
"""

from scannerUtils import ScannerCommand, validate_enum, validate_cin

"""
# search of all 3 letter commands commands (except PRG, POF, ) yielded the following
BLT: BLT,NG  BPL: BPL,NG  BSV: BSV,NG  CIN: CIN,NG  CLC: CLC,NG  CLR: CLR,NG  CNT: CNT,NG  COM: COM,NG  CSG: CSG,NG
CSP: CSP,NG  DCH: DCH,NG  FWM: FWM,NG  KBP: KBP,NG  LOF: LOF,NG  MMM: MMM,NG  MWR: MWR,NG  PDI: PDI,NG  PRI: PRI,NG
SCG: SCG,NG  SCO: SCO,NG  SSG: SSG,NG  TST: TST,NG  WXS: WXS,NG  BAV: BAV,558 EPG: EPG,OK  ESN: ESN,XXXXXXXXXXXXXX,000,1
GLF: GLF,-1  GLG: GLG,01625500,NFM,,0,,,SCANNER_001,1,0,,1, 
MDL: MDL,BC125AT          PWR: PWR,418,01625500     SQL: SQL,0   
STS: STS,011000,          ,,SCANNER_001     ,,CH001  162.5500 ,,         ,,              ,,1            ,,1,0,0,0,,,5,,3
SUM: VER: VER,Version 1.06.06  VOL: VOL,0  WIN: WIN,85,01625500  EWP: EWP,ERR  JNT: JNT,ERR JPM: JPM,ERR KEY: KEY,ERR
MNU: MNU,ERR MRD: MRD,00000000,ERR QSH: QSH,ERR ULF: ULF,ERR

"""
# ------------------------------------------------------------------------------
# Command Definitions
# ------------------------------------------------------------------------------

commands = {
    "BAV": ScannerCommand(
        name="BAV",
        help="""
        Shows battery voltage (10mV units).
        example usage:
        >>> BAV
        <<< BAV,558
        """
    ),
    
    "BLT": ScannerCommand(
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
        """),
    
   "BPL": ScannerCommand(
        name="BPL",
        validator=validate_enum("BPL", ["0","1"]),
        requires_prg=True,
        help="""
        Unknown.  Likely selects the bandplan.
        Valid values:
        0: unkown
        1: unknown
        2: unknown
        """),    
   
   "BSV": ScannerCommand(
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

    "CIN": ScannerCommand(
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
    
    
    "CNT": ScannerCommand(
        name="CNT",
        valid_range=(1, 15),
        help="Set LCD contrast (1–15).",
        requires_prg=True
    ),
    
    "COM": ScannerCommand(
        name="COM",
        help="Possibly related to COM port config (undocumented). Use with caution.",
        requires_prg=True
    ),

    "CSG": ScannerCommand(
        name="CSG",
        help="Custom Search Group status (bitmask of 10 ranges).",
        requires_prg=True
    ),

    "CSP": ScannerCommand(
        name="CSP",
        help="Custom search parameters. Format: CSP,<index>,<low>,<high>",
        requires_prg=True
    ),

    "DCH": ScannerCommand(
        name="DCH",
        help="Delete channel. Format: DCH,<index> (1–500)",
        requires_prg=True
    ),

    "EPG": ScannerCommand(
        name="EPG",
        help="Exit programming mode."
    ),
    
    "EWP": ScannerCommand(
    name="EWP",
    help="Unknown usage"
    ),

    "ESN": ScannerCommand(
        name="ESN",
        help="Get scanner ESN (serial number). Returns long identifier."
    ),

    "FWM": ScannerCommand(
        name="FWM",
        help="Firmware maintenance command (unknown purpose)."
    ),

    "GLF": ScannerCommand(
        name="GLF",
        help="Get global lockout frequency. Repeated calls return next item until GLF,-1.",
        requires_prg=True
    ),

    "GLG": ScannerCommand(
        name="GLG",
        help="Reception status dump (format undocumented, experimental)"
    ),

    "JNT": ScannerCommand(
        name="JNT",
        help="Jump to channel number tag (undocumented, returns JNT,ERR)."
    ),

    "JPM": ScannerCommand(
        name="JPM",
        help="Jump mode command (undocumented, returns JPM,ERR)."
    ),   
   
   "KBP": ScannerCommand(
        name="KBP",
        set_format="KBP,{level},{lock}",
        help="Sets key beep (0:Auto, 99:Off) and key lock (0:Off, 1:On).",
        requires_prg=True
    ),
   
    "KEY": ScannerCommand(
        name="KEY",
        set_format="KEY,{value}",
        help="Simulate keypad input. E.g., KEY,1,P for pressing '1'."
    ),

    "LOF": ScannerCommand(
        name="LOF",
        help="Lock out a frequency (in kHz). Format: LOF,<frequency>",
        requires_prg=True
    ),

    "MDL": ScannerCommand(
        name="MDL",
        help="Returns scanner model (e.g., BC125AT)."
    ),

    "MMM": ScannerCommand(
        name="MMM",
        help="Mystery memory mode (not documented)."
    ),

    "MNU": ScannerCommand(
        name="MNU",
        help="Enters menu system (not supported in remote mode)."
    ),

    "MRD": ScannerCommand(
        name="MRD",
        help="Reads memory register (debug/test use)."
    ),

    "MWR": ScannerCommand(
        name="MWR",
        help="Write memory register (debug/test use)."
    ),

    "PDI": ScannerCommand(
        name="PDI",
        help="Possibly peripheral device interface. Undocumented."
    ),

    "PRG": ScannerCommand(
        name="PRG",
        help="Enter programming mode."
    ),


   "PRI": ScannerCommand(
        name="PRI",
        valid_range=(0, 3),
        help="Sets priority mode (0:Off, 1:On, 2:Plus, 3:DND).",
        requires_prg=True
    ),

    "PWR": ScannerCommand(
        name="PWR",
        help="Returns RSSI and current frequency. Format: PWR,<rssi>,<freq>"
    ),
 
   "QSH": ScannerCommand(
        name="QSH",
        help="Quick search hold mode (seems broken on BC125AT.  I've tried 42k permutations of commands)\nNext possibility is that it's a chained command or only available in certain modes."
    ),

    "SCG": ScannerCommand(
        name="SCG",
        help="Quick group lockout bitmask. Format: SCG,xxxxxxxxxx (each digit is 0 or 1)",
        requires_prg=True
    ),

    "SCO": ScannerCommand(
        name="SCO",
        help="Search/Close Call Options. Format: SCO,<delay>,<code_search>",
        requires_prg=True
    ),

    "SQL": ScannerCommand(
        name="SQL",
        valid_range=(0, 15),
        help="Set squelch level (0–15)."
    ),

    "SSG": ScannerCommand(
        name="SSG",
        help="Service search group (bitmask of 10 categories).",
        requires_prg=True
    ),

    "STS": ScannerCommand(
        name="STS",
        help="Returns scanner status snapshot (multi-field dump)."
    ),

    "SUM": ScannerCommand(
        name="SUM",
        help="Mystery summary command (appears in logs, unknown use)."
    ),

    "TST": ScannerCommand(
        name="TST",
        help="Enter test mode (be careful!)."
    ),

    "ULF": ScannerCommand(
        name="ULF",
        help="Unlock a global lockout frequency. Format: ULF,<frequency>",
        requires_prg=True
    ),

    "VER": ScannerCommand(
        name="VER",
        help="Returns firmware version."
    ),

    "VOL": ScannerCommand(
        name="VOL",
        valid_range=(0, 15),
        help="Set volume level (0–15)."
    ),

    "WIN": ScannerCommand(
        name="WIN",
        help="Returns window voltage + frequency (used internally)."
    ),

    "WXS": ScannerCommand(
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
