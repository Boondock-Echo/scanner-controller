"""
Status and information functions for the BC125AT scanner.

Contains functions for reading scanner status, battery voltage, etc.
"""

from adapters.uniden.common.core import ensure_str


def read_model(self, ser):
    """Read the scanner model from the BC125AT.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: Model information or error message.
    """
    try:
        response = self.send_command(ser, "MDL")
        return ensure_str(response)
    except Exception as e:
        return self.feedback(False, f"Error reading model: {e}")


def read_sw_ver(self, ser):
    """Read the scanner firmware version from the BC125AT.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: Firmware version or error message.
    """
    try:
        response = self.send_command(ser, "VER")
        return ensure_str(response)
    except Exception as e:
        return self.feedback(False, f"Error reading firmware version: {e}")


def read_rssi(self, ser):
    """Read the signal strength from the BC125AT.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        float or str: RSSI value as float or error message.
    """
    try:
        response = self.send_command(ser, "PWR")
        response_str = ensure_str(response)

        parts = response_str.split(",")
        if len(parts) == 3:
            return round(int(parts[1]) / 1023.0, 3)
        return self.feedback(False, f"Unexpected PWR response: {response_str}")
    except Exception as e:
        return self.feedback(False, f"Error reading RSSI: {e}")


def read_battery_voltage(self, ser):
    """Read the battery voltage from the BC125AT.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        float or str: Battery voltage or error message.
    """
    try:
        response = self.send_command(ser, "BAV")
        response_str = ensure_str(response)

        _, val = response_str.split(",")
        voltage = (3.2 * int(val) * 2) / 1023
        return round(voltage, 3)
    except Exception as e:
        return self.feedback(False, f"Error reading battery voltage: {e}")


def read_window_voltage(self, ser):
    """Read the window voltage from the BC125AT.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: Window voltage response or error message.
    """
    try:
        response = self.send_command(ser, "WIN")
        return ensure_str(response)
    except Exception as e:
        return self.feedback(False, f"Error reading window voltage: {e}")


def read_status(self, ser):
    """Read the scanner status from the BC125AT.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: Status response or error message.
    """
    try:
        response = self.send_command(ser, "STS")
        return ensure_str(response)
    except Exception as e:
        return self.feedback(False, f"Error reading status: {e}")


def read_s_meter(self, ser):
    """S-meter (not supported on BC125AT).

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: Error message indicating feature not supported.
    """
    return self.feedback(False, "S-Meter not supported on BC125AT")
