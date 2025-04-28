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

    # Placeholders for missing commands
    # "GLG": scanner_command(
    #     name="GLG",
    #     requires_prg=True,
    #     set_format="GLG,{group_mask}",
    #     validator=validate_param_constraints([]),
    #     help="""Get/Set Global Lockout Group.
    #
    #     Format:
    #     GLG - Get current global lockout group
    #     GLG,[GROUP_MASK] - Set global lockout group
    #     """,
    # ),

    # "MNU": scanner_command(
    #     name="MNU",
    #     requires_prg=False,
    #     set_format="MNU,{option}",
    #     validator=validate_param_constraints([]),
    #     help="""Access Menu.
    #
    #     Format:
    #     MNU - Enter menu mode
    #     MNU,[OPTION] - Select menu option
    #     """,
    # ),

    # "TST": scanner_command(
    #     name="TST",
    #     requires_prg=True,
    #     set_format="TST,{test_mode}",
    #     validator=validate_param_constraints([]),
    #     help="""Run Test Mode.
    #
    #     Format:
    #     TST - Run self test
    #     TST,[TEST_MODE] - Run specific test
    #     """,
    # ),

    "SCG": scanner_command(
        name="SCG",
        requires_prg=True,
        set_format="SCG,{status_mask}",
        validator=validate_param_constraints([]),
        help="""Get/Set Service Search Groups.
            Format:
        SCG - Get current service search group status
        SCG,[STATUS_MASK] - Set service search group status
        """,
    ),

    "SSG": scanner_command(
        name="SSG",
        requires_prg=True,
        set_format="SSG,{status_mask}",
        validator=validate_param_constraints([]),
        help="""Get/Set Service Search Group Settings.
            Format:
        SSG - Get current service search group settings
        SSG,[STATUS_MASK] - Set service search group settings
        """,
    ),
}

# Set source module for each command
for cmd in SYSTEM_COMMANDS.values():
    cmd.source_module = "SYSTEM_COMMANDS"
