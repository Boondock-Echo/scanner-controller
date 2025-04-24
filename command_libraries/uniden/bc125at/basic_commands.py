"""
Basic scanner commands for the BC125AT.

Basic commands include settings for backlight, battery save, contrast,
key beep, volume, squelch, power off, key press, and opening message.
These commands provide the fundamental interface for controlling the scanner's
basic functions and appearance settings.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_enum, validate_param_constraints

# Define validators for specific commands
validate_kbp = validate_param_constraints(
    [
        (
            int,
            lambda x: x == 99 or 0 <= x <= 15,
        ),  # beep level (0=Auto, 1-15, 99=OFF)
        (int, {0, 1}),  # lock (0=OFF, 1=ON)
    ]
)

BASIC_COMMANDS = {
    "BLT": scanner_command(
        name="BLT",
        validator=validate_enum("BLT", ["AO", "AF", "KY", "KS", "SQ"]),
        requires_prg=True,
        help="""Get/Set Backlight settings.

        Format:
        BLT - Get current backlight settings
        BLT,[MODE] - Set backlight mode

        Parameters:
        MODE : Backlight mode
        AO - Always On
        AF - Always Off
        KY - Key press only
        KS - Key press + squelch
        SQ - Squelch only

        Note: This command is only acceptable in Programming Mode.
        """,
    ),
    "BSV": scanner_command(
        name="BSV",
        valid_range=(1, 14),  # charge time (1-14)
        requires_prg=True,
        help="""Get/Set Battery Info.

        Format:
        BSV - Get current battery settings
        BSV,[CHARGE_TIME] - Set battery charge time

        Parameters:
        CHARGE_TIME : Battery charge time (1-14)
                      Increase the charge time based on the mAh of the batteries

        Note: This command is only acceptable in Programming Mode.
        """,
    ),
    "CNT": scanner_command(
        name="CNT",
        set_format="CNT,{mode}",
        validator=validate_param_constraints([(int, (1, 15))]),  # level (1-15)
        requires_prg=True,
        help="""Get/Set LCD Contrast Settings.

        Format:
        CNT - Get current contrast settings
        CNT,[MODE] - Set contrast mode

        Parameters:
        MODE : Contrast mode (1-15  [1:Low, 15:High])

        Note: This command is only acceptable in Programming Mode.
        """,
    ),
    "KBP": scanner_command(
        name="KBP",
        set_format="KBP,{level},{lock}",
        validator=validate_kbp,
        requires_prg=True,
        help="""Get/Set Key Beep and setting.

        Format:
        KBP - Get current key beep settings
        KBP,[LEVEL],[LOCK] - Set key beep and lock settings

        Parameters:
        LEVEL : Beep Level (0:Auto, 1-15, 99:OFF)
        LOCK : Key Lock status (0:OFF, 1:ON)

        Note: This command is only acceptable in Programming Mode.
        """,
    ),
    "VOL": scanner_command(
        name="VOL",
        set_format="VOL,{level}",
        validator=validate_param_constraints([(int, (0, 15))]),  # level (0-15)
        requires_prg=False,
        help="""Get/Set Volume Level Settings.

        Format:
        VOL - Get current volume level
        VOL,[LEVEL] - Set volume level (0-15)

        Parameters:
        LEVEL : Volume level (0-15)

        Note: When using a normalized scale (0.0-1.0):
        - 0.0 corresponds to minimum volume (0)
        - 1.0 corresponds to maximum volume (15)
        - To convert: level = int(normalized_value * 15)
        """,
    ),
    "SQL": scanner_command(
        name="SQL",
        set_format="SQL,{level}",
        validator=validate_param_constraints([(int, (0, 15))]),  # level (0-15)
        requires_prg=True,
        help="""Get/Set Squelch Level Settings.

        Format:
        SQL - Get current squelch level
        SQL,[LEVEL] - Set squelch level (0-15)

        Parameters:
        LEVEL : Squelch level (0:OPEN, 1-14, 15:CLOSE)

        Note: When using a normalized scale (0.0-1.0):
        - 0.0 corresponds to minimum squelch (0)
        - 1.0 corresponds to maximum squelch (15)
        - To convert: level = int(normalized_value * 15)
        """,
    ),
    "POF": scanner_command(
        name="POF",
        set_format="POF",
        validator=validate_param_constraints([]),  # no parameters
        requires_prg=False,
        help="""Power Off command.

        Format:
        POF - Turns off the scanner

        After this command, the scanner doesn't accept any command.
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
        """,
    ),
    "OMS": scanner_command(
        name="OMS",
        set_format="OMS,{line1},{line2},{line3},{line4}",
        validator=validate_param_constraints(
            [
                (str, lambda w: len(w) <= 16),  # line1 (max 16 chars)
                (str, lambda x: len(x) <= 16),  # line2 (max 16 chars)
                (str, lambda y: len(y) <= 16),  # line3 (max 16 chars)
                (str, lambda z: len(z) <= 16),  # line4 (max 16 chars)
            ]
        ),
        requires_prg=True,
        help="""Get/Set Opening Message.

        Format:
        OMS - Get current opening message
        OMS,[L1_CHAR],[L2_CHAR],[L3_CHAR],[L4_CHAR] - Set opening message

        Parameters:
        L1_CHAR : Line 1 text (max 16 characters)
        L2_CHAR : Line 2 text (max 16 characters)
        L3_CHAR : Line 3 text (max 16 characters)
        L4_CHAR : Line 4 text (max 16 characters)

        Note: If you set only spaces for a line, it will return to the default
        message. This command is only acceptable in Programming Mode.
        """,
    ),
}

# Set source module for each command
for cmd in BASIC_COMMANDS.values():
    cmd.source_module = "BASIC_COMMANDS"
