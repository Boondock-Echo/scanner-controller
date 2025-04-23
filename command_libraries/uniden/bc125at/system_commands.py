"""
System-wide commands for the BC125AT.

These commands control system-wide settings such as priority scanning modes,
channel group settings, and other global functions.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

SYSTEM_COMMANDS = {
    "PRI": scanner_command(
        name="PRI",
        requires_prg=True,
        set_format="PRI,{pri_mode}",
        validator=validate_param_constraints(
            [(int, {0, 1, 2, 3})]  # priority mode (0-3)
        ),
        help="""Get/Set Priority Mode.

        Format:
        PRI - Get priority mode setting
        PRI,[PRI_MODE] - Set priority mode

        Parameters:
        PRI_MODE : Priority Mode (0:OFF, 1:ON, 2:PLUS ON, 3:DND)
                   DND = Do Not Disturb mode

        Examples:
        PRI,0 - Turn priority mode off
        PRI,1 - Turn priority mode on
        PRI,2 - Turn priority plus mode on

        Notes:
        - Priority mode lets the scanner check priority channels regularly
        - Priority Plus gives even more frequent priority checks
        - DND only checks priority during reception pauses
        - This command is only acceptable in Programming Mode
        """,
    ),
    "SCG": scanner_command(
        name="SCG",
        requires_prg=True,
        set_format="SCG,{status_mask}",
        validator=validate_param_constraints(
            [
                (
                    str,
                    lambda x: len(x) == 10 and all(c in "01" for c in x),
                )  # 10-digit binary mask
            ]
        ),
        help="""Get/Set Channel Storage Bank Status.

        Format:
        SCG - Get current bank status
        SCG,[STATUS_MASK] - Set bank status

        Parameters:
        STATUS_MASK : 10-digit binary mask where each digit is 0 or 1
                     0 = Valid (enabled), 1 = Invalid (disabled)
                     The order matches scanner banks 1-9,0 (where 0 is bank 10)

        Examples:
        SCG,0000000000 - Enable all banks
        SCG,1000000000 - Disable bank 1, enable all others
        SCG,0000000001 - Disable bank 10, enable all others

        Notes:
        - Controls which channel storage banks are enabled/disabled
        - Cannot set all banks to disabled ("1111111111")
        - This command is only acceptable in Programming Mode
        """,
    ),
    "SSG": scanner_command(
        name="SSG",
        requires_prg=True,
        set_format="SSG,{status_mask}",
        validator=validate_param_constraints(
            [
                (
                    str,
                    lambda x: len(x) == 10 and all(c in "01" for c in x),
                )  # 10-digit binary mask
            ]
        ),
        help="""Get/Set Service Search Group.

        Format:
        SSG - Get current service search status
        SSG,[STATUS_MASK] - Set service search status

        Parameters:
        STATUS_MASK : 10-digit binary mask where each digit is 0 or 1
                     0 = Valid (enabled), 1 = Invalid (disabled)
                     Order of service search groups:
                     |||||||||+-- Racing
                     ||||||||+--- FRS/GMRS/MURS
                     |||||||+---- CB Radio
                     ||||||+----- Military Air
                     |||||+------ Civil Air
                     ||||+------- Railroad
                     |||+-------- Marine
                     ||+--------- Ham Radio
                     |+---------- Fire/Emergency
                     +----------- Police

        Examples:
        SSG,0000000000 - Enable all service search groups
        SSG,0000000001 - Disable Racing search, enable all others

        Notes:
        - Cannot set all service search groups to invalid ("1111111111")
        - This command is only acceptable in Programming Mode
        """,
    ),
    "COM": scanner_command(
        name="COM",
        requires_prg=True,
        set_format="COM,{baud_rate}",
        validator=validate_param_constraints(
            [(int, {4800, 9600, 19200, 38400, 57600, 115200})]  # baud rate
        ),
        help="""Get/Set Serial Port Settings.

        Format:
        COM - Get current serial port settings
        COM,[BAUD_RATE] - Set serial port baud rate

        Parameters:
        BAUD_RATE : Baud rate (4800, 9600, 19200, 38400, 57600, 115200)

        Examples:
        COM,9600 - Set baud rate to 9600 bps
        COM,115200 - Set baud rate to 115200 bps

        Notes:
        - Changes to COM port settings will take effect after power cycling the
            scanner
        - Use with caution as incorrect settings may affect scanner
            communication
        - This command is only acceptable in Programming Mode
        """,
    ),
}

# Set source module for each command
for cmd in SYSTEM_COMMANDS.values():
    cmd.source_module = "SYSTEM_COMMANDS"
