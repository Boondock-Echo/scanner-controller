"""
Specialized function commands for the BCD325P2.

These commands provide functionality for band scope, tone-out,
band coverage settings, and broadcast screen configuration.
"""

from scanner_controller.utilities.core.command_library import ScannerCommand
from scanner_controller.utilities.validators import (
    validate_param_constraints,
    validate_frequency_8_digit,
)

SPECIALIZED_COMMANDS = {
    "BSP": ScannerCommand(
        name="BSP",
        requires_prg=True,
        set_format="BSP,{freq},{step},{span},{max_hold}",
        validator=validate_param_constraints(
            [
                (str, validate_frequency_8_digit),  # frequency
                (
                    int,
                    {
                        500,
                        625,
                        750,
                        833,
                        1000,
                        1250,
                        1500,
                        2000,
                        2500,
                        5000,
                        10000,
                    },
                ),  # step
                (
                    str,
                    {
                        "0.2M",
                        "0.4M",
                        "0.6M",
                        "0.8M",
                        "1M",
                        "2M",
                        "4M",
                        "6M",
                        "8M",
                        "10M",
                        "20M",
                        "40M",
                        "60M",
                        "80M",
                        "100M",
                        "120M",
                        "140M",
                        "160M",
                        "180M",
                        "200M",
                        "250M",
                        "300M",
                        "350M",
                        "400M",
                        "450M",
                        "500M",
                    },
                ),  # span
                (int, {0, 1}),  # max_hold
            ]
        ),
        help="""Get/Set Band Scope System Settings.

        Format:
        BSP - Get current settings
        BSP,[FRQ],[STP],[SPN],[MAX_HOLD] - Set Band Scope

        Parameters:
        FRQ : Center Frequency
        STP : Step (500:5kHz, 625:6.25kHz, 750:7.5kHz, 833:8.33kHz,
              1000:10kHz, etc.)
        SPN : Sweep Span (0.2M to 500M)
        MAX_HOLD : Max hold display (0:OFF, 1:ON)
        """,
    ),
    "TON": ScannerCommand(
        name="TON",
        requires_prg=True,
        set_format=(
            "TON,{index},{name},{freq},{mod},{att},{dly},{alt},{altl},{tone_a},"
            "{rsv},{tone_b},{rsv},{rsv},{rsv},{alt_color},{alt_pattern},"
            "{agc_analog},{rsv},{rsv}"
        ),
        validator=validate_param_constraints(
            [
                (int, lambda x: 1 <= x <= 10),  # index (1-9, 0 means 10)
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (int, None),  # freq
                (str, {"AUTO", "FM", "NFM"}),  # mod
                (int, {0, 1}),  # att (0:OFF, 1:ON)
                (str, {"0", "1", "2", "5", "10", "30", "INF"}),  # dly
                (
                    int,
                    lambda x: x == 0 or 1 <= x <= 9,
                ),  # alt (0:OFF, 1-9:Tone No.)
                (int, lambda x: x == 0 or 1 <= x <= 15),  # altl (0:AUTO, 1-15)
                (int, None),  # tone_a frequency
                (str, None),  # rsv
                (int, None),  # tone_b frequency
                (str, None),  # rsv
                (str, None),  # rsv
                (str, None),  # rsv
                (str, {"OFF", "RED"}),  # alt_color
                (int, {0, 1, 2}),  # alt_pattern (0:ON, 1:Slow, 2:Fast)
                (int, {0, 1}),  # agc_analog (0:OFF, 1:ON)
                (str, None),  # rsv
                (str, None),  # rsv
            ]
        ),
        help="""Get/Set Tone-Out Settings.

        Format:
        TON,[INDEX] - Get tone-out settings for INDEX
        TON,[INDEX],[NAME],[FRQ],[MOD],[ATT],[DLY],[ALT],[ALTL],[TONE_A],...
        [TONE_B],[ALT_COLOR],[ALT_PATTERN],[AGC_ANALOG] - Set tone-out settings

        Parameters:
        INDEX : Index (1-9, 0 means 10)
        NAME : Name (max 16 chars)
        FRQ : Channel Frequency
        MOD : Modulation (AUTO, FM, NFM)
        ATT : Attenuation (0:OFF, 1:ON)
        DLY : Delay Time (0,1,2,5,10,30 seconds, INF: Infinite)
        ALT : Alert Tone (0:OFF, 1-9:Tone No.)
        ALTL : Alert Tone Level (0:AUTO, 1-15)
        TONE_A : Tone A Frequency (e.g., 10000 means 1000.0Hz)
        TONE_B : Tone B Frequency
        ALT_COLOR : Alert Light color (OFF, RED)
        ALT_PATTERN : Alert Light Pattern (0:ON, 1:Slow, 2:Fast)
        AGC_ANALOG : AGC Setting for Analog Audio (0:OFF, 1:ON)
        """,
    ),
    "DBC": ScannerCommand(
        name="DBC",
        requires_prg=True,
        set_format="DBC,{band_no},{step},{mod}",
        validator=validate_param_constraints(
            [
                (int, (1, 31)),  # band_no (1-31)
                (
                    int,
                    {
                        500,
                        625,
                        750,
                        833,
                        1000,
                        1250,
                        1500,
                        2000,
                        2500,
                        5000,
                        10000,
                    },
                ),  # step
                (str, {"AM", "FM", "NFM", "WFM", "FMB"}),  # mod
            ]
        ),
        help="""Get/Set Default Band Coverage Settings.

        Format:
        DBC,[BAND_NO] - Get settings for band number
        DBC,[BAND_NO],[STEP],[MOD] - Set band coverage settings

        Parameters:
        BAND_NO : Band number (1-31)
        STEP : Search Step (500:5kHz, 625:6.25kHz, 750:7.5kHz, 833:8.33kHz,
               1000:10kHz, etc.)
        MOD : Modulation (AM, FM, NFM, WFM, FMB)
        """,
    ),
    "BBS": ScannerCommand(
        name="BBS",
        requires_prg=True,
        set_format="BBS,{index},{limit_l},{limit_h}",
        validator=validate_param_constraints(
            [
                (int, lambda x: 1 <= x <= 10),  # index (1-9, 0 means 10)
                (str, None),  # limit_l (Lower Limit Frequency)
                (str, None),  # limit_h (Upper Limit Frequency)
            ]
        ),
        help="""Get/Set Broadcast Screen Band Settings.

        Format:
        BBS,[INDEX] - Get broadcast screen band settings
        BBS,[INDEX],[LIMIT_L],[LIMIT_H] - Set broadcast screen band settings

        Parameters:
        INDEX : Index (1-9, 0 means 10)
        LIMIT_L : Lower Limit Frequency (00000000-99999999)
        LIMIT_H : Upper Limit Frequency (00000000-99999999)
        """,
    ),
}

# Set source module for each command
for cmd in SPECIALIZED_COMMANDS.values():
    cmd.source_module = "SPECIALIZED_COMMANDS"
