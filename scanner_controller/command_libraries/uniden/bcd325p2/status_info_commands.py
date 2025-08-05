"""
Status and Information commands for the BCD325P2.

These commands retrieve status information from the scanner including
reception status, RSSI levels, display information, and version details.
"""

from scanner_controller.utilities.core.command_library import ScannerCommand

STATUS_INFO_COMMANDS = {
    "GID": ScannerCommand(
        name="GID",
        requires_prg=False,
        set_format="GID",
        help="""Get Current TalkGroup ID Status.

        Format:
        GID - Get current TGID status

        Returns:
        GID,[SITE_TYPE],[TGID],[ID_SRCH_MODE],[NAME1],[NAME2],[NAME3]

        Parameters:
        SITE_TYPE : Site Type (CNV, MOT, EDC, EDS, LTR, P25S, P25F, TRBO, DMR)
        TGID : TGID (if available)
        ID_SRCH_MODE : ID SCAN/ID SEARCH Mode (0:ID SCAN Mode, 1:ID SEARCH Mode)
        NAME1 : SYSTEM/SITE NAME
        NAME2 : GROUP NAME
        NAME3 : TGID NAME

        Returns empty values (,,,,) when TGID is not displayed.
        """,
    ),
    "PWR": ScannerCommand(
        name="PWR",
        requires_prg=False,
        set_format="PWR",
        help="""Get RSSI Level.

        Format:
        PWR - Get current RSSI level and frequency

        Returns:
        PWR,[RSSI],[FRQ]

        Parameters:
        RSSI : RSSI A/D Value (0-1023)
        FRQ : Current Frequency
        """,
    ),
    "STS": ScannerCommand(
        name="STS",
        requires_prg=False,
        set_format="STS",
        help="""Get Current Status.

        Format:
        STS - Get current scanner status

        Returns comprehensive scanner status information including:
        - Display form and contents
        - Squelch status
        - Mute status
        - Battery status
        - Weather alert status
        - Signal level
        - Backlight color and dimmer level

        The response format is complex and includes display data for each line
        on the scanner's screen along with status flags.
        """,
    ),
    "GLG": ScannerCommand(
        name="GLG",
        requires_prg=False,
        set_format="GLG",
        help="""Get Reception Status.

        Format:
        GLG - Get reception status

        Returns:
        GLG,[FRQ/TGID],[MOD],[ATT],[CTCSS/DCS],[NAME1],[NAME2],[NAME3],[SQL],
        [MUT],[SYS_TAG],[CHAN_TAG],[P25NAC]

        Parameters:
        FRQ/TGID : Frequency or TGID
        MOD : Modulation (AM/FM/NFM/WFM/FMB)
        ATT : Attenuation (0:OFF, 1:ON)
        CTCSS/DCS : CTCSS/DCS Status (0-231)
        NAME1 : System, Site or Search Name
        NAME2 : Group Name
        NAME3 : Channel Name
        SQL : Squelch Status (0:CLOSE, 1:OPEN)
        MUT : Mute Status (0:OFF, 1:ON)
        SYS_TAG : Current system number tag (0-999/NONE)
        CHAN_TAG : Current channel number tag (0-999/NONE)
        P25NAC : P25 NAC/Color Code Status
                (0-FFF: NAC, 1000-100F: Color Code, NONE: NAC/Color Code None)

        Returns empty values when no reception is active.
        """,
    ),
    "MDL": ScannerCommand(
        name="MDL",
        requires_prg=False,
        set_format="MDL",
        help="""Get Model Info.

        Format:
        MDL - Get scanner model information

        Returns:
        MDL,BCD325P2
        """,
    ),
    "VER": ScannerCommand(
        name="VER",
        requires_prg=False,
        set_format="VER",
        help="""Get Firmware Version.

        Format:
        VER - Get scanner firmware version

        Returns:
        VER,Version X.XX.XX (current firmware version)
        """,
    ),
}

# Set source module for each command
for cmd in STATUS_INFO_COMMANDS.values():
    cmd.source_module = "STATUS_INFO_COMMANDS"
