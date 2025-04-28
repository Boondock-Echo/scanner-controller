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
}

# Set source module for each command
for cmd in CONFIG_COMMANDS.values():
    cmd.source_module = "CONFIG_COMMANDS"
