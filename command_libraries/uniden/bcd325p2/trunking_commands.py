"""
Trunking System commands for the BCD325P2.

These commands allow you to configure and manage trunked radio systems and
sites.
"""

from utilities.core.shared_utils import ScannerCommand
from utilities.validators import validate_param_constraints

TRUNKING_COMMANDS = {
    "TRN": ScannerCommand(
        name="TRN",
        requires_prg=True,
        set_format=(
            "TRN,{index},{id_search},{s_bit},{end_code},{afs},{rsv1},{rsv2},"
            "{emg},{emgl},{fmap},{ctm_fmap},{rsv3},{rsv4},{rsv5},{rsv6},{rsv7},"
            "{rsv8},{rsv9},{rsv10},{rsv11},{rsv12},{mot_id},{emg_color},"
            "{emg_pattern},{p25nac},{pri_id_scan}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # index
                (int, {0, 1}),  # id_search (0:ID Scan mode, 1:Search Mode)
                (int, {0, 1}),  # s_bit (0:Ignore, 1:Yes)
                (
                    int,
                    {0, 1, 2},
                ),  # end_code (0:Ignore, 1:Analog, 2:Analog and Digital)
                (int, {0, 1}),  # afs (0:Decimal, 1:AFS)
                (str, None),  # rsv1
                (str, None),  # rsv2
                (
                    int,
                    lambda x: x == 0 or 1 <= x <= 9,
                ),  # emg (0:Ignore, 1-9:Alert)
                (int, lambda x: x == 0 or 1 <= x <= 15),  # emgl (0:OFF, 1-15)
                (int, (0, 16)),  # fmap (0-16, 0-15:Preset, 16:Custom)
                (
                    str,
                    lambda x: all(c in "0123456789ABCDEF" for c in x)
                    and len(x) == 8,
                ),  # ctm_fmap
                (str, None),  # rsv3
                (str, None),  # rsv4
                (str, None),  # rsv5
                (str, None),  # rsv6
                (str, None),  # rsv7
                (str, None),  # rsv8
                (str, None),  # rsv9
                (str, None),  # rsv10
                (str, None),  # rsv11
                (str, None),  # rsv12
                (int, {0, 1}),  # mot_id (0:Decimal, 1:HEX)
                (str, {"OFF", "RED"}),  # emg_color
                (int, {0, 1, 2}),  # emg_pattern (0:ON, 1:Slow, 2:Fast)
                (
                    str,
                    lambda x: x == "SRCH" or (x.isalnum() and len(x) <= 4),
                ),  # p25nac
                (int, {0, 1}),  # pri_id_scan (0:OFF, 1:ON)
            ]
        ),
        help="""Get/Set Trunk Info.

        Format:
        TRN,[INDEX] - Get trunk system information
        TRN,[INDEX],[ID_SEARCH],[S_BIT],[END_CODE]... - Set trunk system info

        Parameters:
        INDEX : System Index
        ID_SEARCH : ID Search/Scan (0:ID Scan mode, 1:Search Mode)
        S_BIT : Motorola Status Bit (0:Ignore, 1:Yes)
        END_CODE : Motorola End Code (0:Ignore, 1:Analog, 2:Analog and Digital)
        AFS : EDACS ID Format (0:Decimal, 1:AFS)
        EMG : Emergency Alert (0:Ignore, 1-9:Alert)
        EMGL : Emergency Alert Level (0:OFF, 1-15)
        FMAP : Fleet Map (0-16, 0-15:Preset, 16:Custom)
        CTM_FMAP : Custom Fleet Map (8 digits, each 0-E representing size codes)
        MOT_ID : Motorola/P25 ID Format (0:Decimal, 1:HEX)
        EMG_COLOR : Emergency Alert Light color (OFF, RED)
        EMG_PATTERN : Emergency Alert Light Pattern (0:ON, 1:Slow, 2:Fast)
        P25NAC : P25 NAC/Color Code (0-FFF:NAC, 1000-100F:Color Code,
        SRCH:Search)
        PRI_ID_SCAN : Priority ID Scan (0:OFF, 1:ON)
        """,
    ),
    "AST": ScannerCommand(
        name="AST",
        requires_prg=True,
        set_format="AST,{sys_index},{rsv}",
        validator=validate_param_constraints(
            [(int, None), (str, None)]  # system_index  # reserved parameter
        ),
        help="""Append Site.

        Format:
        AST,[SYS_INDEX],[RSV] - Append a site to the system

        Parameters:
        SYS_INDEX : System Index to add site to
        RSV : Reserved parameter

        Returns:
        The index of the created site, or -1 if creation failed
        """,
    ),
    "SIF": ScannerCommand(
        name="SIF",
        requires_prg=True,
        set_format=(
            "SIF,{index},{name},{quick_key},{hld},{lout},{mod},{att},{c_ch},"
            "{rsv1},{rsv2},{start_key},{latitude},{longitude},{range},"
            "{gps_enable},{rsv3},{mot_type},{edacs_type},{p25waiting},{rsv4}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # index
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (str, lambda x: x == "." or 0 <= int(x) <= 99),  # quick_key
                (int, (0, 255)),  # hold time
                (int, {0, 1}),  # lockout
                (str, {"AUTO", "FM", "NFM"}),  # modulation
                (int, {0, 1}),  # attenuation
                (int, {1}),  # c-ch (control channel only - always 1:ON)
                (str, None),  # rsv1
                (str, None),  # rsv2
                (str, lambda x: x == "." or 0 <= int(x) <= 9),  # start_key
                (str, None),  # latitude
                (str, None),  # longitude
                (int, (1, 250)),  # range
                (int, {0, 1}),  # gps_enable
                (str, None),  # rsv3
                (str, {"STD", "SPL", "CUSTOM"}),  # mot_type
                (str, {"WIDE", "NARROW"}),  # edacs_type
                (
                    int,
                    {0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000},
                ),  # p25waiting
                (str, None),  # rsv4
            ]
        ),
        help="""Get/Set Site Info.

        Format:
        SIF,[INDEX] - Get site information
        SIF,[INDEX],[NAME],[QUICK_KEY],[HLD],[LOUT],[MOD],[ATT],[C-CH],...

        Parameters:
        INDEX : Site Index
        NAME : Name (max 16 chars)
        QUICK_KEY : Quick Key (0-99, . for none)
        HLD : Site Hold Time (0-255)
        LOUT : Lockout (0:Unlocked, 1:Lockout)
        MOD : Modulation (AUTO, FM, NFM)
        ATT : Attenuation (0:OFF, 1:ON)
        C-CH : Control Channel Only (always 1:ON)
        START_KEY : Startup Configuration (0-9, . for none)
        LATITUDE : North or South Latitude
        LONGITUDE : West or East Longitude
        RANGE : Range (1-250: 1=0.5 mile or km)
        GPS_ENABLE : GPS Location detection (0:OFF, 1:ON)
        MOT_TYPE : Band type for MOT/EDACS (STD, SPL, CUSTOM)
        EDACS_TYPE : EDACS type (WIDE, NARROW)
        P25WAITING : Digital Waiting time (0,100,200,...,900,1000 ms)
        """,
    ),
    "TFQ": ScannerCommand(
        name="TFQ",
        requires_prg=True,
        set_format=(
            "TFQ,{chn_index},{frq},{lcn},{lout},{rsv},{number_tag},"
            "{vol_offset},{rsv2},{color_code}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # chn_index
                (int, None),  # frequency
                (int, lambda x: 0 <= x <= 4094),  # lcn
                (int, {0, 1}),  # lockout (0=Unlocked, 1=Lockout)
                (str, None),  # rsv
                (
                    str,
                    lambda x: x == "NONE" or 0 <= int(x) <= 999,
                ),  # number_tag
                (int, (-3, 3)),  # vol_offset (-3 to +3)
                (str, None),  # rsv2
                (str, lambda x: x == "SRCH" or 0 <= int(x) <= 15),  # color_code
            ]
        ),
        help="""Get/Set Trunk Frequency Info.

        Format:
        TFQ,[CHN_INDEX] - Get trunk frequency information
        TFQ,[CHN_INDEX],[FRQ],[LCN],[LOUT]... - Set trunk frequency

        Parameters:
        CHN_INDEX : Trunk Frequency Index
        FRQ : Trunk Frequency
        LCN : LCN
            - EDACS WIDE/NARROW system: 1-30
            - LTR system: 1-20
            - DMR/MotoTRBO system: 0-4094
        LOUT : Lockout (0:Unlocked, 1:Lockout)
        NUMBER_TAG : Number tag (0-999, NONE)
        VOL_OFFSET : Volume Offset (-3 to +3)
        COLOR_CODE : Color Code (0-15, SRCH for Search)

        Notes:
        For Motorola or EDACS SCAT systems, LCN is ignored.
        NUMBER_TAG and VOL_OFFSET are only used for SCAT systems.
        """,
    ),
    "MCP": ScannerCommand(
        name="MCP",
        requires_prg=True,
        set_format=(
            "MCP,{index},{lower1},{upper1},{step1},{offset1},{lower2},{upper2},"
            "{step2},{offset2},{lower3},{upper3},{step3},{offset3},{lower4},"
            "{upper4},{step4},{offset4},{lower5},{upper5},{step5},{offset5},"
            "{lower6},{upper6},{step6},{offset6}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # index
                (int, None),  # lower1
                (int, None),  # upper1
                (
                    str,
                    {
                        "500",
                        "625",
                        "750",
                        "833",
                        "1000",
                        "1250",
                        "1500",
                        "1875",
                        "2000",
                        "2500",
                        "3000",
                        "3125",
                        "3500",
                        "3750",
                        "4000",
                        "4375",
                        "4500",
                        "5000",
                        "5500",
                        "5625",
                        "6000",
                        "6250",
                        "6500",
                        "6875",
                        "7000",
                        "7500",
                        "8000",
                        "8125",
                        "8500",
                        "8750",
                        "9000",
                        "9375",
                        "9500",
                        "10000",
                    },
                ),  # step1
                (int, (-1023, 1023)),  # offset1
                (int, None),  # lower2
                (int, None),  # upper2
                (
                    str,
                    {
                        "500",
                        "625",
                        "750",
                        "833",
                        "1000",
                        "1250",
                        "1500",
                        "1875",
                        "2000",
                        "2500",
                        "3000",
                        "3125",
                        "3500",
                        "3750",
                        "4000",
                        "4375",
                        "4500",
                        "5000",
                        "5500",
                        "5625",
                        "6000",
                        "6250",
                        "6500",
                        "6875",
                        "7000",
                        "7500",
                        "8000",
                        "8125",
                        "8500",
                        "8750",
                        "9000",
                        "9375",
                        "9500",
                        "10000",
                    },
                ),  # step2
                (int, (-1023, 1023)),  # offset2
                (int, None),  # lower3
                (int, None),  # upper3
                (
                    str,
                    {
                        "500",
                        "625",
                        "750",
                        "833",
                        "1000",
                        "1250",
                        "1500",
                        "1875",
                        "2000",
                        "2500",
                        "3000",
                        "3125",
                        "3500",
                        "3750",
                        "4000",
                        "4375",
                        "4500",
                        "5000",
                        "5500",
                        "5625",
                        "6000",
                        "6250",
                        "6500",
                        "6875",
                        "7000",
                        "7500",
                        "8000",
                        "8125",
                        "8500",
                        "8750",
                        "9000",
                        "9375",
                        "9500",
                        "10000",
                    },
                ),  # step3
                (int, (-1023, 1023)),  # offset3
                (int, None),  # lower4
                (int, None),  # upper4
                (
                    str,
                    {
                        "500",
                        "625",
                        "750",
                        "833",
                        "1000",
                        "1250",
                        "1500",
                        "1875",
                        "2000",
                        "2500",
                        "3000",
                        "3125",
                        "3500",
                        "3750",
                        "4000",
                        "4375",
                        "4500",
                        "5000",
                        "5500",
                        "5625",
                        "6000",
                        "6250",
                        "6500",
                        "6875",
                        "7000",
                        "7500",
                        "8000",
                        "8125",
                        "8500",
                        "8750",
                        "9000",
                        "9375",
                        "9500",
                        "10000",
                    },
                ),  # step4
                (int, (-1023, 1023)),  # offset4
                (int, None),  # lower5
                (int, None),  # upper5
                (
                    str,
                    {
                        "500",
                        "625",
                        "750",
                        "833",
                        "1000",
                        "1250",
                        "1500",
                        "1875",
                        "2000",
                        "2500",
                        "3000",
                        "3125",
                        "3500",
                        "3750",
                        "4000",
                        "4375",
                        "4500",
                        "5000",
                        "5500",
                        "5625",
                        "6000",
                        "6250",
                        "6500",
                        "6875",
                        "7000",
                        "7500",
                        "8000",
                        "8125",
                        "8500",
                        "8750",
                        "9000",
                        "9375",
                        "9500",
                        "10000",
                    },
                ),  # step5
                (int, (-1023, 1023)),  # offset5
                (int, None),  # lower6
                (int, None),  # upper6
                (
                    str,
                    {
                        "500",
                        "625",
                        "750",
                        "833",
                        "1000",
                        "1250",
                        "1500",
                        "1875",
                        "2000",
                        "2500",
                        "3000",
                        "3125",
                        "3500",
                        "3750",
                        "4000",
                        "4375",
                        "4500",
                        "5000",
                        "5500",
                        "5625",
                        "6000",
                        "6250",
                        "6500",
                        "6875",
                        "7000",
                        "7500",
                        "8000",
                        "8125",
                        "8500",
                        "8750",
                        "9000",
                        "9375",
                        "9500",
                        "10000",
                    },
                ),  # step6
                (int, (-1023, 1023)),  # offset6
            ]
        ),
        help="""Get/Set Motorola Custom Band Plan.

        Format:
        MCP,[INDEX] - Get band plan settings for site INDEX
        MCP,[INDEX],[LOWER1],[UPPER1],[STEP1],[OFFSET1]... - Set band plan

        Parameters:
        INDEX : Site Index
        LOWERn : Lower Frequency n
        UPPERn : Upper Frequency n
        STEPn : Step n
            500: 5.0kHz     625: 6.25kHz     1000: 10.0kHz
            1250: 12.5kHz   1500: 15.0kHz    ...etc
        OFFSETn : Offset n (-1023 to 1023)

        Notes:
        Before using this command, set Band Plan type as "Custom"
        using the SIF command.
        """,
    ),
    "ABP": ScannerCommand(
        name="ABP",
        requires_prg=True,
        set_format=(
            "ABP,{index},{base_freq_0},{spacing_freq_0},{base_freq_1},"
            "{spacing_freq_1},{base_freq_2},{spacing_freq_2},{base_freq_3},"
            "{spacing_freq_3},{base_freq_4},{spacing_freq_4},{base_freq_5},"
            "{spacing_freq_5},{base_freq_6},{spacing_freq_6},{base_freq_7},"
            "{spacing_freq_7},{base_freq_8},{spacing_freq_8},{base_freq_9},"
            "{spacing_freq_9},{base_freq_a},{spacing_freq_a},{base_freq_b},"
            "{spacing_freq_b},{base_freq_c},{spacing_freq_c},{base_freq_d},"
            "{spacing_freq_d},{base_freq_e},{spacing_freq_e},{base_freq_f},"
            "{spacing_freq_f}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # index
                # Hexadecimal validators for base frequencies (25-960MHz)
                # Min value: (25 * 10^6) / 5 = 5,000,000 (hex: 4C4B40)
                # Max value: (960 * 10^6) / 5 = 192,000,000 (hex: B71B000)
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_0
                # Hexadecimal validators for spacing frequencies (0.125-128kHz)
                # Min value: (0.125 * 10^3) / 125 = 1 (hex: 1)
                # Max value: (128 * 10^3) / 125 = 1024 (hex: 400)
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_0
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_1
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_1
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_2
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_2
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_3
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_3
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_4
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_4
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_5
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_5
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_6
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_6
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_7
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_7
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_8
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_8
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_9
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_9
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_a
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_a
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_b
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_b
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_c
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_c
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_d
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_d
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_e
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_e
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= int("4C4B40", 16)
                        and int(x, 16) <= int("B71B000", 16)
                    ),
                ),  # base_freq_f
                (
                    str,
                    lambda x: x == "0"
                    or (
                        x.isalnum()
                        and all(c in "0123456789ABCDEF" for c in x)
                        and int(x, 16) >= 1
                        and int(x, 16) <= int("400", 16)
                    ),
                ),  # spacing_freq_f
            ]
        ),
        help="""Get/Set APCO-P25 Band Plan.

        Format:
        ABP,[INDEX] - Get band plan for site INDEX
        ABP,[INDEX],[BASE_FREQ_0],[SPACING_FREQ_0]... - Set band plan

        Parameters:
        INDEX : Site Index
        BASE_FREQ_n : Base frequency (25.0000MHz to 960.0000MHz, 5.0Hz step)
                      Hexadecimal representation: (base frequency * 10^6) / 5
        SPACING_FREQ_n : Spacing frequency (0.125kHz to 128.0kHz, 0.125kHz step)
                         Hexadecimal representation:
                         (spacing frequency * 10^3) / 125

        Example:
        Base freq = 851.00625MHz, Spacing = 6.25kHz
        BASE_FREQ_n = A2510A2 (hex)
        SPACING_FREQ_n = 32 (hex)

        Notes:
        Band plans with no data return "0".
        """,
    ),
}

# Set source module for each command
for cmd in TRUNKING_COMMANDS.values():
    cmd.source_module = "TRUNKING_COMMANDS"
