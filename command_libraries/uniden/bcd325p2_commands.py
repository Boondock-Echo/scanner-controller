"""
Bcd325P2 Commands module.

This module provides functionality related to bcd325p2 commands.
It includes command definitions, help text, and utility functions for
interacting with the BCD325P2 scanner.
"""

# Application imports
from utilities.core.shared_utils import scanner_command
from utilities.validators import (
    validate_binary_options,
    validate_param_constraints,
)

# Define all commands for the BCD325P2 scanner
commands = {
    "ABP": scanner_command(
        name="ABP",
        requires_prg=True,
        help="""Get/Set APCO-P25 Band Plan.

        Format:
        ABP,[INDEX] - Get Band Plan for site INDEX
        ABP,[INDEX],[BASE_FREQ_0],[SPACING_FREQ_0]... - Set Band Plan

        Parameters:
        INDEX : Site Index
        BASE_FREQ_n : Base frequency (25.0000MHz to 960.0000MHz, 5.0Hz step)
        SPACING_FREQ_n : Spacing frequency (0.125kHz to 128.0kHz, 0.125kHz step)
        """,
    ),
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
    "BSP": scanner_command(
        name="BSP",
        requires_prg=True,
        set_format="BSP,{freq},{step},{span},{max_hold}",
        validator=validate_param_constraints(
            [
                (int, None),  # frequency
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
        STP : Step (500:5kHz, 1000:10kHz, etc.)
        SPN : Sweep Span (0.2M to 500M)
        MAX_HOLD : Max hold display (0:OFF, 1:ON)
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
    "CLC": scanner_command(
        name="CLC",
        set_format=(
            "CLC,{cc_mode},{cc_override},{cc_band},"
            "{alert_beep},{alert_light},{cc_pause}"
        ),
        validator=validate_param_constraints(
            [
                (int, {0, 1, 2}),  # cc_mode (0=Off, 1=CC Priority, 2=CC DND)
                (int, {0, 1}),  # cc_override (0=Off, 1=On)
                (str, validate_binary_options(5)),  # cc_band (00000-11111)
                (int, {0, 1}),  # alert_beep (0=Off, 1=On)
                (int, {0, 1}),  # alert_light (0=Off, 1=On)
                (int, (1, 10)),  # cc_pause (1-10 seconds)
            ]
        ),
        requires_prg=True,
        help="""Configure Close Call mode settings.

        Parameters:
        cc_mode      : Close Call mode (0=Off, 1=CC Priority, 2=CC DND)
        cc_override  : Override (0=Off, 1=On)
        cc_band      : Band filter bitmap (VHF Low,Air,VHF High,UHF,800MHz+)
                       00000 to 11111 (1=enabled, 0=disabled)
        alert_beep   : Alert beep (0=Off, 1=On)
        alert_light  : Alert light (0=Off, 1=On)
        cc_pause     : Close Call pause time (1-10 seconds)

        Example: CLC,1,0,11111,1,1,3
        Sets CC Priority mode, override off, all bands, beep on, light on, 3sec
        pause
        """,
    ),
    "GDO": scanner_command(
        name="GDO",
        requires_prg=True,
        set_format=(
            "GDO,{disp_mode},{unit},{time_format},{time_zone},{pos_format}"
        ),
        validator=validate_param_constraints(
            [
                (int, {0, 1, 2, 3, 4}),  # display mode (0-4)
                (int, {0, 1}),  # unit (0=mile, 1=km)
                (int, {0, 1}),  # time format (0=12h, 1=24h)
                (float, (-14.0, 14.0)),  # time zone (-14.0 to 14.0)
                (str, {"DMS", "DEG"}),  # position format
            ]
        ),
        help="""Get/Set GPS Display Options.

        Format:
        GDO - Get current GPS display settings
        GDO,[DISP_MODE],[UNIT],[TIME_FORMAT],[TIME_ZONE],[POS_FORMAT] -
        Set GPS settings

        Parameters:
        DISP_MODE : Display GPS mode (0:ETA, 1:Clock, 2:Elevation, 3:Speed,
            4:Location)
        UNIT : Distance unit (0:mile, 1:km)
        TIME_FORMAT : Time format (0:12H, 1:24H)
        TIME_ZONE : Time zone (-14.0 to 14.0)
        POS_FORMAT : Position format (DMS/DEG)
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
    "SCN": scanner_command(
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
        SCN,[DISP_MODE],[RSV],[CH_LOG]... - Set scanner options

        Parameters:
        DISP_MODE : Display mode (1:MODE1, 2:MODE2, 3:MODE3)
        CH_LOG : Control Channel Logging (0:OFF, 1:ON, 2:Extend)
        G_ATT : Global attenuator (0:OFF, 1:ON)
        P25_LPF : P25 Low Pass Filter (0:OFF, 1:ON)
        DISP_UID : Display Unit ID (0:OFF, 1:ON)
        """,
    ),
    "SCO": scanner_command(
        name="SCO",
        set_format="SCO,{delay},{code_search},{attstep},{deskip},{audiotype}",
        validator=validate_param_constraints(
            [
                (int, {-10, -5, -2, 0, 1, 2, 5, 10, 30}),  # delay
                (int, {0, 1, 2}),  # code_search
                (int, {0, 1}),  # attstep
                (int, {0, 1}),  # deskip
                (int, {0, 1, 2}),  # audiotype
            ]
        ),
        requires_prg=True,
        help="""Configure Search and Close Call options.

        Parameters:
        delay       : Search delay setting (-10, -5, 0, 1, 2, 5, 10, 30)
                      Negative values for no delay
        code_search : Code search during search mode (0=Off, 1=On)
        attstep     : Auto step (0=Off, 1=On)
        deskip      : Data skip (0=Off, 1=On)
        audiotype   : Audio AGC type (0=Auto, 1=Conventional, 2=Digital)

        Example: SCO,2,1,1,1,0
        2 second delay, code search on, auto step on, data skip on, auto audio
        AGC
        """,
    ),
    "WXS": scanner_command(
        name="WXS",
        set_format=(
            "WXS,{delay},{attenuation},{alert_priority},"
            "{rsv},{agc_analog},{rsv}"
        ),
        validator=validate_param_constraints(
            [
                (int, {-10, -5, -2, 0, 1, 2, 5, 10, 30}),  # delay
                (int, {0, 1}),  # attenuation
                (int, {0, 1}),  # alert_priority
                (str, None),  # rsv
                (int, {0, 1}),  # agc_analog
                (str, None),  # rsv
            ]
        ),
        help="""NOAA weather settings.

        Parameters:
        delay          : Delay (-10, -5, -2, 0, 1, 2, 5, 10, 30)
        attenuation    : Attenuation (0=OFF, 1=ON)
        alert_priority : Weather alert priority (0=OFF, 1=ON)
        agc_analog     : Analog AGC (0=OFF, 1=ON)
        """,
        requires_prg=True,
    ),
}


def getHelp(command):
    """
    Return the help string for the specified command (case-insensitive).

    Returns None if command is not defined.
    """
    cmd = commands.get(command.upper())
    return cmd.help if cmd else None


def listCommands():
    """Return a sorted list of all available command names."""
    return sorted(commands.keys())
