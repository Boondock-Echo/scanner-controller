"""
Command registry module.

Provides functionality for building command tables. These commands are used to
interact with the scanner adapter and perform various operations.
This module is designed to be used with a scanner adapter and a serial
connection object.
"""


def build_command_table(adapter, ser):
    """
    Build command table for the specified adapter.

    Args:
        adapter: Scanner adapter instance
        ser: Serial connection object

    Returns:
        Dictionary mapping command names to handler functions
    """
    # Primary commands use get/set
    COMMANDS = {
        # Volume
        "get volume": lambda: adapter.read_volume(ser),
        "set volume": lambda arg: adapter.write_volume(ser, float(arg)),
        # Squelch
        "get squelch": lambda: adapter.read_squelch(ser),
        "set squelch": lambda arg: adapter.write_squelch(ser, float(arg)),
        # Frequency
        "get frequency": lambda: adapter.read_frequency(ser),
        "set frequency": lambda arg: adapter.write_frequency(ser, float(arg)),
        # Status
        "get rssi": lambda: adapter.read_rssi(ser),
        "get smeter": lambda: adapter.read_smeter(ser),
        "get battery": lambda: adapter.readBatteryVoltage(ser),
        "get window": lambda: adapter.readWindowVoltage(ser),
        "get status": lambda: adapter.readStatus(ser),
        # Device Info
        "get model": lambda: adapter.read_model(ser),
        "get version": lambda: adapter.read_swver(ser),
        # Key Simulation
        "send key": lambda arg: adapter.sendKey(ser, arg),
        # Raw Command
        "send": lambda arg: adapter.send_command(ser, arg),
        # Frequency Hold
        "hold frequency": lambda arg: adapter.enter_quick_frequency_hold(
            ser, float(arg)
        ),
        # Dump Memory to File
        "dump memory": lambda: adapter.dumpMemoryToFile(ser),
        # Read Global Lockouts
        "get lockout": lambda: adapter.readGlobalLockout(ser),
        # Channel I/O
        "get channel": lambda arg: adapter.readChannelInfo(ser, int(arg)),
        "set channel": lambda arg: (
            lambda args: adapter.writeChannelInfo(
                ser,
                int(args[0]),  # index
                args[1],  # name
                int(args[2]),  # freq_khz
                args[3],  # mod
                int(args[4]),  # ctcss
                int(args[5]),  # delay
                int(args[6]),  # lockout
                int(args[7]),  # priority
            )
        )(arg.split(",")),
        # Help gets added in main.py after this table is built
    }

    # Add backwards compatibility aliases for read/write
    for cmd, handler in list(COMMANDS.items()):
        if cmd.startswith("get "):
            COMMANDS["read " + cmd[4:]] = handler
        elif cmd.startswith("set "):
            COMMANDS["write " + cmd[4:]] = handler

    COMMAND_HELP = {
        "get volume": "Reads the current Volume level.",
        "set volume": "Sets volume level (0-1.0). Usage: set volume 0.75",
        "get squelch": "Reads the squelch level.",
        "set squelch": "Sets squelch (0-1.0). Usage: set squelch 0.5",
        "get frequency": (
            "Reads the currently tuned frequency (if supported)."
            "Usage: get frequency"
            " (e.g., 162.550)"
        ),
        "set frequency": (
            "Sets the frequency (MHz). Usage: set frequency " "162.550"
        ),
        "get rssi": "Reads the signal strength (RSSI).",
        "get smeter": "Reads the S-meter value.",
        "get battery": "Returns the battery voltage (V).",
        "get window": "Returns the window voltage and frequency.",
        "get status": "Returns full scanner display state and flags.",
        "get model": "Returns the scanner model.",
        "get version": "Returns the firmware version.",
        "send key": "Simulates keypad input. Usage: send key 123E",
        "send": "Sends a raw command. Usage: send PWR",
        "hold frequency": (
            "Enters a frequency hold mode. Usage: hold frequency " "851.0125"
        ),
        "dump memory": "Reads all memory entries via CIN and saves to file.",
        "get lockout": "Lists global lockout frequencies.",
        "get channel": "Reads a channel by index. Usage: get channel 5",
        "set channel": (
            "Writes channel info. Usage: set channel "
            "index,name,freq_khz,mod,ctcss,delay,lockout,priority\n"
            "Example: set channel 5,CH5,4625625,FM,100,2,0,1"
        ),
    }

    # Add backwards compatibility help entries
    for cmd, help_text in list(COMMAND_HELP.items()):
        if cmd.startswith("get "):
            COMMAND_HELP["read " + cmd[4:]] = (
                help_text + "\n(Alias: " + cmd + ")"
            )
        elif cmd.startswith("set "):
            COMMAND_HELP["write " + cmd[4:]] = (
                help_text + "\n(Alias: " + cmd + ")"
            )

    return COMMANDS, COMMAND_HELP
