"""
Status query commands for the BC125AT.

These commands retrieve status information from the scanner including model
information, firmware version, and other system details.
"""

from utilities.core.command_library import ScannerCommand
from utilities.validators import validate_param_constraints

STATUS_COMMANDS = {
    "MDL": ScannerCommand(
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
    "VER": ScannerCommand(
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
    "KEY": ScannerCommand(
        name="KEY",
        set_format="KEY,{value}",
        validator=validate_param_constraints(
            [
                (
                    str,
                    {
                        "0",
                        "1",
                        "2",
                        "3",
                        "4",
                        "5",
                        "6",
                        "7",
                        "8",
                        "9",
                        ".",
                        "E",
                        "H",
                        "S",
                        "L",
                        "M",
                        "F",
                    },
                )
            ]
        ),
        requires_prg=False,
        help="""Push KEY command.

        Format:
        KEY,[KEY] - Simulates pressing a key on the scanner

        Valid key values:
        0-9 : Numeric keys
        .   : . (decimal point)
        E   : E/yes/gps key
        H   : Hold key
        S   : Scan/srch key
        L   : L/O key
        M   : Menu key
        F   : Func key

        Examples:
        KEY,5 - Press key 5
        KEY,M - Press Menu key
        KEY,F - Press Function key

        Notes:
        - Used to remotely control the scanner
        - Simulates physical button presses
        """,
    ),
    # Placeholders for missing commands
    # "ESN": ScannerCommand(
    #     name="ESN",
    #     requires_prg=False,
    #     set_format="ESN",
    #     validator=validate_param_constraints([]),
    #     help="""Get Electronic Serial Number.
    #
    #     Format:
    #     ESN - Get scanner electronic serial number
    #     """,
    # ),
    #
    # "STS": ScannerCommand(
    #     name="STS",
    #     requires_prg=False,
    #     set_format="STS",
    #     validator=validate_param_constraints([]),
    #     help="""Get Current Status.
    #
    #     Format:
    #     STS - Get current scanner status
    #     """,
    # ),
    #
    # "SUM": ScannerCommand(
    #     name="SUM",
    #     requires_prg=True,
    #     set_format="SUM",
    #     validator=validate_param_constraints([]),
    #     help="""Get/Set Survey Mode.
    #
    #     Format:
    #     SUM - Get survey mode status
    #     SUM,[SETTING] - Set survey mode
    #     """,
    # ),
    #
    # "WIN": ScannerCommand(
    #     name="WIN",
    #     requires_prg=False,
    #     set_format="WIN",
    #     validator=validate_param_constraints([]),
    #     help="""Get Window Position.
    #
    #     Format:
    #     WIN - Get current window position
    #     """,
    # ),
}

# Set source module for each command
for cmd in STATUS_COMMANDS.values():
    cmd.source_module = "STATUS_COMMANDS"
