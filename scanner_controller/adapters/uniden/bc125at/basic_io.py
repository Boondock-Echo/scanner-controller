"""
Basic I/O functions for the BC125AT scanner.

Contains functions for reading and writing volume and squelch settings.
"""

import logging

from scanner_controller.adapters.uniden.common.core import ensure_str


def read_volume(self, ser):
    """
    Read the current volume setting from the scanner.

    Args:
        ser: Serial connection to the scanner

    Returns:
        int: Volume level (0-15)
    """
    try:
        # Send command and get response as bytes
        response = self.send_command(ser, "VOL")

        # Add better logging and debugging
        logging.debug(f"Raw volume response: {response!r}")

        if not response or response == b"":
            raise ValueError("Failed to read volume. No response from scanner.")

        # Convert to string for parsing
        response_str = ensure_str(response)
        logging.debug(f"Parsed response string: {response_str!r}")

        # Parse the response
        parts = response_str.split(",")
        if len(parts) < 2 or parts[0] != "VOL":
            raise ValueError(f"Invalid volume response: {response_str}")

        volume = int(parts[1])
        logging.debug(f"Read volume level: {volume}")
        return self.feedback(True, f"Volume: {volume}")
    except Exception as e:
        logging.error(f"Error in read_volume: {str(e)}")
        return self.feedback(False, f"Error reading volume: {str(e)}")


def write_volume(self, ser, level):
    """
    Set the volume level on the scanner.

    Args:
        ser: Serial connection to the scanner
        level (int): Volume level (0-15)

    Returns:
        bool: True if successful

    Raises:
        ValueError: If volume level is out of range
    """
    # Validate volume level
    try:
        level = int(level)
        if not 0 <= level <= 15:
            return self.feedback(
                False, f"Volume level must be between 0-15, got {level}"
            )
    except ValueError:
        return self.feedback(False, f"Invalid volume level: {level}")

    try:
        # Send command to set volume
        response = self.send_command(ser, f"VOL,{level}")

        # Add debug logging
        logging.debug(f"Volume write response: {response!r}")

        if not response:
            return self.feedback(
                False, "Failed to set volume. No response from scanner."
            )

        # Ensure response is a string before checking
        response_str = ensure_str(response)

        # Check response
        if "OK" not in response_str:
            return self.feedback(
                False,
                f"Failed to set volume. Unexpected response: {response_str}",
            )

        logging.debug(f"Set volume to {level}")
        return self.feedback(True, f"Volume set to {level}")
    except Exception as e:
        logging.error(f"Error in write_volume: {str(e)}")
        return self.feedback(False, f"Error setting volume: {str(e)}")


def read_squelch(self, ser):
    """
    Read the current squelch setting from the scanner.

    Args:
        ser: Serial connection to the scanner

    Returns:
        int: Squelch level (0-15)
    """
    try:
        response = self.send_command(ser, "SQL")
        logging.debug(
            f"Raw squelch response: {response!r} (type: {type(response)})"
        )

        if not response or response == b"":
            return self.feedback(
                False, "Failed to read squelch. No response from scanner."
            )

        # Convert to string for parsing
        response_str = ensure_str(response)
        logging.debug(f"Converted response: {response_str!r}")

        # Parse the response
        parts = response_str.split(",")
        if len(parts) < 2 or parts[0] != "SQL":
            return self.feedback(
                False, f"Invalid squelch response format: {response_str}"
            )

        try:
            squelch = int(parts[1])
            logging.debug(f"Parsed squelch level: {squelch}")
            return self.feedback(True, f"Squelch: {squelch}")
        except (ValueError, IndexError):
            return self.feedback(
                False, f"Could not parse squelch level from: {response_str}"
            )

    except Exception as e:
        logging.error(f"Error in read_squelch: {str(e)}")
        return self.feedback(False, f"Error reading squelch: {str(e)}")


def write_squelch(self, ser, level):
    """
    Set the squelch level on the scanner.

    Args:
        ser: Serial connection to the scanner
        level (int): Squelch level (0-15)

    Returns:
        bool: True if successful

    Raises:
        ValueError: If squelch level is out of range
    """
    try:
        # Validate squelch level
        level = int(level)
        if not 0 <= level <= 15:
            return self.feedback(
                False, f"Squelch level must be between 0-15, got {level}"
            )

        # Send command to set squelch
        response = self.send_command(ser, f"SQL,{level}")
        logging.debug(f"Squelch write response: {response!r}")

        if not response:
            return self.feedback(
                False, "Failed to set squelch. No response from scanner."
            )

        response_str = ensure_str(response)

        if "OK" not in response_str:
            return self.feedback(
                False,
                f"Failed to set squelch. Unexpected response: {response_str}",
            )

        logging.debug(f"Set squelch to {level}")
        logging.info(f"Successfully set squelch to {level}")
        return self.feedback(True, f"Squelch set to {level}")
    except Exception as e:
        logging.error(f"Error in write_squelch: {str(e)}")
        return self.feedback(False, f"Error setting squelch: {str(e)}")
