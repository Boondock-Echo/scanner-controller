"""
Status and information functions for the BCD325P2 scanner.

Contains functions for reading scanner status, battery voltage, etc.
"""

from adapters.uniden.common.core import ensure_str


def read_battery_voltage(self, ser):
    """Read the battery voltage from the BCD325P2.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        float or str: Battery voltage or error message.
    """
    try:
        response = self.send_command(ser, "BAV")
        # Decode bytes to string
        response_str = ensure_str(response)

        _, val = response_str.split(",")
        voltage = (3.2 * int(val) * 2) / 1023
        return round(voltage, 3)
    except Exception as e:
        return self.feedback(False, f"Error reading battery voltage: {e}")


def read_window_voltage(self, ser):
    """Read the window voltage from the BCD325P2.

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
    """Read the scanner status from the BCD325P2.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: Status response or error message.
    """
    try:
        response = self.send_command(ser, "STS")
        # Return as string for consistency
        return ensure_str(response)
    except Exception as e:
        return self.feedback(False, f"Error reading status: {e}")


def read_s_meter(self, ser):
    """Read S-Meter value.

    Args:
        ser: Serial connection to the scanner.

    Returns:
        str: S-Meter value or error message.
    """
    try:
        response = self.send_command(ser, "PWR")
        response_str = ensure_str(response)

        parts = response_str.split(",")
        if len(parts) >= 2:
            # Format S-meter value as a normalized reading
            strength = int(parts[1]) / 1023.0
            return f"S-Meter: {strength:.2f} ({parts[1]} raw)"
        return self.feedback(False, f"Unexpected response: {response_str}")
    except Exception as e:
        return self.feedback(False, f"Error reading S-meter: {e}")


def read_model(self, ser):
    """Read the scanner model.

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
    """Read the scanner firmware version.

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
