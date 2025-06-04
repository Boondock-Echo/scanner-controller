"""
This module is part of the scanner tool library.

This module provides the `scanner_command` class for building and parsing
commands for a scanner tool, with validation and logging capabilities.
"""

# Import centralized logging utilities
from utilities.log_utils import get_logger
from utilities.errors import CommandError

# Get a logger for this module
logger = get_logger(__name__)


class scanner_command:
    """
    A class representing a command for the scanner tool.

    Represents a command for the scanner tool, providing methods to build
    commands, validate input values, and parse responses from the scanner.

    Attributes:
        name (str): The name of the command.
        valid_range (tuple, optional): A tuple specifying the valid range
        for the command's value.
        query_format (str, optional): The format string for query commands.
        set_format (str, optional): The format string for set commands.
        validator (callable, optional): A custom validation function for the
        command's value.
        parser (callable, optional): A custom parsing function for the command's
        response.
        requires_prg (bool): Indicates if the command requires a program to be
        loaded.
        help (str, optional): Help text describing the command.
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
            query_format (str, optional): The format string for query commands.
            set_format (str, optional): The format string for set commands.
            validator (callable, optional): A custom validation function for the
            command's value.
            parser (callable, optional): A custom parsing function for the
            command's response.
            requires_prg (bool): Indicates if the command requires a program to
            be loaded.
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

    def build_command(self, value=None):
        """
        Build a command string for the scanner tool.

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
                (
                    f"{self.name}: Value must be between {self.valid_range[0]} "
                    f"and {self.valid_range[1]}."
                )
            )
        return f"{self.set_format.format(value=value)}\r"

    def parse_response(self, response):
        """
        Parse the response from the scanner tool.

        Args:
            response (str): The raw response string from the scanner.

        Returns:
            str: The parsed response, or the raw response if no parser is
            defined.

        Raises:
            Exception: If the response contains an error.
        """
        response = response.strip()
        # Treat only explicit error responses as errors. Some valid responses
        # may contain the substring "ERR" (e.g. "CARRIER"), so we check for
        # an actual error prefix instead of using ``in``.
        if response.upper().startswith("ERR"):
            raise CommandError(
                f"{self.name}: Command returned an error: {response}"
            )
        return self.parser(response) if self.parser else response
