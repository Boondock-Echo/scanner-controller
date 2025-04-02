import textwrap
import time
from utilities.shared_utils import scanner_command, validate_enum

def getHelp(command=None):
    help_map = {
        "MDL": "MDL: Get model info",
        "VER": "VER: Get firmware version",
        "PRG": "PRG: Enter programming mode",
        "EPG": "EPG: Exit programming mode",
        "VOL": "VOL: Set volume level (0-29)",
        "SQL": "SQL: Set squelch level (0-19)",
        "BLT": "BLT: Backlight control",
        "BSV": "BSV: Battery saver info",
        "COM": "COM: COM port setting",
        "CLR": "CLR: Clear all memory",
        "KBP": "KBP: Key beep setting",
        "PRI": "PRI: Priority mode",
        "DCH": "DCH: Delete channel",
        "CIN": "CIN: Get/set channel info",
        "SCO": "SCO: Search/Close Call settings",
        "GLF": "GLF: Get global lockout freq",
        "ULF": "ULF: Unlock global freq",
        "LOF": "LOF: Lock out freq",
        "CLC": "CLC: Close Call config",
        "SSG": "SSG: Service Search Group setup",
        "CSG": "CSG: Custom Search Group setup",
        "CSP": "CSP: Custom Search Parameters",
        "WXS": "WXS: Weather settings",
        "CNT": "CNT: LCD contrast"
    }
    if command:
        print(help_map.get(command.upper(), "No help available for that command."))
    else:
        print("Type getHelp('COMMAND') for details.")

class scanner_command:
    def __init__(self, name, valid_range=None, query_format=None, set_format=None,
                 validator=None, parser=None, requires_prg=False):
        self.name = name.upper()
        self.valid_range = valid_range
        self.query_format = query_format if query_format else self.name
        self.set_format = set_format if set_format else f"{self.name},{{value}}"
        self.validator = validator
        self.parser = parser
        self.requires_prg = requires_prg

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

def listCommands():
    return [
        ("MDL", "Get model info", False),
        ("VER", "Get firmware version", False),
        ("PRG", "Enter programming mode", False),
        ("EPG", "Exit programming mode", False),
        ("VOL", "Set volume level (0-15)", False),
        ("SQL", "Set squelch level (0-15)", False),
        ("BLT", "Backlight control", True),
        ("BSV", "Battery saver info", True),
        ("COM", "COM port setting", True),
        ("CLR", "Clear all memory", True),
        ("KBP", "Key beep setting", True),
        ("PRI", "Priority mode", True),
        ("DCH", "Delete channel", True),
        ("CIN", "Get/set channel info", True),
        ("SCO", "Search/Close Call settings", True),
        ("GLF", "Get global lockout freq", True),
        ("ULF", "Unlock global freq", True),
        ("LOF", "Lock out freq", True),
        ("CLC", "Close Call config", True),
        ("SSG", "Service Search Group setup", True),
        ("CSG", "Custom Search Group setup", True),
        ("CSP", "Custom Search Parameters", True),
        ("WXS", "Weather settings", True),
        ("CNT", "LCD contrast", True),
    ]

commands = {
    "MDL": scanner_command("MDL"),
    "VER": scanner_command("VER"),
    "PRG": scanner_command("PRG"),
    "EPG": scanner_command("EPG"),
    "VOL": scanner_command("VOL", valid_range=(0, 29)),
    "SQL": scanner_command("SQL", valid_range=(0, 19)),
    "BLT": scanner_command("BLT", requires_prg=True),
    "BSV": scanner_command("BSV", requires_prg=True),
    "COM": scanner_command("COM", requires_prg=True),
    "CLR": scanner_command("CLR", requires_prg=True),
    "KBP": scanner_command("KBP", requires_prg=True),
    "PRI": scanner_command("PRI", requires_prg=True),
    "DCH": scanner_command("DCH", requires_prg=True),
    "CIN": scanner_command("CIN", requires_prg=True),
    "SCO": scanner_command("SCO", requires_prg=True),
    "GLF": scanner_command("GLF", requires_prg=True),
    "ULF": scanner_command("ULF", requires_prg=True),
    "LOF": scanner_command("LOF", requires_prg=True),
    "CLC": scanner_command("CLC", requires_prg=True),
    "SSG": scanner_command("SSG", requires_prg=True),
    "CSG": scanner_command("CSG", requires_prg=True),
    "CSP": scanner_command("CSP", requires_prg=True),
    "WXS": scanner_command("WXS", requires_prg=True),
    "CNT": scanner_command("CNT", requires_prg=True),
}
