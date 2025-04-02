import logging
from utilities.serial_utils import clear_serial_buffer, read_response, send_command, wait_for_data

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

def validate_enum(name, allowed_values):
    """
    Returns a validator function that checks if a given value is in allowed_values.

    Args:
        name (str): The name of the command (for error messages)
        allowed_values (Iterable[str]): A set or list of valid string values

    Returns:
        function: A validator function to pass into scanner_command
    """
    allowed_upper = {v.upper() for v in allowed_values}

    def validator(value):
        if str(value).upper() not in allowed_upper:
            raise ValueError(f"{name} must be one of: {', '.join(sorted(allowed_upper))}")
    return validator

def validate_cin(params):
    """
    Validates the argument list for the CIN command.

    Args:
        params (str or list): Should be a comma-separated string or list of values.

    Raises:
        ValueError: If the format or fields are invalid
    """
    if isinstance(params, str):
        parts = [p.strip() for p in params.split(",")]
    else:
        parts = list(params)

    if len(parts) not in {1, 9}:
        raise ValueError("CIN requires 1 (read) or 9 (write) arguments")

    index = int(parts[0])
    if not (1 <= index <= 500):
        raise ValueError("Index must be between 1 and 500")

    if len(parts) == 9:
        name = parts[1]
        freq = int(parts[2])
        mod = parts[3].upper()
        ctcss = int(parts[4])
        delay = int(parts[5])
        lockout = int(parts[6])
        priority = int(parts[7])

        if len(name) > 16:
            raise ValueError("Name must be 16 characters or fewer")

        if not (10000 <= freq <= 1300000):
            raise ValueError("Frequency seems invalid (check units?)")

        if mod not in {"AUTO", "AM", "FM", "NFM"}:
            raise ValueError("Modulation must be AUTO, AM, FM, or NFM")

        if not (0 <= ctcss <= 231):
            raise ValueError("CTCSS/DCS code must be 0–231")

        if delay not in {-10, -5, 0, 1, 2, 3, 4, 5}:
            raise ValueError("Delay must be one of: -10, -5, 0–5")

        if lockout not in {0, 1}:
            raise ValueError("Lockout must be 0 or 1")

        if priority not in {0, 1}:
            raise ValueError("Priority must be 0 or 1")