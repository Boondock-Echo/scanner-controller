import logging
import os
import sys
import time


# Add the project root directory to the Python path if needed
def ensure_root_in_path():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    if root_dir not in sys.path:
        sys.path.insert(0, root_dir)


# Call this function when the module is imported
ensure_root_in_path()

# Shared utilities for scanner adapters


class scanner_command:
    """
    Defines a command that can be sent to a scanner
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
        Build a command string to send to the scanner
        """
        if value is None:
            return f"{self.query_format}\r"

        if self.validator:
            self.validator(value)
        elif self.valid_range and not (
            self.valid_range[0] <= value <= self.valid_range[1]
        ):
            raise ValueError(
                f"{self.name}: Value must be between {self.valid_range[0]} and {self.valid_range[1]}."
            )

        return f"{self.set_format.format(value=value)}\r"

    def parseResponse(self, response):
        """
        Parse the response from the scanner
        """
        response = response.strip()
        if response == "ERR" or "ERR" in response:
            raise Exception(f"{self.name}: Command returned an error: {response}")
        return self.parser(response) if self.parser else response


def clear_serial_buffer(ser):
    """
    Clears any accumulated data in the serial buffer before sending commands.
    """
    try:
        time.sleep(0.2)
        while ser.in_waiting:
            ser.read(ser.in_waiting)
        logging.debug("Serial buffer cleared.")
    except Exception as e:
        logging.error(f"Error clearing serial buffer: {e}")
