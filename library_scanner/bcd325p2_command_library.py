"""
This module defines the BCD325P2 scanner command library.

It includes command definitions and a public API for retrieving command help
and listing commands.
"""

from library_scanner.commands.commands_uniden_bcd325p2 import commands

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
ABP: ABP,NG     ACC: ACC,NG     ACT: ACT,NG     AGC: AGC,NG     AGT: AGT,NG
AGV: AGV,NG     AOP: AOP,NG     AST: AST,NG     BAV: BAV,480    BBS: BBS,NG
BLT: BLT,NG     BSP: BSP,NG     BSV: BSV,NG     CBP: CBP,NG     CIE: CIE,NG
CIN: CIN,NG     CLA: CLA,NG     CLC: CLC,NG     CLR: CLR,NG     CNT: CNT,NG
COM: COM,NG     CSC: CSC,ERR    CSG: CSG,NG     CSP: CSP,NG     CSY: CSY,NG
DBC: DBC,NG     DCH: DCH,NG     DGR: DGR,NG     DLA: DLA,NG     DSY: DSY,NG
EPG: EPG,OK     ESN: ESN,37902048001926,0F0,1   EWP: EWP,ERR    FSC: FSC,OK
FWD: FWD,NG     FWM: FWM,NG     GCM: GCM,NG     GDO: GDO,NG     GID: GID,,,,,,
GIE: GIE,NG     GIN: GIN,NG     GLF: GLF,-1     GLG: GLG,,,,,,,,,,,, GLI: GLI,NG
JNT: JNT,ERR    JPM: JPM,ERR    KBP: KBP,NG     KEY: KEY,ERR    LCT: LCT,NG
LIH: LIH,NG     LIN: LIN,NG     LIT: LIT,NG     LOF: LOF,NG     LOI: LOI,NG
MCP: MCP,NG     MDL: MDL,BCD325P2 MEM: MEM,NG   MMM: MMM,NG     MNU: MNU,ERR
MRD: MRD,00000000,ERR           MWR: MWR,NG     OMS: OMS,NG     PDI: PDI,NG
POF: POF,OK     PRI: PRI,NG     PRG: PRG,OK     PWR: PWR,241,04623875
QGL: QGL,NG     QSC: QSC,ERR    QSH: QSH,ERR    QSL: QSL,NG     REV: REV,NG
RIE: RIE,NG     RMB: RMB,NG     SCN: SCN,NG     SCO: SCO,NG     SCT: SCT,NG
SGP: SGP,NG     SHK: SHK,NG     SIF: SIF,NG     SIH: SIH,NG     SIN: SIN,NG
SIT: SIT,NG     SLI: SLI,NG     SQL: SQL,1      SSP: SSP,NG     STS: STS,011000,
            ,,Qck Save Grp    ,,FireWatch       ,, 462.3875 DCS331,,S0:---------
            ,,GRP----------   ,,1,1,0,0,0,0,0,RED,0
SUM: SUM,00ACH  TFQ: TFQ,NG     TIN: TIN,NG     TON: TON,NG     TRN: TRN,NG
TST: TST,NG       ULF: ULF,ERR      ULI: ULI,NG       VER: VER,Version 1.09.12
VOL: VOL,0        WIN: WIN,86,04623875           WXS: WXS,NG
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
    """
    Retrieve and return a sorted list of all available command names.

    Returns:
        list: Sorted list of command names.
    """
    return sorted(commands.keys())
