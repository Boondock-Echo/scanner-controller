"""
Adapter module.

This module provides functionality related to adapter.
"""

import logging
import time


class scanner_command:
    """
    Represents a scanner command with validation and parsing capabilities.

    Attributes:
        name (str): The name of the command.
        valid_range (tuple, optional): The valid range for the command value.
        query_format (str, optional): The format for query commands.
        set_format (str, optional): The format for set commands.
        validator (callable, optional): A function to validate the command
            value.
        parser (callable, optional): A function to parse the command response.
        requires_prg (bool): Indicates if the command requires PRG mode.
        help (str, optional): Help text for the command.
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
        Initialize a scanner_command instance.

        Args:
            name (str): The name of the command.
            valid_range (tuple, optional): The valid range for the command
            value.
            query_format (str, optional): The format for query commands.
            set_format (str, optional): The format for set commands.
            validator (callable, optional): A function to validate the command
            value.
            parser (callable, optional): A function to parse the command
            response.
            requires_prg (bool): Indicates if the command requires PRG mode.
            help (str, optional): Help text for the command.
        """
        self.name = name.upper()
        self.valid_range = valid_range
        self.query_format = query_format if query_format else self.name
        self.set_format = set_format if set_format else f"{self.name},{{value}}"
        self.validator = validator
        self.parser = parser
        self.requires_prg = requires_prg
        self.help = help  # optional help text

    def buildCommand(self, value=None):
        """
        Build the command string to send to the scanner.

        Args:
            value (optional): The value to set for the command.

        Returns:
            str: The formatted command string.
        """
        if value is None:
            return f"{self.query_format}\r"
        if self.validator:
            self.validator(value)
        elif self.valid_range and not (
            self.valid_range[0] <= value <= self.valid_range[1]
        ):
            raise ValueError(
                f"{self.name}: Value must be between "
                f"{self.valid_range[0]} and {self.valid_range[1]}."
            )
        return f"{self.set_format.format(value=value)}\r"

    def parseResponse(self, response):
        """
        Parse the response from the scanner.

        Args:
            response (str): The raw response string.

        Returns:
            str: The parsed response or the raw response if no parser is
            provided.

        Raises:
            Exception: If the response contains an error.
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

    Args:
        ser: The serial connection object.
    """
    try:
        time.sleep(0.2)
        while ser.in_waiting:
            ser.read(ser.in_waiting)
        logging.debug("Serial buffer cleared.")
    except Exception as e:
        logging.error(f"Error clearing serial buffer: {e}")


def parse_frequency_response(response):
    """
    Parse the frequency response from the scanner.

    Args:
        response (str): The raw response string.

    Returns:
        float or None: The parsed frequency value, or None if parsing fails.
    """
    try:
        # Example: Parse the response assuming it returns
        # "STS,<frequency>,<other_data>"
        if response.startswith("STS,"):
            parts = response.split(",")
            if len(parts) > 1:
                return float(parts[1])  # Extract frequency from second field
            else:
                raise ValueError("Invalid STS response format.")
        else:
            raise ValueError("Unexpected response format.")
    except Exception as e:
        logging.error(f"Error parsing frequency response: {response} - {e}")
        return None


def send_command_and_parse_response(command, serial_connection):
    """
    Send a command to the scanner and parse the response.

    Args:
        command (str): The command string to send.
        serial_connection: The serial connection object.

    Returns:
        float or None: The parsed frequency value, or None if no valid
        response is found.
    """
    try:
        # Clear the serial buffer before sending the command
        clear_serial_buffer(serial_connection)

        # Send the command
        serial_connection.write(command.encode())
        logging.debug(f"Command sent: {command} (type: {type(command)})")

        # Allow time for the scanner to respond
        time.sleep(0.1)

        # Read the response and handle decoding errors
        raw_response = (
            serial_connection.read(serial_connection.in_waiting)
            .decode("utf-8", errors="ignore")
            .strip()
        )
        logging.debug(f"Raw response received: {raw_response}")

        # Split the response into lines and process each line
        for line in raw_response.splitlines():
            logging.debug(f"Processing line: {line}")
            if line.startswith("STS,") or line.startswith("PWR,"):
                return parse_frequency_response(line)

        # If no valid response is found, log an error
        logging.error(f"No valid response found in: {raw_response}")
        return None

    except Exception as e:
        logging.error(f"Error sending command '{command}': {e}")
        return None
