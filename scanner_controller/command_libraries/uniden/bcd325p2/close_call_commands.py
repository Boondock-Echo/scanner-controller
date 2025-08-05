"""
Close Call related scanner commands for the BCD325P2.

Close Call is a feature that allows the scanner to detect and tune to nearby
signals, even if they are not programmed into the scanner. The commands in this
section are related to the Close Call feature.
"""

from scanner_controller.utilities.core.command_library import ScannerCommand
from scanner_controller.utilities.validators import (
    validate_binary_options,
    validate_param_constraints,
)

CLOSE_CALL_COMMANDS = {
    "CLC": ScannerCommand(
        name="CLC",
        requires_prg=True,
        set_format="CLC,{cc_mode},{cc_override},{rsv},{altb},{altl},{altp},"
        "{cc_band},{lout},{hld},{quick_key},{number_tag},{alt_color},"
        "{alt_pattern}",
        validator=validate_param_constraints(
            [
                (int, {0, 1, 2}),  # cc_mode (0:OFF, 1:CC PRI, 2:CC DND)
                (int, {0, 1}),  # cc_override (0:OFF, 1:ON)
                (str, None),  # rsv (reserve parameter)
                (
                    int,
                    lambda x: x == 0 or 1 <= x <= 9,
                ),  # altb (0:OFF, 1-9:Tone No)
                (int, lambda x: x == 0 or 1 <= x <= 15),  # altl (0:AUTO, 1-15)
                (
                    str,
                    {"3", "5", "10", "15", "30", "45", "60", "INF"},
                ),  # altp (Close Call Pause)
                (str, validate_binary_options(7)),  # cc_band (7-digit binary)
                (int, {0, 1}),  # lout (0:Unlocked, 1:Lockout)
                (int, (0, 255)),  # hld (0-255)
                (
                    str,
                    lambda x: x == "." or 0 <= int(x) <= 99,
                ),  # quick_key (0-99, .)
                (
                    str,
                    lambda x: x == "NONE" or 0 <= int(x) <= 999,
                ),  # number_tag (0-999, NONE)
                (str, {"OFF", "RED"}),  # alt_color
                (int, {0, 1, 2}),  # alt_pattern (0:ON, 1:Slow, 2:Fast)
            ]
        ),
        help="""Get/Set Close Call Settings.

        Format:
        CLC - Get current Close Call settings
        CLC,[CC_MODE],[CC_OVERRIDE],[RSV],[ALTB],[ALTL],[ALTP],[CC_BAND],[LOUT],
        [HLD],[QUICK_KEY],[NUMBER_TAG],[ALT_COLOR],[ALT_PATTERN] -
        Set Close Call

        Parameters:
        CC_MODE : Mode (0:OFF, 1:CC PRI, 2:CC DND)
        CC_OVERRIDE : Override (0:OFF, 1:ON)
        RSV : Reserve Parameter
        ALTB : Alert Beep (0:OFF, 1-9:Tone No)
        ALTL : Alert Tone Level (0:AUTO, 1-15)
        ALTP : Close Call Pause (3, 5, 10, 15, 30, 45, 60, INF seconds)
        CC_BAND : Close Call Band (7-digit binary, each bit represents a band)
                 Format: #######
                 From left to right: VHF LOW1, VHF LOW2, AIR BAND, VHF HIGH1,
                 VHF HIGH2, UHF, 800MHz+
        LOUT : Lockout for CC Hits with Scan (0:Unlocked, 1:Lockout)
        HLD : System Hold Time for CC Hits with Scan (0-255)
        QUICK_KEY : Quick Key for CC Hits with Scan (0-99, . means none)
        NUMBER_TAG : Number tag (0-999, NONE)
        ALT_COLOR : Alert Light color (OFF, RED)
        ALT_PATTERN : Alert Light Pattern (0:ON, 1:Slow, 2:Fast)
        """,
    ),
    "JPM": ScannerCommand(
        name="JPM",
        requires_prg=False,  # JPM doesn't require program mode
        set_format="JPM,{jump_mode},{index}",
        validator=validate_param_constraints(
            [
                (
                    str,
                    {
                        "SCN_MODE",
                        "SVC_MODE",
                        "CTM_MODE",
                        "CC_MODE",
                        "WX_MODE",
                        "FTO_MODE",
                    },
                ),  # jump_mode
                (
                    str,
                    None,
                ),  # index - many possible values depending on jump_mode
            ]
        ),
        help="""Jump Mode.

        Format:
        JPM,[JUMP_MODE],[INDEX] - Jump to specified mode and index

        Parameters:
        JUMP_MODE : Mode to jump to
                   SCN_MODE - Scan mode
                   SVC_MODE - Service Search mode
                   CTM_MODE - Custom Search mode
                   CC_MODE - Close Call Only mode
                   WX_MODE - WX SCAN mode
                   FTO_MODE - Tone-Out mode

        INDEX : Depends on JUMP_MODE
                SCN_MODE - Channel Index
                SVC_MODE - PublicSafety, News, HAM, Marine, Railroad, Air, CB,
                           FRS/GMRS/MURS, Racing, FM, Special, Military
                CTM_MODE - RESERVE
                CC_MODE - RESERVE
                WX_MODE - NORMAL, A_ONLY, SAME_1, SAME_2, SAME_3, SAME_4,
                          SAME_5, ALL_FIPS
                FTO_MODE - RESERVE

        Note: Scanner returns NG if the mode switch cannot be done.
        """,
    ),
    "JNT": ScannerCommand(
        name="JNT",
        requires_prg=False,  # JNT doesn't require program mode
        set_format="JNT,{sys_tag},{chan_tag}",
        validator=validate_param_constraints(
            [
                (
                    str,
                    lambda x: x == "" or x == "NONE" or 0 <= int(x) <= 999,
                ),  # sys_tag
                (
                    str,
                    lambda x: x == "" or x == "NONE" or 0 <= int(x) <= 999,
                ),  # chan_tag
            ]
        ),
        help="""Jump to Number Tag.

        Format:
        JNT,[SYS_TAG],[CHAN_TAG] - Jump to specified number tag

        Parameters:
        SYS_TAG : System Number Tag (0-999, NONE, or blank)
        CHAN_TAG : Channel Number Tag (0-999, NONE, or blank)

        Notes:
        - When both parameters are blank, scanner returns error
        - When SYS_TAG is blank and CHAN_TAG has a number tag, scanner jumps to
          the channel number tag in current system
        - When SYS_TAG has a number tag and CHAN_TAG is blank, scanner jumps to
          the first channel of the system number tag
        """,
    ),
}

# Set source module for each command
for cmd in CLOSE_CALL_COMMANDS.values():
    cmd.source_module = "CLOSE_CALL_COMMANDS"
