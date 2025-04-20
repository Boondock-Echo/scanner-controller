"""
Basic scanner commands for the BCD325P2.
"""

from utilities.core.shared_utils import scanner_command
from utilities.validators import validate_param_constraints

BASIC_COMMANDS = {
    "BLT": scanner_command(
        name="BLT",
        requires_prg=True,
        set_format="BLT,{event},{rsv},{dimmer}",
        validator=validate_param_constraints(
            [
                (str, {"IF", "10", "30", "KY", "SQ"}),  # event type
                (str, None),  # rsv (reserve parameter)
                (int, {1, 2, 3}),  # dimmer (1=Low, 2=Middle, 3=High)
            ]
        ),
        help="""Get/Set Backlight settings.

        Format:
        BLT - Get current backlight settings
        BLT,[EVNT],[RSV],[DIMMER] - Set backlight

        Parameters:
        EVNT : Event type (IF:INFINITE, 10:10sec, 30:30sec, KY:KEYPRESS,
        SQ:SQUELCH)
        DIMMER : Backlight dimmer level (1:Low, 2:Middle, 3:High)
        """,
    ),
    "BSV": scanner_command(
        name="BSV",
        requires_prg=True,
        set_format="BSV,{bat_save},{charge_time}",
        validator=validate_param_constraints(
            [
                (int, {0, 1}),  # battery save (0=OFF, 1=ON)
                (int, (1, 16)),  # charge time (1-16)
            ]
        ),
        help="""Get/Set Battery Info.

        Format:
        BSV - Get current battery settings
        BSV,[BAT_SAVE],[CHARGE_TIME] - Set battery options

        Parameters:
        BAT_SAVE : Battery save mode (0:OFF, 1:ON)
        CHARGE_TIME : Battery charge time (1-16)
        """,
    ),
    "CNT": scanner_command(
        name="CNT",
        set_format="CNT,{mode}",
        validator=validate_param_constraints([(int, (1, 16))]),  # level (1-16)
        requires_prg=True,
        help="""
        Get/Set contrast.

        Format:
        CNT - Get current contrast settings
        CNT,[MODE] - Set contrast mode

        Parameters:
        MODE : Contrast mode (1-16  [1:Low, 16:High])
        """,
    ),
    "KBP": scanner_command(
        name="KBP",
        set_format="KBP,{level},{lock},{safe}",
        validator=validate_param_constraints(
            [
                (
                    int,
                    lambda x: (x == 99 or 0 <= x <= 15),
                ),  # beep level (0=Auto, 1-15, 99=OFF)
                (int, {0, 1}),  # lock (0=OFF, 1=ON)
                (int, {0, 1}),  # safe (0=OFF, 1=ON)
            ]
        ),
        requires_prg=True,
        help="Sets key beep (0:Auto, 99:Off) and key lock (0:Off, 1:On).",
    ),
    "VOL": scanner_command(
        name="VOL",
        set_format="VOL,{level}",
        validator=validate_param_constraints([(int, (0, 15))]),  # level (0-15)
        requires_prg=False,
        help="""
        Get/Set volume.

        Format:
        VOL - Get current volume level
        VOL,[LEVEL] - Set volume level (0-15)
        """,
    ),
    "SQL": scanner_command(
        name="SQL",
        set_format="SQL,{level}",
        validator=validate_param_constraints([(int, (0, 15))]),  # level (0-15)
        requires_prg=True,
        help="""
        Get/Set squelch.

        Format:
        SQL - Get current squelch level
        SQL,[LEVEL] - Set squelch level (0-15)
        """,
    ),
    "POF": scanner_command(
        name="POF",
        set_format="POF",
        validator=validate_param_constraints([]),  # no parameters
        requires_prg=False,
        help="""
        Power Off command.
        """,
    ),
    "KEY": scanner_command(
        name="KEY",
        set_format="KEY,{key}",
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
        help="""
        Key command.
        Format:
        KEY,[KEY] - Set key value (0-9) to be pressed.
        Example: KEY,0 - Press key 0.

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
        message.
        """,
    ),
}
# KBP, BLT, BSV, CNT, VOL, SQL, POF, KEY, OMS
