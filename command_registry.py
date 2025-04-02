from scanner_adapters.scanner_utils import send_command

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
        "read battery": lambda: adapter.readBatteryVoltage(ser),
        "read window": lambda: adapter.readWindowVoltage(ser),
        "read status": lambda: adapter.readStatus(ser),

        # Device Info
        "read model": lambda: adapter.readModel(ser),
        "read version": lambda: adapter.readSWVer(ser),

        # Key Simulation
        "send key": lambda arg: adapter.sendKey(ser, arg),

        # Raw Command
        "send": lambda arg: adapter.send_command(ser, arg),

        # Frequency Hold
        "hold frequency": lambda arg: adapter.enter_quick_frequency_hold(ser, float(arg)),

        # Dump Memory to File
        "dump memory": lambda: adapter.dumpMemoryToFile(ser),

        # Read Global Lockouts
        "read lockout": lambda: adapter.readGlobalLockout(ser),

        # Channel I/O
        "read channel": lambda arg: adapter.readChannelInfo(ser, int(arg)),
        "write channel": lambda arg: (
            lambda args: adapter.writeChannelInfo(
                ser,
                int(args[0]),  # index
                args[1],       # name
                int(args[2]),  # freq_khz
                args[3],       # mod
                int(args[4]),  # ctcss
                int(args[5]),  # delay
                int(args[6]),  # lockout
                int(args[7])   # priority
            )
        )(arg.split(",")),

        # Help gets added in main.py after this table is built
    }

    COMMAND_HELP = {
        "read volume": "Reads the current volume level.",
        "write volume": "Sets volume level (0-1.0). Usage: write volume 0.75",
        "read squelch": "Reads the squelch level.",
        "write squelch": "Sets squelch (0-1.0). Usage: write squelch 0.5",
        "read frequency": "Reads the currently tuned frequency (if supported).",
        "write frequency": "Sets the frequency (MHz). Usage: write frequency 162.550",
        "read rssi": "Reads the signal strength (RSSI).",
        "read smeter": "Reads the S-meter value.",
        "read battery": "Returns the battery voltage (V).",
        "read window": "Returns the window voltage and frequency.",
        "read status": "Returns full scanner display state and flags.",
        "read model": "Returns the scanner model.",
        "read version": "Returns the firmware version.",
        "send key": "Simulates keypad input. Usage: send key 123E",
        "send": "Sends a raw command. Usage: send PWR",
        "hold frequency": "Enters a frequency hold mode. Usage: hold frequency 851.0125",
        "dump memory": "Reads all memory entries via CIN and saves to file.",
        "read lockout": "Lists global lockout frequencies.",
        "read channel": "Reads a channel by index. Usage: read channel 5",
        "write channel": (
            "Writes channel info. Usage: write channel index,name,freq_khz,mod,ctcss,delay,lockout,priority\n"
            "Example: write channel 5,CH5,4625625,FM,100,2,0,1"
        ) 
    }
    return COMMANDS, COMMAND_HELP
"""
This implementation is causing the program to crash.  Removed for now.
    COMMANDS["write"].__doc__ = "volume, squelch, frequency",
    COMMANDS["read"].__doc__ = "volume, squelch, frequency, rssi, smeter, battery, window, status, model, version",
    COMMANDS["set"].__doc__ = "volume, squelch, frequency",
    COMMANDS["get"].__doc__ = "volume, squelch, frequency, rssi, smeter, battery, window, status, model, version",
    COMMANDS["send"].__doc__ = "key, command",
    COMMANDS["hold"].__doc__ = "frequency",
    COMMANDS["dump"].__doc__ = "memory",   
"""
