"""
Weather Alert related commands for the BCD325P2.

These commands configure NOAA weather scanning and SAME alert group settings.
"""

from scanner_controller.utilities.core.command_library import ScannerCommand
from scanner_controller.utilities.validators import validate_param_constraints

WEATHER_ALERT_COMMANDS = {
    "WXS": ScannerCommand(
        name="WXS",
        requires_prg=True,
        set_format="WXS,{dly},{att},{alt_pri},{rsv},{agc_analog},{rsv}",
        validator=validate_param_constraints(
            [
                (int, {-10, -5, -2, 0, 1, 2, 5, 10, 30}),  # delay time
                (int, {0, 1}),  # attenuation (0=OFF, 1=ON)
                (int, {0, 1}),  # alert priority (0=OFF, 1=ON)
                (str, None),  # rsv (reserved parameter)
                (int, {0, 1}),  # agc_analog (0=OFF, 1=ON)
                (str, None),  # rsv (reserved parameter)
            ]
        ),
        help="""Get/Set Weather Settings.

        Format:
        WXS - Get current weather settings
        WXS,[DLY],[ATT],[ALT_PRI],[RSV],[AGC_ANALOG],[RSV] - Set weather
        settings

        Parameters:
        DLY : Delay Time (-10,-5,-2,0,1,2,5,10,30)
        ATT : Attenuation (0=OFF, 1=ON)
        ALT_PRI : Weather Alert Priority (0=OFF, 1=ON)
        AGC_ANALOG : AGC Setting for Analog Audio (0=OFF, 1=ON)
        RSV : Reserved parameter
        """,
    ),
    "SGP": ScannerCommand(
        name="SGP",
        requires_prg=True,
        set_format=(
            "SGP,{same_index},{name},{fips1},{fips2},{fips3},{fips4},"
            "{fips5},{fips6},{fips7},{fips8}"
        ),
        validator=validate_param_constraints(
            [
                (int, (1, 5)),  # same_index (1-5)
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (
                    str,
                    lambda x: x == "------" or (len(x) == 6 and x.isdigit()),
                ),  # fips1
                (
                    str,
                    lambda x: x == "------" or (len(x) == 6 and x.isdigit()),
                ),  # fips2
                (
                    str,
                    lambda x: x == "------" or (len(x) == 6 and x.isdigit()),
                ),  # fips3
                (
                    str,
                    lambda x: x == "------" or (len(x) == 6 and x.isdigit()),
                ),  # fips4
                (
                    str,
                    lambda x: x == "------" or (len(x) == 6 and x.isdigit()),
                ),  # fips5
                (
                    str,
                    lambda x: x == "------" or (len(x) == 6 and x.isdigit()),
                ),  # fips6
                (
                    str,
                    lambda x: x == "------" or (len(x) == 6 and x.isdigit()),
                ),  # fips7
                (
                    str,
                    lambda x: x == "------" or (len(x) == 6 and x.isdigit()),
                ),  # fips8
            ]
        ),
        help="""Get/Set SAME Group Settings.

        Format:
        SGP,[SAME_INDEX] - Get SAME group settings
        SGP,[SAME_INDEX],[NAME],[FIPS1],[FIPS2],[FIPS3],[FIPS4],[FIPS5],
        [FIPS6],[FIPS7],[FIPS8] - Set SAME group

        Parameters:
        SAME_INDEX : SAME Index (1-5)
        NAME : SAME Group Name (max 16 chars)
        FIPS1-8 : FIPS Codes (6-digit: 000000-999999, or ------ means none)

        Notes:
        FIPS (Federal Information Processing Standards) codes are used for
        SAME (Specific Area Message Encoding) to target weather alerts to
        specific geographic areas.
        """,
    ),
}

# Set source module for each command
for cmd in WEATHER_ALERT_COMMANDS.values():
    cmd.source_module = "WEATHER_ALERT_COMMANDS"
