"""
Status query commands for the BC125AT.

These commands retrieve status information from the scanner including model
information, firmware version, and other system details.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

STATUS_COMMANDS = {
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
    "KEY": scanner_command(
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
    "QSH": scanner_command(
        name="QSH",
        requires_prg=False,
        set_format="QSH,{frequency},{modulation},{attenuation}",
        validator=validate_param_constraints(
            [
                (int, lambda x: 25000 <= x <= 512000),  # frequency in kHz
                (str, {"AUTO", "AM", "FM", "NFM"}),  # modulation
                (int, {0, 1}),  # attenuation (0=OFF, 1=ON)
            ]
        ),
        help="""Quick Search Hold.

        Format:
        QSH,[FRQ],[MOD],[ATT] - Enter quick search hold mode at specified
        frequency

        Parameters:
        FRQ : Frequency in kHz (25000-512000)
        MOD : Modulation (AUTO, AM, FM, NFM)
        ATT : Attenuation (0=OFF, 1=ON)

        Examples:
        QSH,155625,FM,0 - Hold on 155.625 MHz with FM modulation and attenuation
        off

        Notes:
        - Puts the scanner in Quick Search Hold mode at the specified frequency
        - Allows direct tuning to a specific frequency
        """,
    ),
}

# Set source module for each command
for cmd in STATUS_COMMANDS.values():
    cmd.source_module = "STATUS_COMMANDS"
