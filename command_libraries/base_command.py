"""
Base Command module.

This module provides functionality related to base command.
"""


class BaseCommand:
    """Base class for all scanner commands."""

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
        Initialize a BaseCommand instance.

        Args:
            name: Command name
            valid_range: Tuple of (min, max) for valid values
            query_format: Format for query commands
            set_format: Format for set commands
            validator: Function to validate command values
            parser: Function to parse command responses
            requires_prg: Whether command requires programming mode
            help: Help text for the command
        """
        self.name = name.upper()
        self.valid_range = valid_range
        self.query_format = query_format if query_format else self.name
        self.set_format = (
            set_format if set_format else f"{self.name}, {{value}}"
        )
        self.validator = validator
        self.parser = parser
        self.requires_prg = requires_prg
        self.help = help

    def build_command(self, value=None):
        """Build a command string to send to the scanner."""
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

    def parse_response(self, response):
        """Parse the response from the scanner."""
        response = response.strip()
        if response == "ERR" or "ERR" in response:
            raise Exception(
                f"{self.name}: Command returned an error: {response}"
            )
        return self.parser(response) if self.parser else response
