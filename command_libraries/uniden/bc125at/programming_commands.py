"""
Programming mode control commands for the BC125AT.

These commands handle entering and exiting the scanner's programming mode,
which is required for most configuration operations.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

PROGRAMMING_COMMANDS = {
    "PRG": scanner_command(
        name="PRG",
        requires_prg=False,
        set_format="PRG",
        validator=validate_param_constraints([]),  # no parameters
        help="""Enter Programming Mode.

        Format:
        PRG - Enter scanner programming mode

        Response:
        PRG,OK - Successfully entered programming mode
        PRG,NG - Failed to enter programming mode

        Notes:
        - The scanner displays "Remote Mode" on first line and "Keypad Lock" on
            second line
        - This command is invalid when the scanner is in Menu Mode, during
            Direct Entry operation,
          or during Quick Save operation
        - Many commands require the scanner to be in programming mode
        """,
    ),
    "EPG": scanner_command(
        name="EPG",
        requires_prg=True,
        set_format="EPG",
        validator=validate_param_constraints([]),  # no parameters
        help="""Exit Programming Mode.

        Format:
        EPG - Exit scanner programming mode

        Response:
        EPG,OK - Successfully exited programming mode

        Notes:
        - The scanner exits from Program Mode and goes to Scan Hold Mode
        - All programming mode only commands will be unavailable after this
            command
        """,
    ),
}

# Set source module for each command
for cmd in PROGRAMMING_COMMANDS.values():
    cmd.source_module = "PROGRAMMING_COMMANDS"
