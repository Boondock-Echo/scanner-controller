"""
Provides a Python interface for the scanner device.

This module provides functionality for interacting with a scanner device via
serial communication. It includes classes and functions for sending commands,
parsing responses, and handling errors.
"""

import logging
import time


class scanner_command:
    """
    Represent a command for the scanner device.

    This class encapsulates the details of a scanner command, including its
    name, valid range, formats for querying and setting values, validation
    logic, and response parsing functionality.
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
            valid_range (tuple, optional): A tuple specifying the valid range
            for the command's value.
            query_format (str, optional): The format string for querying the
            command.
            set_format (str, optional): The format string for setting the
            command's value.
            validator (callable, optional): A function to validate the command's
            value.
            parser (callable, optional): A function to parse the command's
            response.
            requires_prg (bool, optional): Indicates if the command requires a
            program mode.
            help (str, optional): Help text describing the command.
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
        Build a command string for the scanner.

        Args:
            value (optional): The value to set for the command. If None, a query
            command is built.

        Returns:
            str: The formatted command string.

        Raises:
            ValueError: If the value is out of the valid range.
        """
        if value is None:
            return f"{self.query_format}\r"
        if self.validator:
            self.validator(value)
        elif self.valid_range and not (
            self.valid_range[0] <= value <= self.valid_range[1]
        ):
            raise ValueError(
                f"{self.name}: Value must be between {self.valid_range[0]} and "
                f"{self.valid_range[1]}."
            )
        return f"{self.set_format.format(value=value)}\r"

    def parseResponse(self, response):
        """
        Parse the response from the scanner.

        Args:
            response (str): The raw response string from the scanner.

        Returns:
            str: The parsed response if a parser is provided,
            otherwise the raw response.

        Raises:
            Exception: If the response contains an error.
        """
        response = response.strip()
        if response == "ERR" or "ERR" in response:
            raise Exception(
                f"{self.name}: Command returned an error: {response}"
            )
            raise Exception(
                f"{self.name}: Command returned an error: {response}"
            )
        return self.parser(response) if self.parser else response


def clear_serial_buffer(ser):
    """
    Clear any accumulated data in the serial buffer before sending commands.

    This is important to ensure that the scanner receives clean commands
    without any leftover data from previous operations.
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

    This function assumes the response format is "STS,<frequency>,<other_data>"
    and extracts the frequency value.
    """
    try:
        # Example: Parse the response assuming it returns
        # "STS,<frequency>,<other_data>"
        # Example: Parse the response assuming it returns
        # "STS,<frequency>,<other_data>"
        if response.startswith("STS,"):
            parts = response.split(",")
            if len(parts) > 1:
                return float(
                    parts[1]
                )  # Extract the frequency from the second field
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

    This function handles the serial communication with the scanner device,
    including sending the command, waiting for a response, and parsing the
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
