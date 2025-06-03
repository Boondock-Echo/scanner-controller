"""
This module provides utility functions and classes for scanner control.

It includes serial buffer management and command handling.
"""

import logging
import time


class scanner_command:
    """
    Represent a scanner command with validation, formatting, and parsing.

    This class is used to construct commands for a scanner, validate input
    values,
    format commands for sending, and parse responses from the scanner.
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
                for the command value.
            query_format (str, optional): The format string for query commands.
            set_format (str, optional): The format string for set commands.
            validator (callable, optional): A function to validate the command
            value.
            parser (callable, optional): A function to parse the response from
            the scanner.
            requires_prg (bool, optional): Whether the command requires a
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
            value (optional): The value to set for the command.
                If None, a query command is built.

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
                (
                    f"{self.name}: Value must be between {self.valid_range[0]} "
                    f"and {self.valid_range[1]}."
                )
            )
        return f"{self.set_format.format(value=value)}\r"

    def parseResponse(self, response):
        """
        Parse the response from the scanner.

        Args:
            response (str): The raw response string from the scanner.

        Returns:
            str: The parsed response if a parser is provided, otherwise the raw
            response.

        Raises:
            Exception: If the response contains an error.
        """
        response = response.strip()
        # Some valid responses can include the substring "ERR" (e.g. "CARRIER").
        # Consider it an error only when the response actually begins with "ERR".
        if response.upper().startswith("ERR"):
            raise Exception(
                f"{self.name}: Command returned an error: {response}"
            )
        return self.parser(response) if self.parser else response


def clear_serial_buffer(ser):
    """
    Clear accumulated data in the serial buffer before sending commands.

    This function clears the serial input and output buffers before sending
    commands.
    """
    try:
        time.sleep(0.2)
        while ser.in_waiting:
            ser.read(ser.in_waiting)
        logging.debug("Serial buffer cleared.")
    except Exception as e:
        logging.error(f"Error clearing serial buffer: {e}")
