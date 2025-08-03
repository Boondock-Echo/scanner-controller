"""
Scanner configuration commands for the BCD325P2.

These commands allow you to configure various scanner settings and options.
"""

from utilities.core.command_library import ScannerCommand
from utilities.validators import validate_param_constraints

SCANNER_CONFIGURATION_COMMANDS = {
    "SCN": ScannerCommand(
        name="SCN",
        requires_prg=True,
        set_format=(
            "SCN,{disp_mode},{rsv},{ch_log},{g_att},{rsv},{p25_lpf},{disp_uid}"
        ),
        validator=validate_param_constraints(
            [
                (int, {1, 2, 3}),  # display mode (1=MODE1, 2=MODE2, 3=MODE3)
                (str, None),  # rsv
                (int, {0, 1, 2}),  # ch_log (0=OFF, 1=ON, 2=Extend)
                (int, {0, 1}),  # g_att (0=OFF, 1=ON)
                (str, None),  # rsv
                (int, {0, 1}),  # p25_lpf (0=OFF, 1=ON)
                (int, {0, 1}),  # disp_uid (0=OFF, 1=ON)
            ]
        ),
        help="""Get/Set Scanner Option Settings.

        Format:
        SCN - Get current scanner settings
        SCN,[DISP_MODE],[RSV],[CH_LOG],[G_ATT],[RSV],[P25_LPF],[DISP_UID] -
        Set scanner options

        Parameters:
        DISP_MODE : Display mode (1:MODE1, 2:MODE2, 3:MODE3)
        RSV : Reserved parameter
        CH_LOG : Control Channel Logging (0:OFF, 1:ON, 2:Extend)
        G_ATT : Global attenuator (0:OFF, 1:ON)
        RSV : Reserved parameter
        P25_LPF : P25 Low Pass Filter (0:OFF, 1:ON)
        DISP_UID : Display Unit ID (0:OFF, 1:ON)
        """,
    ),
    "COM": ScannerCommand(
        name="COM",
        requires_prg=True,
        set_format="COM,{baud_rate},{flow_control}",
        validator=validate_param_constraints(
            [
                (int, {4800, 9600, 19200, 38400, 57600, 115200}),  # baud rate
                (int, {0, 1}),  # flow control (0=OFF, 1=ON)
            ]
        ),
        help="""Get/Set Serial Port Settings.

        Format:
        COM - Get current serial settings
        COM,[BAUD_RATE],[FLOW_CONTROL] - Set serial port settings

        Parameters:
        BAUD_RATE : Baud rate (4800, 9600, 19200, 38400, 57600, 115200)
        FLOW_CONTROL : Hardware flow control (0=OFF, 1=ON)

        Note: Changes to these settings will not take effect until after power
              cycling the scanner.
        """,
    ),
    "CLR": ScannerCommand(
        name="CLR",
        requires_prg=True,
        set_format="CLR,{clear_type}",
        validator=validate_param_constraints(
            [
                (
                    str,
                    {
                        "ALL",
                        "SYSTEM",
                        "SITE",
                        "GROUP",
                        "CHANNEL",
                        "LOCATION",
                        "CUSTOM",
                    },
                )
            ]
        ),
        help="""Clear Scanner Memory.

        Format:
        CLR,[CLEAR_TYPE] - Clear memory

        Parameters:
        CLEAR_TYPE : Type of memory to clear (ALL, SYSTEM, SITE, GROUP,
                    CHANNEL, LOCATION, CUSTOM)

        WARNING: This command will permanently erase memory and cannot be
        undone.
                Scanner will restart after executing this command.
        """,
    ),
    "PRI": ScannerCommand(
        name="PRI",
        requires_prg=False,
        set_format="PRI,{pri_mode}",
        validator=validate_param_constraints([(int, {0, 1, 2})]),
        help="""Get/Set Priority Mode.

        Format:
        PRI - Get current priority mode
        PRI,[PRI_MODE] - Set priority mode

        Parameters:
        PRI_MODE : Priority mode setting
                 0 = Priority OFF
                 1 = Priority ON
                 2 = Priority DND (Do Not Disturb)
        """,
    ),
    "AGV": ScannerCommand(
        name="AGV",
        requires_prg=True,
        set_format="AGV,{analog_agc},{digital_agc}",
        validator=validate_param_constraints(
            [
                (int, {0, 1}),  # analog AGC (0=OFF, 1=ON)
                (int, {0, 1}),  # digital AGC (0=OFF, 1=ON)
            ]
        ),
        help="""Get/Set Audio AGC Settings.

        Format:
        AGV - Get current AGC settings
        AGV,[ANALOG_AGC],[DIGITAL_AGC] - Set AGC settings

        Parameters:
        ANALOG_AGC : Analog Audio AGC (0=OFF, 1=ON)
        DIGITAL_AGC : Digital Audio AGC (0=OFF, 1=ON)
        """,
    ),
    "P25": ScannerCommand(
        name="P25",
        requires_prg=True,
        set_format="P25,{threshold},{digital_agc},{ignore_errors}",
        validator=validate_param_constraints(
            [
                (int, (0, 20)),  # threshold (0-20)
                (int, {0, 1}),  # digital AGC (0=OFF, 1=ON)
                (int, {0, 1}),  # ignore errors (0=OFF, 1=ON)
            ]
        ),
        help="""Get/Set P25 Digital Settings.

        Format:
        P25 - Get current P25 settings
        P25,[THRESHOLD],[DIGITAL_AGC],[IGNORE_ERRORS] - Set P25 settings

        Parameters:
        THRESHOLD : P25 decode threshold (0-20, default is 5)
        DIGITAL_AGC : Digital Audio AGC (0=OFF, 1=ON)
        IGNORE_ERRORS : Ignore P25 errors (0=OFF, 1=ON)
        """,
    ),
}

# Set source module for each command
for cmd in SCANNER_CONFIGURATION_COMMANDS.values():
    cmd.source_module = "SCANNER_CONFIGURATION_COMMANDS"
