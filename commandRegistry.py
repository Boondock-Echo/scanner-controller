from scannerUtils import send_command

def build_command_table(adapter, ser):
    """
    Builds the command-to-function dispatcher and help descriptions.

    Parameters:
        adapter: The scanner adapter instance (e.g., BC125ATAdapter)
        ser: An open serial.Serial connection to the scanner

    Returns:
        (COMMANDS, COMMAND_HELP): Tuple of dictionaries:
            - COMMANDS maps command strings to functions
            - COMMAND_HELP maps command strings to help descriptions
    """

    COMMANDS = {
        # Volume
        "read volume": lambda: adapter.readVolume(ser),
        "write volume": lambda arg: adapter.writeVolume(ser, float(arg)),

        # Squelch
        "read squelch": lambda: adapter.readSquelch(ser),
        "write squelch": lambda arg: adapter.writeSquelch(ser, float(arg)),

        # Frequency
        "read frequency": lambda: adapter.readFrequency(ser),
        "write frequency": lambda arg: adapter.writeFrequency(ser, float(arg)),

        # Status
        "read rssi": lambda: adapter.readRSSI(ser),
        "read smeter": lambda: adapter.readSMeter(ser),

        # Device Info
        "read model": lambda: adapter.readModel(ser),
        "read version": lambda: adapter.readSWVer(ser),

        # Key Simulation
        "send key": lambda arg: adapter.sendKey(ser, arg),

        # Raw Command
        "send": lambda arg: send_command(ser, arg),
        
        # Frequency Hold
        "hold frequency": lambda arg: adapter.enterFrequencyHold(ser, float(arg)),

        # Dump Memory to File        
        "dump memory": lambda: adapter.dumpMemoryToFile(ser),

        # 'help' is injected later in main.py
    }

    COMMAND_HELP = {
        # Volume
        "read volume": "Reads the current volume level from the scanner.",
        "write volume": "Sets the volume level. Usage: write volume <0–15>",

        # Squelch
        "read squelch": "Reads the current squelch level.",
        "write squelch": "Sets the squelch level. Usage: write squelch <0–15>",

        # Frequency
        "read frequency": "Reads the current tuned frequency.",
        "write frequency": "Sets the frequency (MHz). Usage: write frequency <freq>",

        # Status
        "read rssi": "Reads signal strength (RSSI).",
        "read smeter": "Reads the S-meter value.",

        # Info
        "read model": "Returns the scanner model (e.g., BC125AT).",
        "read version": "Returns the firmware version.",

        # Key simulation
        "send key": "Simulates a keypress. Usage: send key <sequence>",

        # Raw command access
        "send": "Sends a raw serial command to the scanner. Usage: send <COMMAND>",

        # Dump Memory
        "dump memory": "Reads all data and sends it to a .txt file.",
  
        # Help
        "help": "Lists all available commands, or use 'help <command>' for details.",
    }

    return COMMANDS, COMMAND_HELP
