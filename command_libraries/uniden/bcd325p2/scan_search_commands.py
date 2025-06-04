"""
Scan and Search commands for the BCD325P2.

These commands control search operations, custom search settings, and related
functionality.
"""

from utilities.core.shared_utils import ScannerCommand
from utilities.validators import (
    validate_binary_options,
    validate_param_constraints,
)

SCAN_SEARCH_COMMANDS = {
    "QSH": ScannerCommand(
        name="QSH",
        requires_prg=False,
        set_format=(
            "QSH,{frq},{rsv},{mod},{att},{dly},{rsv},{code_srch},{bsc},"
            "{rep},{rsv},{agc_analog},{agc_digital},{p25waiting}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # frequency
                (str, None),  # rsv (reserved)
                (str, {"AUTO", "AM", "FM", "NFM", "WFM", "FMB"}),  # modulation
                (int, {0, 1}),  # attenuation (0=OFF, 1=ON)
                (int, {-10, -5, -2, 0, 1, 2, 5, 10, 30}),  # delay time
                (str, None),  # rsv (reserved)
                # code_srch (0=OFF, 1=CTCSS/DCS, 2=P25 NAC/Color Code)
                (int, {0, 1, 2}),
                # bsc - broadcast screen (16 digits)
                (str, validate_binary_options(16)),
                (int, {0, 1}),  # rep - repeater find (0=OFF, 1=ON)
                (str, None),  # rsv (reserved)
                (int, {0, 1}),  # agc_analog (0=OFF, 1=ON)
                (int, {0, 1}),  # agc_digital (0=OFF, 1=ON)
                # p25waiting
                (int, {0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000}),
            ]
        ),
        help="""Go to quick search hold mode.

        Format:
        QSH - Get current quick search
        QSH,[FRQ],[RSV],[MOD],[ATT],[DLY],[RSV],[CODE_SRCH],[BSC],[REP],[RSV],
        [AGC_ANALOG],[AGC_DIGITAL],[P25WAITING] - Switch to quick search

        Parameters:
        FRQ : Frequency (The right frequency)
        MOD : Modulation (AUTO/AM/FM/NFM/WFM/FMB)
        ATT : Attenuation (0:OFF, 1:ON)
        DLY : Delay Time (-10,-5,-2,0,1,2,5,10,30)
        CODE_SRCH : CTCSS/DCS/P25 NAC Search
                    (0:OFF, 1:CTCSS/DCS, 2:P25 NAC/Color Code)
        BSC : Broadcast Screen (16digit binary, each position represents a band)
        REP : Repeater Find (0:OFF, 1:ON)
        AGC_ANALOG : AGC Setting for Analog Audio (0:OFF, 1:ON)
        AGC_DIGITAL : AGC Setting for Digital Audio (0:OFF, 1:ON)
        P25WAITING : Digital Waiting time (0,100,...,900,1000 ms)

        This command is invalid when the scanner is in Menu Mode,
        during Direct Entry operation, or during Quick Save operation.
        """,
    ),
    "QSC": ScannerCommand(
        name="QSC",
        requires_prg=False,
        set_format=(
            "QSC,{frq},{rsv},{mod},{att},{dly},{rsv},{code_srch},{bsc},"
            "{rep},{rsv},{agc_analog},{agc_digital},{p25waiting}"
        ),
        validator=validate_param_constraints(
            [
                (int, None),  # frequency
                (str, None),  # rsv (reserved)
                (str, {"AUTO", "AM", "FM", "NFM", "WFM", "FMB"}),  # modulation
                (int, {0, 1}),  # attenuation (0=OFF, 1=ON)
                (int, {-10, -5, -2, 0, 1, 2, 5, 10, 30}),  # delay time
                (str, None),  # rsv (reserved)
                # code_srch (0=OFF, 1=CTCSS/DCS, 2=P25 NAC/Color Code)
                (int, {0, 1, 2}),
                # bsc - broadcast screen (16 digits)
                (str, validate_binary_options(16)),
                (int, {0, 1}),  # rep - repeater find (0=OFF, 1=ON)
                (str, None),  # rsv (reserved)
                (int, {0, 1}),  # agc_analog (0=OFF, 1=ON)
                (int, {0, 1}),  # agc_digital (0=OFF, 1=ON)
                # p25waiting
                (int, {0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000}),
            ]
        ),
        help="""Set current frequency and get reception status.

        Format:
        QSC,[FRQ],[RSV],[MOD],[ATT],[DLY],[RSV],[CODE_SRCH],[BSC],[REP],[RSV],
        [AGC_ANALOG],[AGC_DIGITAL],[P25WAITING] - Set frequency and get status

        Parameters:
        FRQ : Frequency (The right frequency)
        MOD : Modulation (AUTO/AM/FM/NFM/WFM/FMB)
        ATT : Attenuation (0:OFF, 1:ON)
        DLY : Delay Time (-10,-5,-2,0,1,2,5,10,30)
        CODE_SRCH : CTCSS/DCS/P25 NAC Search
                    (0:OFF, 1:CTCSS/DCS, 2:P25 NAC/Color Code)
        BSC : Broadcast Screen (16digit binary, each position represents a band)
        REP : Repeater Find (0:OFF, 1:ON)
        AGC_ANALOG : AGC Setting for Analog Audio (0:OFF, 1:ON)
        AGC_DIGITAL : AGC Setting for Digital Audio (0:OFF, 1:ON)
        P25WAITING : Digital Waiting time (0,100,200,...,900,1000 ms)

        Returns:
        [RSSI],[FRQ],[SQL] - RSSI level, frequency, and squelch status

        This command is invalid when the scanner is in Menu Mode, during Direct
        Entry operation, or during Quick Save operation.
        """,
    ),
    "CSC": ScannerCommand(
        name="CSC",
        requires_prg=False,
        set_format="CSC,{mode}",
        validator=validate_param_constraints(
            [(str, {"ON", "OFF"})]  # mode (ON/OFF)
        ),
        help="""Go to Custom search and get reception status.

        Format:
        CSC,ON - Start custom search and output status
        CSC,OFF - Stop custom search output

        Returns:
        [RSSI],[FRQ],[SQL] - Series of status messages with RSSI level,
        frequency, and squelch status (0:CLOSE, 1:OPEN)

        This command is invalid when the scanner is in Menu Mode, during Direct
        Entry operation, or during Quick Save operation.
        """,
    ),
    "SCO": ScannerCommand(
        name="SCO",
        requires_prg=True,
        set_format=(
            "SCO,{rsv},{mod},{att},{dly},{rsv},{code_srch},{bsc},{rep},{rsv},"
            "{rsv},{max_store},{rsv},{agc_analog},{agc_digital},{p25waiting}"
        ),
        validator=validate_param_constraints(
            [
                (str, None),  # rsv (reserved)
                (str, {"AUTO", "AM", "FM", "NFM", "WFM", "FMB"}),  # modulation
                (int, {0, 1}),  # attenuation (0=OFF, 1=ON)
                (int, {-10, -5, -2, 0, 1, 2, 5, 10, 30}),  # delay time
                (str, None),  # rsv (reserved)
                # code_srch (0=OFF, 1=CTCSS/DCS, 2=P25 NAC/Color Code)
                (int, {0, 1, 2}),
                # bsc - broadcast screen (16 digits)
                (str, validate_binary_options(16)),
                (int, {0, 1}),  # rep - repeater find (0=OFF, 1=ON)
                (str, None),  # rsv (reserved)
                (str, None),  # rsv (reserved)
                (int, (1, 256)),  # max_store (1-256)
                (str, None),  # rsv (reserved)
                (int, {0, 1}),  # agc_analog (0=OFF, 1=ON)
                (int, {0, 1}),  # agc_digital (0=OFF, 1=ON)
                # p25waiting
                (int, {0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000}),
            ]
        ),
        help="""Get/Set Search/Close Call Settings.

        Format:
        SCO - Get current search settings
        SCO,[RSV],[MOD],[ATT],[DLY],[RSV],[CODE_SRCH],[BSC],[REP],[RSV],[RSV],
        [MAX_STORE],[RSV],[AGC_ANALOG],[AGC_DIGITAL],[P25WAITING] -
        Set search settings

        Parameters:
        MOD : Modulation (AUTO/AM/FM/NFM/WFM/FMB)
        ATT : Attenuation (0:OFF, 1:ON)
        DLY : Delay Time (-10,-5,-2,0,1,2,5,10,30)
        CODE_SRCH : CTCSS/DCS/P25 NAC Search
                    (0:OFF, 1:CTCSS/DCS, 2:P25 NAC/Color Code)
        BSC : Broadcast Screen - 16 digits where each bit represents a band
              From left to right: Pager, FM, UHF TV, VHF TV, NOAA WX, Reserve,
              Band 1, Band 2, etc.
        REP : Repeater Find (0:OFF, 1:ON)
        MAX_STORE : Max Auto Store (1-256)
        AGC_ANALOG : AGC Setting for Analog Audio (0:OFF, 1:ON)
        AGC_DIGITAL : AGC Setting for Digital Audio (0:OFF, 1:ON)
        P25WAITING : Digital Waiting time (0,100,200,...,900,1000 ms)
        """,
    ),
    "SHK": ScannerCommand(
        name="SHK",
        requires_prg=True,
        set_format=(
            "SHK,{srch_key_1},{srch_key_2},{srch_key_3},{rsv},{rsv},{rsv}"
        ),
        validator=validate_param_constraints(
            [
                (str, None),  # srch_key_1 - many possible values
                (str, None),  # srch_key_2 - many possible values
                (str, None),  # srch_key_3 - many possible values
                (str, None),  # rsv (reserved)
                (str, None),  # rsv (reserved)
                (str, None),  # rsv (reserved)
            ]
        ),
        help="""Get/Set Search Key Settings.

        Format:
        SHK - Get current search key settings
        SHK,[SRCH_KEY_1],[SRCH_KEY_2],[SRCH_KEY_3],[RSV],[RSV],[RSV] -
        Set search keys

        Parameters:
        SRCH_KEY_1 to SRCH_KEY_3 : Search Range
        Possible values:
        .(dot) : Not assigned
        PublicSafety : Public Safety range     CUSTOM_1 : Custom 1 range
        News : News range                      CUSTOM_2 : Custom 2 range
        HAM : HAM Radio range                  CUSTOM_3 : Custom 3 range
        Marine : Marine range                  CUSTOM_4 : Custom 4 range
        Railroad : Railroad range              CUSTOM_5 : Custom 5 range
        Air : Air range                        CUSTOM_6 : Custom 6 range
        CB : CB Radio range                    CUSTOM_7 : Custom 7 range
        FRS/GMRS/MURS : FRS/GMRS/MURS range    CUSTOM_8 : Custom 8 range
        Racing : Racing range                  CUSTOM_9 : Custom 9 range
        FM : FM Broadcast range                CUSTOM_10 : Custom 10 range
        Special : Special range                TONE_OUT : Tone Out mode
        Military : Military Air range          B_SCOPE : Band Scope
        """,
    ),
    "SSP": ScannerCommand(
        name="SSP",
        requires_prg=True,
        set_format=(
            "SSP,{srch_index},{dly},{att},{hld},{lout},{quick_key},{start_key},"
            "{rsv},{number_tag},{agc_analog},{agc_digital},{p25waiting}"
        ),
        validator=validate_param_constraints(
            [
                (int, {1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 15}),  # srch_index
                (int, {-10, -5, -2, 0, 1, 2, 5, 10, 30}),  # delay time
                (int, {0, 1}),  # attenuation (0=OFF, 1=ON)
                (int, (0, 255)),  # hold time (0-255)
                (int, {0, 1}),  # lockout (0=Unlocked, 1=Lockout)
                (str, lambda x: x == "." or 0 <= int(x) <= 99),  # quick_key
                (str, lambda x: x == "." or 0 <= int(x) <= 9),  # start_key
                (str, None),  # rsv (reserved)
                (
                    str,
                    lambda x: x == "NONE" or 0 <= int(x) <= 999,
                ),  # number_tag
                (int, {0, 1}),  # agc_analog (0=OFF, 1=ON)
                (int, {0, 1}),  # agc_digital (0=OFF, 1=ON)
                # p25waiting
                (int, {0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000}),
            ]
        ),
        help="""Get/Set Service Search Settings.

        Format:
        SSP,[SRCH_INDEX] - Get service search settings
        SSP,[SRCH_INDEX],[DLY],[ATT],[HLD],[LOUT],[QUICK_KEY],[START_KEY],[RSV],
        [NUMBER_TAG],[AGC_ANALOG],[AGC_DIGITAL],[P25WAITING]
        - Set search settings

        Parameters:
        SRCH_INDEX : Service Search Range
          1: Public Safety  6: Air        12: Special
          2: News          7: CB Radio   15: Military Air
          3: HAM Radio     8: FRS/GMRS/MURS
          4: Marine        9: Racing
          5: Railroad     11: FM Broadcast
        DLY : Delay Time (-10,-5,-2,0,1,2,5,10,30)
        ATT : Attenuation (0:OFF, 1:ON)
        HLD : System Hold Time for Search with Scan (0-255)
        LOUT : Lockout for Search with Scan (0:Unlocked, 1:Lockout)
        QUICK_KEY : Quick Key (0-99/.(dot) means none)
        START_KEY : Startup Configuration Key (0-9/.(dot) means none)
        NUMBER_TAG : Number tag (0-999/NONE)
        AGC_ANALOG : AGC Setting for Analog Audio (0:OFF, 1:ON)
        AGC_DIGITAL : AGC Setting for Digital Audio (0:OFF, 1:ON)
        P25WAITING : Digital Waiting time (0,100,200,...,900,1000 ms)
        """,
    ),
    "CSP": ScannerCommand(
        name="CSP",
        requires_prg=True,
        set_format=(
            "CSP,{srch_index},{name},{limit_l},{limit_h},{stp},{mod},{att},"
            "{dly},{rsv},{hld},{lout},{c_ch},{rsv},{rsv},{quick_key},"
            "{start_key},{rsv},{number_tag},{agc_analog},{agc_digital},"
            "{p25waiting}"
        ),
        validator=validate_param_constraints(
            [
                # srch_index (1-9, 0 means 10)
                (int, lambda x: 1 <= x <= 10 or x == 0),
                (str, lambda x: len(x) <= 16),  # name (max 16 chars)
                (int, (250000, 9600000)),  # limit_l (lower limit)
                (int, (250000, 9600000)),  # limit_h (upper limit)
                (
                    str,
                    {
                        "AUTO",
                        "500",
                        "625",
                        "750",
                        "833",
                        "1000",
                        "1250",
                        "1500",
                        "2000",
                        "2500",
                        "5000",
                        "10000",
                    },
                ),  # step
                (str, {"AUTO", "AM", "FM", "NFM", "WFM", "FMB"}),  # modulation
                (int, {0, 1}),  # attenuation (0=OFF, 1=ON)
                (int, {-10, -5, -2, 0, 1, 2, 5, 10, 30}),  # delay time
                (str, None),  # rsv (reserved)
                (int, (0, 255)),  # hold time (0-255)
                (int, {0, 1}),  # lockout (0=Unlocked, 1=Lockout)
                (int, {0, 1}),  # c-ch (0=OFF, 1=ON)
                (str, None),  # rsv (reserved)
                (str, None),  # rsv (reserved)
                (str, lambda x: x == "." or 0 <= int(x) <= 99),  # quick_key
                (str, lambda x: x == "." or 0 <= int(x) <= 9),  # start_key
                (str, None),  # rsv (reserved)
                # number_tag
                (str, lambda x: x == "NONE" or 0 <= int(x) <= 999),
                (int, {0, 1}),  # agc_analog (0=OFF, 1=ON)
                (int, {0, 1}),  # agc_digital (0=OFF, 1=ON)
                # p25waiting
                (int, {0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000}),
            ]
        ),
        help="""Get/Set Custom Search Settings.

        Format:
        CSP,[SRCH_INDEX] - Get custom search settings
        CSP,[SRCH_INDEX],[NAME],[LIMIT_L],[LIMIT_H],[STP],[MOD],[ATT],[DLY]...
        - Set custom search

        Parameters:
        SRCH_INDEX : Index (1-9, 0 means 10)
        NAME : Name (max 16 chars)
        LIMIT_L : Lower Limit Frequency (250000-9600000)
        LIMIT_H : Upper Limit Frequency (250000-9600000)
        STP : Search Step (AUTO, 500:5kHz, 1000:10kHz, etc.)
        MOD : Modulation (AUTO/AM/FM/NFM/WFM/FMB)
        ATT : Attenuation (0:OFF, 1:ON)
        DLY : Delay Time (-10,-5,-2,0,1,2,5,10,30)
        HLD : System Hold Time (0-255)
        LOUT : Lockout (0:Unlocked, 1:Lockout)
        C-CH : Control Channel Only (0:OFF, 1:ON)
        QUICK_KEY : Quick Key (0-99/.(dot) means none)
        START_KEY : Startup Configuration Key (0-9/.(dot) means none)
        NUMBER_TAG : Number tag (0-999/NONE)
        AGC_ANALOG : AGC Setting for Analog Audio (0:OFF, 1:ON)
        AGC_DIGITAL : AGC Setting for Digital Audio (0:OFF, 1:ON)
        P25WAITING : Digital Waiting time (0,100,200,...,900,1000 ms)
        """,
    ),
    "CSG": ScannerCommand(
        name="CSG",
        requires_prg=True,
        set_format="CSG,{status}",
        validator=validate_param_constraints(
            [
                # status (10-digit string where each digit is 0 or 1)
                (str, lambda x: all(c in "01" for c in x) and len(x) == 10)
            ]
        ),
        help="""Get/Set Custom Search Group.

        Format:
        CSG - Get current custom search range status
        CSG,[STATUS] - Set custom search range status

        Parameters:
        STATUS : 10-digit string where each digit is 0 or 1 (0:valid, 1:invalid)
                The order matches the custom search ranges 1-10

        Notes:
        - It's not possible to set all Custom Search Ranges to "0"
        """,
    ),
    "CBP": ScannerCommand(
        name="CBP",
        requires_prg=True,
        set_format=(
            "CBP,{srch_index},{mot_type},{lower1},{upper1},{step1},{offset1},"
            "{lower2},{upper2},{step2},{offset2},{lower3},{upper3},{step3},"
            "{offset3},{lower4},{upper4},{step4},{offset4},{lower5},{upper5},"
            "{step5},{offset5},{lower6},{upper6},{step6},{offset6}"
        ),
        validator=validate_param_constraints(
            [
                # srch_index (1-9, 0 means 10)
                (int, lambda x: 1 <= x <= 10 or x == 0),
                (str, {"STD", "SPL", "CUSTOM"}),  # mot_type
                (int, None),  # lower1
                (int, None),  # upper1
                # step1 (500-10000)
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
                ),
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
                ),
                # step2
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
                ),
                # step3
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
                ),
                # step4
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
                ),
                # step5
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
                ),
                # step6
                (int, (-1023, 1023)),  # offset6
            ]
        ),
        help="""Get/Set C-Ch Only Custom search MOT Band Plan Settings.

        Format:
        CBP,[SRCH_INDEX] - Get band plan settings for search index
        CBP,[SRCH_INDEX],[MOT_TYPE],[LOWER1],[UPPER1],[STEP1],[OFFSET1]... -
        Set band plan

        Parameters:
        SRCH_INDEX : Index (1-9, 0 means 10)
        MOT_TYPE : Band type for MOT (STD/SPL/CUSTOM)
        LOWERn : Lower Frequency n
        UPPERn : Upper Frequency n
        STEPn : Step n (examples: 500:5kHz, 1000:10kHz, etc.)
        OFFSETn : Offset n (-1023 to 1023)

        Notes:
        - If MOT_TYPE is not CUSTOM, other settings will be ignored
        - In set command, if only "," parameters are sent, the Band Plan
          settings will not change
        """,
    ),
}

# Set source module for each command
for cmd in SCAN_SEARCH_COMMANDS.values():
    cmd.source_module = "SCAN_SEARCH_COMMANDS"
