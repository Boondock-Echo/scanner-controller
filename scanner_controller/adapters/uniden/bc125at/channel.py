"""
Channel-related functions for the BC125AT scanner.

Contains functions for reading and writing channel information.
"""

import time

from scanner_controller.adapters.uniden.common.core import ensure_str


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
        return self.feedback(True, f"Channel {index}: {response_str}")
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
            "0",  # Skip parameter
        ]
        response = self.send_command(ser, f"CIN,{','.join(parts)}")
        response_str = ensure_str(response)
        self.exit_programming_mode(ser)
        return self.feedback(
            "OK" in response_str, f"Channel {index} written → {response_str}"
        )
    except Exception as e:
        return self.feedback(False, f"Error writing channel info: {e}")


def read_global_lockout(self, ser, timeout=5):
    """Read global lockout frequencies.

    Parameters
    ----------
    ser : serial.Serial
        Serial connection to the scanner.
    timeout : float, optional
        Maximum time in seconds to wait for the ``GLF,-1`` sentinel.

    Returns
    -------
    str
        Lockout frequency data or an error message if timed out.
    """
    try:
        self.enter_programming_mode(ser)
        results = []
        start = time.time()
        while True:
            if time.time() - start > timeout:
                self.exit_programming_mode(ser)
                return self.feedback(
                    False,
                    f"Timed out waiting for GLF,-1 after {timeout} seconds",
                )

            response = self.send_command(ser, "GLF")
            response_str = ensure_str(response).strip()

            if response_str == "GLF,-1":
                break
            results.append(response_str)
        self.exit_programming_mode(ser)
        return self.feedback(True, "\n".join(results))
    except Exception as e:
        return self.feedback(False, f"Error reading global lockout: {e}")
