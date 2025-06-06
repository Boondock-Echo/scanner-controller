"""
This module is a unified interface for interacting with any scanner model.

It includes functionality for building and parsing scanner commands, as
well as reading and writing various scanner parameters such as volume, squelch,
frequency, RSSI, and more.

Classes:
    ScannerCommand: Represents a scanner command with functionality to build
                     and parse commands.

Functions:
    get_scanner_interface(model): Returns the appropriate adapter class for the
                               specified scanner model.
    read_volume(ser, model): Reads the volume level for the specified scanner
                           model.
    write_volume(ser, model, value): Sets the volume level for the specified
                                   scanner model.
    read_squelch(ser, model): Reads the squelch level for the specified scanner
                            model.
    write_squelch(ser, model, value): Sets the squelch level for the specified
                                    scanner model.
    read_frequency(ser, model): Reads the current frequency for the specified
                              scanner model.
    write_frequency(ser, model, value): Sets the frequency for the specified
                                      scanner model.
    read_rssi(ser, model): Reads the RSSI (Received Signal Strength Indicator)
                         for the specified scanner model.
    read_smeter(ser, model): Reads the S-meter value for the specified scanner
                           model.
    read_model(ser, model): Reads the model information for the specified
                          scanner model.
    read_swver(ser, model): Reads the software version for the specified scanner
                          model.

Usage:
    This module is designed to work with specific scanner models and their
    respective adapters. It provides a high-level interface for interacting
    with scanners, abstracting away the low-level communication details.

Dependencies:
    - logging: Used for logging command execution details.
    - adapters.uniden.bc125at_adapter: Adapter for the BC125AT scanner model.

Exceptions:
    - ValueError: Raised when an invalid value is provided for a command or an
                 unsupported scanner model is specified.
    - Exception: Raised when a scanner command returns an error response.

Note:
    Ensure that the appropriate adapter modules are available and that the
    scanner is properly connected before using this module.

Command Library module.
This module provides functionality related to command library.
"""

# Import centralized logging utilities
from utilities.log_utils import get_logger

# Get a logger for this module
logger = get_logger(__name__)


class ScannerCommand:
    """Scanner command handler for serial communications with scanner devices.

    This class encapsulates the behavior of commands sent to scanner devices,
    including validation, formatting, and response parsing.

    Attributes:
        name: The command name (uppercase)
        valid_range: Optional tuple with (min, max) range for valid values
        query_format: Format string for query commands
        set_format: Format string for setting values with {value} placeholder
        validator: Optional function to perform custom validation
        parser: Optional function to transform responses
        requires_prg: Whether the command requires programming mode
        help: Optional help text describing the command
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
        """Initialize a ScannerCommand with validation and parsing options.

        Args:
            name: Command name (will be converted to uppercase)
            valid_range: Optional tuple of (min, max) for valid values
            query_format: Format string for query commands
            set_format: Format string for set commands with {value} placeholder
            validator: Optional function for custom validation
            parser: Optional function to transform responses
            requires_prg: Whether command requires programming mode
            help: Optional help text describing the command
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
        r"""
        Build a formatted command string to send to the scanner.

        This method constructs either a query or set command based on input:
        - If no value is provided, generates a query command using query_format
        - If a value is provided, generates a set command using set_format

        Parameters:
            value: The value to set (optional). If None, builds a query command.

        Returns:
            str: Formatted command string with carriage return appended

        Raises:
            ValueError: If validation fails for the provided value
                - When the value is outside the valid_range
                - When a custom validator rejects the value

        Examples:
            # Query the current volume
            cmd.build_command()    # Returns: "VOL\r"

            # Set volume to 5
            cmd.build_command(5)   # Returns: "VOL,5\r"
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
        Parse and validate the response received from the scanner.

        This method handles error checking and optional transformation of
        the scanner's response through a custom parser function.

        Parameters:
            response (str): The raw response string from the scanner

        Returns:
            The parsed response value (type depends on the parser function)

        Raises:
            Exception: If the response contains an error indication
        """
        response = response.strip()
        if response == "ERR" or "ERR" in response:
            raise Exception(
                f"{self.name}: Command returned an error: {response}"
            )
        return self.parser(response) if self.parser else response


"""
Command Library for Scanner Controller
Provides a unified interface to different scanner adapters.
"""


def get_scanner_interface(model):
    """Return the appropriate adapter class based on scanner model."""
    if model.upper() == "BC125AT":
        from adapters.uniden.bc125at_adapter import BC125ATAdapter

        return BC125ATAdapter
    elif model.upper() == "BCD325P2":
        from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter

        return BCD325P2Adapter
    else:
        raise ValueError(f"Unsupported scanner model: {model}")


def read_volume(ser, model):
    """Read the volume level for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.read_volume(ser)


def write_volume(ser, model, value):
    """Set the volume level for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.write_volume(ser, value)


def read_squelch(ser, model):
    """Read the squelch level for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.read_squelch(ser)


def write_squelch(ser, model, value):
    """Set the squelch level for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.write_squelch(ser, value)


def read_frequency(ser, model):
    """Read the current frequency for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.read_frequency(ser)


def write_frequency(ser, model, value):
    """Set the frequency for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.write_frequency(ser, value)


def read_rssi(ser, model):
    """Read the RSSI for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.read_rssi(ser)


def read_smeter(ser, model):
    """Read the S-meter value for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.read_smeter(ser)


def read_model(ser, model):
    """Read the model information for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.read_model(ser)


def read_swver(ser, model):
    """Read the software version for the specified scanner model."""
    adapter = get_scanner_interface(model)()
    return adapter.read_swver(ser)
