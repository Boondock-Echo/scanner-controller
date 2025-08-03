"""
Basic scanner commands for the BC125AT.

Basic commands include settings for backlight, battery save, contrast,
key beep, volume, squelch, power off, key press, and opening message.
These commands provide the fundamental interface for controlling the scanner's
basic functions and appearance settings.
"""

from utilities.core.command_library import ScannerCommand
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
    "BLT": ScannerCommand(
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
    "BSV": ScannerCommand(
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
    "CNT": ScannerCommand(
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
    "KBP": ScannerCommand(
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
    "VOL": ScannerCommand(
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
    "SQL": ScannerCommand(
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
    "BPL": ScannerCommand(
        name="BPL",
        requires_prg=True,
        set_format="BPL,{level}",
        validator=validate_param_constraints([]),
        help="""Get/Set Bandplan.

        Format:
        BPL - Get current bandplan settings
        BPL,[SETTING] - Set bandplan

        Parameters:
        SETTING : Unknown at this time.
        """,
    ),
    "BAV": ScannerCommand(
        name="BAV",
        requires_prg=False,
        set_format="BAV",
        validator=validate_param_constraints([]),
        help="""Get Battery Voltage.

        Format:
        BAV - Get current battery voltage
        """,
    ),
    "PWR": ScannerCommand(
        name="PWR",
        requires_prg=False,
        set_format="PWR,{status}",
        validator=validate_param_constraints([]),
        help="""Get/Set Power Status.

        Format:
        PWR - Get current power status
        PWR,[STATUS] - Set power status
        """,
    ),
}

# Set source module for each command
for cmd in BASIC_COMMANDS.values():
    cmd.source_module = "BASIC_COMMANDS"
