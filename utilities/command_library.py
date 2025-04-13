r"""
Command Library Module.

This module provides a framework for defining, validating, and executing scanner
commands. It standardizes the way the application communicates with different
scanner models by abstracting command formatting, parameter validation, and
response parsing.

The primary class, scanner_command, represents a specific command that can be
sent to a scanner. Commands can be used for both querying scanner state and
configuring scanner settings.

Examples:
    # Create a command to get/set volume
    vol_cmd = scanner_command(
        name="VOL",
        valid_range=(0, 15),
        help="Control scanner audio volume"
    )

    # Query current volume
    query_cmd = vol_cmd.buildCommand()  # Returns "VOL\r"

    # Set volume to 8
    set_cmd = vol_cmd.buildCommand(8)   # Returns "VOL,8\r"
"""

import logging

# Configure logging
logging.basicConfig(
    filename="scanner_tool.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class scanner_command:
    """
    Scanner command class for building and parsing scanner commands.

    This class encapsulates all the information needed to format, validate,
    and parse a specific scanner command. It handles both query commands
    (requesting information from the scanner) and set commands (changing
    scanner settings).

    Each command can have custom validation rules, formatting templates,
    and response parsing logic. This allows for handling the variety of
    command formats across different scanner models and protocols.

    Workflow:
    1. Create command instances for each scanner operation
    2. Use buildCommand() to generate properly formatted command strings
    3. Send the command string to the scanner via serial connection
    4. Parse the response using parseResponse()
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
        Initialize a scanner command with formatting and validation rules.

        Args:
            name (str): The command name (will be converted to uppercase)
                Example: "VOL", "MDL", "FRQ"

            valid_range (tuple, optional): A tuple defining (min, max) values
                Example: (0, 15) for volume limits

            query_format (str, optional): Format string for read/query commands
                Default is the command name itself
                Example: "MDL" to query the model number

            set_format (str, optional): Format string for write/set commands
                with {value} placeholder. Default is "{command},{value}"
                Example: "VOL,{value}" for setting volume

            validator (callable, optional): Custom function to validate inputs
                Function signature: validator(value) -> None
                (raises ValueError if invalid)
                Example: lambda x: x.isdigit() or raise ValueError("Numeric")

            parser (callable, optional): Custom function to parse response data
                Function signature: parser(response_string) -> parsed_data
                Example: lambda x: int(x.split(',')[1])

            requires_prg (bool, optional): Whether command requires the scanner
                to be in programming mode. Default is False

            help (str, optional): Help text explaining the command's purpose
                Example: "Sets or queries the scanner volume (0-15)"
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
        Build a formatted command string to send to the scanner.

        Args:
            value: Optional value for set commands, None for query commands

        Returns:
            Formatted command string with carriage return

        Raises:
            ValueError: If the value fails validation
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

    def parseResponse(self, response):
        """
        Parse the response from the scanner.

        Args:
            response: The raw response string from the scanner

        Returns:
            Parsed response data

        Raises:
            Exception: If the response contains an error
        """
        response = response.strip()
        if response == "ERR" or "ERR" in response:
            raise Exception(
                f"{self.name}: Command returned an error: {response}"
            )
        return self.parser(response) if self.parser else response
