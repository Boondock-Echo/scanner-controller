"""
Configuration and control commands for the BC125AT.

These commands handle various scanner configuration settings and operations
including COM port settings, clearing memory, and power management.
These commands provide core functionality for managing the BC125AT scanner's
operation.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

CONFIG_COMMANDS = {
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

        Notes:
        - Changes to COM port settings will take effect after power cycling the
        scanner
        - Use with caution as incorrect settings may affect scanner
        communication
        - This command is only acceptable in Programming Mode
        """,
    ),
    "CLR": scanner_command(
        name="CLR",
        requires_prg=True,
        set_format="CLR",
        validator=validate_param_constraints([]),  # no parameters
        help="""Clear All Memory.

        Format:
        CLR - Reset all scanner memory to initial settings

        Response:
        CLR,OK - Successfully reset all memory

        Notes:
        - This command will erase ALL scanner memory and restore factory
            defaults
        - Operation takes several seconds to complete
        - This is a destructive operation that cannot be undone
        - This command is only acceptable in Programming Mode
        """,
    ),
    "POF": scanner_command(
        name="POF",
        requires_prg=False,
        set_format="POF",
        validator=validate_param_constraints([]),  # no parameters
        help="""Power Off Command.

        Format:
        POF - Turn off the scanner

        Response:
        POF,OK - Acknowledgment before powering off

        Notes:
        - This command powers off the scanner immediately
        - After this command, the scanner doesn't accept any further commands
        """,
    ),
    "MDL": scanner_command(
        name="MDL",
        requires_prg=False,
        set_format="MDL",
        validator=validate_param_constraints([]),  # no parameters
        help="""Get Model Info.

        Format:
        MDL - Get scanner model information

        Response:
        MDL,BC125AT - Returns model information

        Notes:
        - Returns the model name of the scanner
        - Can be used to verify communication and identify the scanner model
        """,
    ),
    "VER": scanner_command(
        name="VER",
        requires_prg=False,
        set_format="VER",
        validator=validate_param_constraints([]),  # no parameters
        help="""Get Firmware Version.

        Format:
        VER - Get scanner firmware version

        Response:
        VER,Version x.xx.xx - Returns firmware version

        Notes:
        - Returns the current firmware version of the scanner
        - Useful for verifying compatibility with software and features
        """,
    ),
}

# Set source module for each command
for cmd in CONFIG_COMMANDS.values():
    cmd.source_module = "CONFIG_COMMANDS"
