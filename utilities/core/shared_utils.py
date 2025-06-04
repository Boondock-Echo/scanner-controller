"""
Shared utilities for scanner communication and control.

This module provides common functionality used across different scanner adapter
implementations, including command building and serial communication helpers.
"""

import logging
import os
import sys
import time


def ensure_root_in_path():
    """
    Add the project root directory to the Python path if not already included.

    This ensures that imports from the project root work correctly regardless
    of where the script is run from.
    """
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)


# Call this function when the module is imported
ensure_root_in_path()


class scanner_command:
    """
    Defines a command that can be sent to a scanner.

    This class encapsulates the logic for building command strings,
    validating command parameters, and parsing responses from the scanner.
    """

    def __init__(
        self,
        name,
        valid_range=None,
        query_format=None,
        set_format=None,
        validator=None,
        parser=None,
        requires_prg=False,
        help=None,
    ):
        """
        Initialize a scanner command with its properties and behavior.

        Parameters:
            name (str): Command name, will be converted to uppercase
            valid_range (tuple): Optional (min, max) value range for validation
            query_format (str): Format string for query commands
            set_format (str): Format string for set commands with {value}
            placeholder validator (callable): Optional custom validation
            function parser (callable): Optional response parser function
            requires_prg (bool): Whether the command requires programming mode
            help (str): Optional help text describing the command
        """
        self.name = name.upper()
        self.valid_range = valid_range
        self.query_format = query_format if query_format else self.name
        self.set_format = set_format if set_format else f"{self.name},{{value}}"
        self.validator = validator
        self.parser = parser
        self.requires_prg = requires_prg
        self.help = help  # optional help text

    def build_command(self, value=None):
        """
        Build a command string to send to the scanner.

        Parameters:
            value: Optional value to set. If None, builds a query command.

        Returns:
            str: Formatted command string ending with carriage return.

        Raises:
            ValueError: If the value fails validation.
        """
        if value is None:
            return f"{self.query_format}\r"

        if self.validator:
            self.validator(value)
        elif self.valid_range and not (
            self.valid_range[0] <= value <= self.valid_range[1]
        ):
            raise ValueError(
                f"{self.name}: Value must be between {self.valid_range[0]} "
                f"and {self.valid_range[1]}."
            )

        return f"{self.set_format.format(value=value)}\r"

    def parse_response(self, response):
        """
        Parse the response from the scanner.

        Parameters:
            response (str): Raw response string from the scanner

        Returns:
            The parsed response value. Type depends on the parser function.

        Raises:
            Exception: If the response indicates an error.
        """
        response = response.strip()
        if response == "ERR" or "ERR" in response:
            raise Exception(
                f"{self.name}: Command returned an error: {response}"
            )
        return self.parser(response) if self.parser else response


def clear_serial_buffer(ser):
    """
    Clear any accumulated data in the serial buffer before sending commands.

    This helps prevent misinterpreting stale data as responses to new commands.

    Parameters:
        ser: An open serial.Serial connection to the scanner

    Raises:
        Exception: If there's an error accessing the serial port
    """
    try:
        time.sleep(0.2)
        while ser.in_waiting:
            ser.read(ser.in_waiting)
        logging.debug("Serial buffer cleared.")
    except Exception as e:
        logging.error(f"Error clearing serial buffer: {e}")


def send_command(ser, cmd):
    """
    Clear the buffer and send a command (with CR termination) to the device.

    Args:
        ser: An open serial connection object
        cmd: Command string to send

    Returns:
        str: Response from the device as a string
    """
    clear_serial_buffer(ser)
    full_cmd = cmd.strip() + "\r"
    try:
        ser.write(full_cmd.encode("utf-8"))
        logging.info(f"Sent command: {cmd}")
    except Exception as e:
        logging.error(f"Error sending command {cmd}: {e}")
        return ""
    return read_response(ser)


def read_response(ser, timeout=1.0):
    """
    Read a response from the serial port with a timeout.

    Args:
        ser: An open serial connection object
        timeout: Maximum time to wait for a response

    Returns:
        str: The response from the device as a string
    """
    ser.timeout = timeout
    response = ser.read_until(b"\r").decode("utf-8").strip()
    logging.debug(f"Received response: {response}")
    return response


def diagnose_connection_issues():
    """
    Diagnose common connection issues with the scanner.

    This function checks for common problems such as unavailable serial ports,
    incorrect baud rates, or other hardware-related issues.
    """
    import serial.tools.list_ports

    print("\nDiagnosing connection issues...")
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print("No serial ports detected. Ensure the scanner is connected.")
        return

    print("Available serial ports:")
    for port in ports:
        print(f"  - {port.device}: {port.description}")

    print("\nSuggestions:")
    print("  1. Verify the scanner is powered on.")
    print("  2. Check that the correct port is selected.")
    print("  3. Ensure no other application is using the port.")
    print("  4. Try reconnecting the scanner or using a different USB port.")
