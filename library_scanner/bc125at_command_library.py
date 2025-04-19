"""
BC125AT Command Library.

This module defines the command structure and API for the BC125AT scanner.
It includes command definitions, validators, and helper functions for
interacting with the scanner.
"""

# Import commands from the specific command library
from command_libraries.uniden.bc125at_commands import commands

# ------------------------------------------------------------------------------
# Command Definitions
# ------------------------------------------------------------------------------

"""
BC125AT Command Library.

This file defines the BC125AT-specific command structure, including valid
ranges, query/set formats, help descriptions, and optional validators or
parsers.

It is used by:
- The BC125ATAdapter to build and parse commands
- The main program to support contextual help (via getHelp)

# search of all 3 letter commands commands (except PRG, POF, ) yielded the
# following
BLT: BLT,NG  BPL: BPL,NG  BSV: BSV,NG  CIN: CIN,NG  CLC: CLC,NG  CLR: CLR,NG
CNT: CNT,NG  COM: COM,NG  CSG: CSG,NG  CSP: CSP,NG  DCH: DCH,NG  FWM: FWM,NG
KBP: KBP,NG  LOF: LOF,NG  MMM: MMM,NG  MWR: MWR,NG  PDI: PDI,NG  PRI: PRI,NG
SCG: SCG,NG  SCO: SCO,NG  SSG: SSG,NG  TST: TST,NG  WXS: WXS,NG  BAV: BAV,558
EPG: EPG,OK  ESN: ESN,XXXXXXXXXXXXXX,000,1
GLF: GLF,-1  GLG: GLG,01625500,NFM,,0,,,SCANNER_001,1,0,,1,
MDL: MDL,BC125AT          PWR: PWR,418,01625500     SQL: SQL,0
STS: STS,011000,          ,,SCANNER_001     ,,CH001  162.5500 ,,         ,
,              ,,1            ,,1,0,0,0,,,5,,3
SUM: VER: VER,Version 1.06.06  VOL: VOL,0  WIN: WIN,85,01625500  EWP: EWP,ERR
JNT: JNT,ERR JPM: JPM,ERR KEY: KEY,ERR MNU: MNU,ERR MRD: MRD,00000000,ERR
QSH: QSH,ERR ULF: ULF,ERR
"""

# ------------------------------------------------------------------------------
# Public API
# ------------------------------------------------------------------------------


def getHelp(command):
    """
    Return the help string for the specified command (case-insensitive).

    Returns None if command is not defined.
    """
    cmd = commands.get(command.upper())
    return cmd.help if cmd else None


def listCommands():
    """Return a sorted list of all available command names."""
    return sorted(commands.keys())
