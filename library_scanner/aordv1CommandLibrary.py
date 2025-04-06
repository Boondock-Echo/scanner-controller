def getHelp(command=None):
    help_map = {
        "WI": "WI: Identify AR-DV1",
        "VR": "VR: Firmware version",
        "RF": "RF: Set/Read receive frequency",
        "MD": "MD: Mode control",
        "AG": "AG: Audio gain (00–99)",
        "ST": "ST: Frequency step (kHz)",
        "SH": "SH: Frequency step adjustment",
        "SQ": "SQ: Squelch selection",
        "NQ": "NQ: Noise squelch level",
        "LQ": "LQ: Level squelch level",
        "VQ": "VQ: Voice squelch",
        "CI": "CI: Tone squelch on/off",
        "CN": "CN: Tone squelch frequency",
        "DI": "DI: DCS on/off",
        "DS": "DS: DCS code",
        "DC": "DC: Simple encryption decode",
        "RX": "RX: Receiver status",
        "ZP": "ZP: Power on",
        "QP": "QP: Power off",
        "EX": "EX: Exit remote control"
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
        if response.startswith("?") or "ERR" in response.upper():
            raise Exception(f"{self.name}: Command returned an error: {response}")
        return self.parser(response) if self.parser else response

def listCommands():
    return [
        ("WI", "Identify AR-DV1", False),
        ("VR", "Firmware version", False),
        ("RF", "Set/Read receive frequency", False),
        ("MD", "Mode control", False),
        ("AG", "Audio gain (00–99)", False),
        ("ST", "Frequency step (kHz)", False),
        ("SH", "Frequency step adjustment", False),
        ("SQ", "Squelch selection", False),
        ("NQ", "Noise squelch level", False),
        ("LQ", "Level squelch level", False),
        ("VQ", "Voice squelch", False),
        ("CI", "Tone squelch on/off", False),
        ("CN", "Tone squelch frequency", False),
        ("DI", "DCS on/off", False),
        ("DS", "DCS code", False),
        ("DC", "Simple encryption decode", False),
        ("RX", "Receiver status", False),
        ("ZP", "Power on", False),
        ("QP", "Power off", False),
        ("EX", "Exit remote control", False),
    ]

commands = {
    "WI": scanner_command("WI"),
    "VR": scanner_command("VR"),
    "RF": scanner_command("RF"),
    "MD": scanner_command("MD"),
    "AG": scanner_command("AG"),
    "ST": scanner_command("ST"),
    "SH": scanner_command("SH"),
    "SQ": scanner_command("SQ"),
    "NQ": scanner_command("NQ"),
    "LQ": scanner_command("LQ"),
    "VQ": scanner_command("VQ"),
    "CI": scanner_command("CI"),
    "CN": scanner_command("CN"),
    "DI": scanner_command("DI"),
    "DS": scanner_command("DS"),
    "DC": scanner_command("DC"),
    "RX": scanner_command("RX"),
    "ZP": scanner_command("ZP"),
    "QP": scanner_command("QP"),
    "EX": scanner_command("EX"),
}
