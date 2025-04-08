"""
LEGACY ADAPTER - REDIRECTS TO NEW LOCATION
This file is kept for backward compatibility and redirects to adapters/base_adapter.py
"""

import warnings
warnings.warn(
    "Using adapter_scanner.base_adapter is deprecated. "
    "Please use adapters.base_adapter instead.",
    DeprecationWarning, 
    stacklevel=2
)

from adapters.base_adapter import BaseScannerAdapter

# Keep original scanner_command definition for backward compatibility
class scanner_command:
    def __init__(self, name, valid_range=None, query_format=None, set_format=None,
                 validator=None, parser=None, requires_prg=False, help=None):
        self.name = name.upper()
        self.valid_range = valid_range
        self.query_format = query_format if query_format else self.name
        self.set_format = set_format if set_format else f"{self.name},{{value}}"
        self.validator = validator
        self.parser = parser
        self.requires_prg = requires_prg
        self.help = help  # optional help text

    def buildCommand(self, value=None):
        if value is None:
            return f"{self.query_format}\r"
        if self.validator:
            self.validator(value)
        elif self.valid_range and not (self.valid_range[0] <= value <= self.valid_range[1]):
            raise ValueError(f"{self.name}: Value must be between {self.valid_range[0]} and {self.valid_range[1]}.")
        return f"{self.set_format.format(value=value)}\r"
    
    def parseResponse(self, response):
        response = response.strip()
        if response == "ERR" or "ERR" in response:
            raise Exception(f"{self.name}: Command returned an error: {response}")
        return self.parser(response) if self.parser else response