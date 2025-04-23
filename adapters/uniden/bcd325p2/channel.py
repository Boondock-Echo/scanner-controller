"""
Channel-related functions for the BCD325P2 scanner.

Contains functions for reading and writing channel information.
"""

from adapters.uniden.common.core import ensure_str


def read_channel_info(self, ser, index):
    """Read channel information.

    Args:
        ser: Serial connection to the scanner.
        index: Channel index.

    Returns:
        str: Channel information or error message.
    """
    try:
        self.enter_programming_mode(ser)
        response = self.send_command(ser, f"CIN,{index}")
        response_str = ensure_str(response)
        self.exit_programming_mode(ser)
        return response_str
    except Exception as e:
        return self.feedback(False, f"Error reading channel info: {e}")


def write_channel_info(
    self, ser, index, name, freq_khz, mod, ctcss, delay, lockout, priority
):
    """Write channel information.

    Args:
        ser: Serial connection to the scanner.
        index: Channel index.
        name: Channel name.
        freq_khz: Frequency in kHz.
        mod: Modulation type.
        ctcss: CTCSS tone.
        delay: Delay setting.
        lockout: Lockout status.
        priority: Priority status.

    Returns:
        str: Status message after write attempt.
    """
    try:
        self.enter_programming_mode(ser)
        parts = [
            str(index),
            name[:16],
            str(freq_khz),
            mod.upper(),
            str(ctcss),
            str(delay),
            str(lockout),
            str(priority),
            "0",  # ATT
            "0",  # ALT
            "0",  # ALTL
            "",  # Reserved
            "",  # Reserved
            "",  # Reserved
            "",  # Reserved
            "0",  # AUDIO_TYPE
            "0",  # P25NAC
            "0",  # NUMBER_TAG
            "OFF",  # ALT_COLOR
            "0",  # ALT_PATTERN
            "0",  # VOL_OFFSET
        ]
        response = self.send_command(ser, f"CIN,{','.join(parts)}")
        response_str = ensure_str(response)
        self.exit_programming_mode(ser)
        return self.feedback(
            "OK" in response_str, f"Channel {index} written → {response_str}"
        )
    except Exception as e:
        return self.feedback(False, f"Error writing channel info: {e}")


def read_global_lockout(self, ser):
    """Read global lockout frequencies.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: Lockout frequency data or error message.
    """
    try:
        self.enter_programming_mode(ser)
        results = []
        while True:
            response = self.send_command(ser, "GLF")
            response_str = ensure_str(response)

            if response_str.strip() == "GLF,-1":
                break
            results.append(response_str.strip())
        self.exit_programming_mode(ser)
        return "\n".join(results)
    except Exception as e:
        return self.feedback(False, f"Error reading global lockout: {e}")
