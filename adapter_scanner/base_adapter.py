"""
This module provides the base classes for scanner commands and scanner adapters.

Classes:
- scanner_command: Represents a command that can be sent to a scanner.
- BaseScannerAdapter: Provides a base implementation for scanner adapter functionality.
"""


class scanner_command:
    """
    Represent a command that can be sent to a scanner.

    Attributes:
        name (str): The name of the command.
        valid_range (tuple, optional): The valid range for the command value.
        query_format (str, optional): The format for query commands.
        set_format (str, optional): The format for set commands.
        validator (callable, optional): A function to validate the command value.
        parser (callable, optional): A function to parse the command response.
        requires_prg (bool): Indicates if the command requires programming mode.
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
            valid_range (tuple, optional): The valid range for the command value.
            query_format (str, optional): The format for query commands.
            set_format (str, optional): The format for set commands.
            validator (callable, optional): A function to validate the command value.
            parser (callable, optional): A function to parse the command response.
            requires_prg (bool): Indicates if the command requires programming mode.
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
        Build a command string to send to the scanner.

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
        Parse the response received from the scanner.

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
            raise Exception(f"{self.name}: Command returned an error: {response}")
        return self.parser(response) if self.parser else response


class BaseScannerAdapter:
    """
    Base class for scanner adapters.

    This class provides default implementations for various scanner operations,
    which can be overridden by subclasses to provide specific functionality.
    """

    def readVolume(self, ser):
        """
        Read the volume level of the scanner.

        Args:
            ser: The serial connection to the scanner.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"

    def writeVolume(self, ser, value):
        """
        Write the volume level to the scanner.

        Args:
            ser: The serial connection to the scanner.
            value: The volume level to set.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"

    def readSquelch(self, ser):
        """
        Read the squelch value of the scanner.

        Args:
            ser: The serial connection to the scanner.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"

    def writeSquelch(self, ser, value):
        """
        Write the squelch value to the scanner.

        Args:
            ser: The serial connection to the scanner.
            value: The squelch value to set.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"

    def readFrequency(self, ser):
        """
        Read the frequency value of the scanner.

        Args:
            ser: The serial connection to the scanner.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"

    def writeFrequency(self, ser, value):
        """
        Write the frequency value to the scanner.

        Args:
            ser: The serial connection to the scanner.
            value: The frequency value to set.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"

    def readRSSI(self, ser):
        """
        Read the RSSI (Received Signal Strength Indicator) value of the scanner.

        Args:
            ser: The serial connection to the scanner.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"

    def readSMeter(self, ser):
        """
        Read the S-Meter value of the scanner.

        Args:
            ser: The serial connection to the scanner.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"

    def readModel(self, ser):
        """
        Read the model information of the scanner.

        Args:
            ser: The serial connection to the scanner.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"

    def readSWVer(self, ser):
        """
        Read the software version of the scanner.

        Args:
            ser: The serial connection to the scanner.

        Returns:
            str: A string indicating that the operation is not supported.
        """
        return "Not Supported"
