import logging

# Configure logging
logging.basicConfig(
    filename="scanner_tool.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

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

"""
Command Library for Scanner Controller
Provides a unified interface to different scanner adapters.
"""

from adapters.uniden.bc125at_adapter import BC125ATAdapter
from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter

def getScannerInterface(model):
    """Return the appropriate adapter class based on scanner model"""
    if model.upper() == "BC125AT":
        return BC125ATAdapter
    elif model.upper() == "BCD325P2":
        return BCD325P2Adapter
    else:
        raise ValueError(f"Unsupported scanner model: {model}")

def readVolume(ser, model):
    """Read the volume level for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.readVolume(ser)

def writeVolume(ser, model, value):
    """Set the volume level for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.writeVolume(ser, value)

def readSquelch(ser, model):
    """Read the squelch level for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.readSquelch(ser)

def writeSquelch(ser, model, value):
    """Set the squelch level for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.writeSquelch(ser, value)

def readFrequency(ser, model):
    """Read the current frequency for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.readFrequency(ser)

def writeFrequency(ser, model, value):
    """Set the frequency for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.writeFrequency(ser, value)

def readRSSI(ser, model):
    """Read the RSSI for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.readRSSI(ser)

def readSMeter(ser, model):
    """Read the S-meter value for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.readSMeter(ser)

def readModel(ser, model):
    """Read the model information for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.readModel(ser)

def readSWVer(ser, model):
    """Read the software version for the specified scanner model"""
    adapter = getScannerInterface(model)()
    return adapter.readSWVer(ser)