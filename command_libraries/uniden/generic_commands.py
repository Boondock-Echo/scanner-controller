"""Generic command definitions for Uniden scanners."""

from utilities.core.command_library import ScannerCommand
from utilities.validators import validate_param_constraints

commands = {
    "MDL": ScannerCommand(
        name="MDL",
        requires_prg=False,
        set_format="MDL",
        validator=validate_param_constraints([]),
        help="""Get Model Info.

        Format:
        MDL - Get scanner model information

        Response:
        MDL,<MODEL_NAME>
        """,
    ),
    "VER": ScannerCommand(
        name="VER",
        requires_prg=False,
        set_format="VER",
        validator=validate_param_constraints([]),
        help="""Get Firmware Version.

        Format:
        VER - Get scanner firmware version

        Response:
        VER,<VERSION_STRING>
        """,
    ),
    "VOL": ScannerCommand(
        name="VOL",
        set_format="VOL,{level}",
        validator=validate_param_constraints([(int, (0, 15))]),
        requires_prg=False,
        help="""Get/Set Volume Level.

        Format:
        VOL - Get current volume level
        VOL,[LEVEL] - Set volume level (0-15)

        Parameters:
        LEVEL : Volume level (0-15)
        """,
    ),
    "SQL": ScannerCommand(
        name="SQL",
        set_format="SQL,{level}",
        validator=validate_param_constraints([(int, (0, 15))]),
        requires_prg=True,
        help="""Get/Set Squelch Level.

        Format:
        SQL - Get current squelch level
        SQL,[LEVEL] - Set squelch level (0-15)

        Parameters:
        LEVEL : Squelch level (0:OPEN, 1-14, 15:CLOSE)
        """,
    ),
}


for cmd in commands.values():
    cmd.source_module = "commands"


def get_help(command):
    """Return help text for ``command`` if available."""
    cmd = commands.get(command.upper())
    return cmd.help if cmd else None


def list_commands():
    """Return a sorted list of available command names."""
    return sorted(commands.keys())
