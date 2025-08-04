# Scanner Controller

This project provides a cross-platform command line interface (CLI) and graphical user interface (GUI) for controlling various radio scanner models through a unified interface. Built with PyQt6, the GUI allows users to interact with different scanner hardware using a consistent set of controls regardless of the manufacturer's native interface.

## What This Program Does

Scanner Controller bridges the gap between different scanner models by:

1. **Providing a universal interface** for controlling scanners from different manufacturers
2. **Abstracting hardware differences** through model-specific adapters
3. **Enabling remote control** of scanners via a computer interface
4. **Enhancing the user experience** with visual feedback and intuitive controls
5. **Standardizing commands** across different scanner models

The application dynamically detects connected scanner models and loads the appropriate command adapter, making it easy to switch between different scanner hardware.

## Current GUI Features

- **Audio Controls**: Adjust volume and squelch levels using sliders.
- **Display Group**: View scanner information on a simulated LCD display.
- **Signal Meters**: Monitor RSSI and squelch levels in real-time.
- **Control Keys**: Access frequently used scanner functions like "Hold", "Scan", "Menu", etc.
- **Keypad**: Input numeric values and commands using a keypad.
- **Rotary Knob**: Simulate a rotary knob for navigation and selection.
- **Port Detection**: Automatically detect and connect to supported scanner models via serial ports.
- **Scanning Control**: Start or stop scanning directly from the interface and access Close Call operations.
- **Close Call Controls**: Manage Close Call settings and jump commands through adapter helpers.

## Supported Scanner Models

The following scanner models are supported through the `commandLibrary`:

- **BC125AT**: Uniden handheld scanner
- **BCD325P2**: Uniden handheld digital scanner
- **Generic Uniden**: Fallback adapter for other Uniden models. Unknown Uniden
  scanners automatically use this fallback with basic volume and squelch
  control.

The code is designed to work with most Uniden scanners and is abstracted to allow easy porting to other manufacturers.

## System Architecture

The application follows a modular architecture:

```
┌───────────┐     ┌─────────┐     ┌─────────┐     ┌──────────┐
│ GUI / CLI │ <-- │ Scanner │ <-- │ Command │ <-- │ Scanner  │
│ Interface │ --> │ Adapter │ --> │ Library │ --> │ Hardware │
└───────────┘     └─────────┘     └─────────┘     └──────────┘
```

1. **GUI/CLI Layer**: User interface components that capture user input
2. **Scanner Adapters**: Model-specific implementations that convert generic commands to hardware-specific protocols
3. **Command Library**: Translates UI actions into scanner-specific commands

This separation allows new scanner models to be added without modifying the user interface.

## Project Structure

The repository is organized into modules so new scanner models and features can be added easily:

```text
scanner-controller/
├── adapters/            # Scanner model adapters
├── command_libraries/   # Command definitions for each model
├── scanner_gui/         # GUI application
│   ├── gui/             # PyQt widgets
│   └── icons/           # SVG resources
├── utilities/           # Shared utilities and helper scripts
├── tools/               # Miscellaneous scripts
├── dev_tools/           # Development utilities
├── tests/               # Unit tests
├── docs/                # Additional documentation
└── logs/                # Log files (git-ignored)
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Boondock-Echo/scanner-controller.git
cd scanner-controller
```

2. (Recommended) Create and activate a virtual environment:

```bash
# On Unix/macOS
python -m venv .venv
source .venv/bin/activate
# On Windows
python -m venv .venv
.\.venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

To include optional HID support, install the package with the `hid` extra:

```bash
pip install .[hid]
```

To enable optional SDR hardware support, install the package with the `sdr` extra:

```bash
pip install .[sdr]
```

4. Ensure the required scanner models are connected via serial ports.

## SDR Device Setup

Platform-specific drivers are required for RTL-SDR and other SDR hardware.

### Windows

1. Use [Zadig](https://zadig.akeo.ie/) to replace the default driver with **WinUSB**.
2. Plug in the SDR and verify it appears as an *RTL2832U* device.
3. Install optional Python packages with:

   ```bash
   pip install .[sdr]
   ```

### macOS

1. Install drivers via [Homebrew](https://brew.sh/):

   ```bash
   brew install rtl-sdr soapysdr soapyrtlsdr
   ```
2. Install the Python extras with:

   ```bash
   pip install .[sdr]
   ```

### Linux

1. Install drivers and udev rules from your package manager, for example on Debian/Ubuntu:

   ```bash
   sudo apt install rtl-sdr soapysdr-module-rtlsdr
   ```
2. If building from source, copy the provided udev rules and reload:

   ```bash
   sudo cp rtl-sdr.rules /etc/udev/rules.d/99-rtl-sdr.rules
   sudo udevadm control --reload-rules && sudo udevadm trigger
   ```
3. Install the Python extras with:

   ```bash
   pip install .[sdr]
   ```

## Enabling HID Devices on Linux

Some scanners, such as the **Uniden BC125AT**, may appear as HID devices at
`/dev/usb/hiddev*` rather than traditional serial ports.

### One-command Setup

Run the helper script to load the USB serial driver and grant HID access:

```bash
tools/setup_hid.sh
```

Log out and back in, then verify detection with:

```bash
python tools/scanner_diagnostics.py --scan
```

### Option 1: Load USB Serial Driver

Expose the scanner as a serial port by loading the USB serial driver:

```bash
sudo modprobe usbserial vendor=0x1965 product=0x0017
```

A `/dev/ttyUSB*` port should appear. Verify with:

```bash
dmesg | tail
python tools/scanner_diagnostics.py --scan
```

### Option 2: Use Native HID Support

1. Install the optional [`hid`](https://pypi.org/project/hid/) library via the
   `hid` extra:

   ```bash
   pip install .[hid]
   ```

2. Grant your user access to HID devices:

   ```bash
   sudo usermod -aG plugdev $USER
   # log out and back in, or run: su - $USER
   ```

3. Ensure `/dev/usb/hiddev*` paths are accessible. On Linux this may require
   additional drivers, udev rules, or group permissions.

### Verifying Detection

Check kernel messages after plugging in the scanner:

```bash
dmesg | tail
```

Then run the diagnostics tool to list available devices:

```bash
python tools/scanner_diagnostics.py --scan
```

HID paths will be listed alongside serial ports once configured correctly.

After each change, re-run `python tools/scanner_diagnostics.py --scan` to confirm the device is detected.

## Usage

Run the CLI version:

```bash
python main.py
```

Or launch the GUI:

```bash
python -m scanner_gui.main
```

Use the interface to select a serial port and control the scanner.

### Custom Search Command

The CLI provides a `custom search` command to sweep a range of frequencies and
collect RSSI readings:

```bash
custom search <center> <span> <step>
```

* `<center>` – center frequency of the sweep. Values may include a unit
  suffix (e.g. `144M`, `144000k`). Without a suffix, MHz is assumed.
* `<span>` – bandwidth to cover. Supports the same unit notation as
  `<center>`.
* `<step>` – step size between samples. Accepts either kHz or MHz
  notation (e.g. `500k` or `0.5M`). If no unit is specified, the value is
  interpreted as kilohertz.

The command returns pairs of `(frequency, rssi)` values. These readings can be
fed into a future GUI waterfall display for visual analysis of signal activity.

### Band Step Size Defaults

When selecting a preset or band without specifying a step size, the controller
uses conventional values defined in `config/step_size_defaults.py`. A few
examples are shown below:

| Band           | Step (kHz) |
| -------------- | ---------- |
| air            | 833        |
| race           | 1250       |
| marine         | 2500       |
| railroad       | 1500       |
| ham2m          | 2000       |
| ham70cm        | 1250       |
| weather        | 2500       |
| cb             | 1000       |
| frs            | 1250       |
| public_safety  | 1250       |
| mil_air        | 2500       |

### Band Select Command

The `band select` command configures the band scope using either a preset
name or explicit parameters. The shorter alias `band set` behaves the same.

```text
> band select air
> band set 108M 136M 12.5k AM
```

After the `BSP` command is sent during `band select`, the scanner now
automatically enters band-scope search by issuing a scan-start key. It also
programs custom search range 1 using `CSP` and enables only that range with
`CSG,0111111111` so the scope limits match the selected band. The `CSP`
command uses the preset limits in 100‑Hz units (e.g. `01080000` for 108 MHz)
to align with the scanner's expected format.

#### BC125AT Search-Based Sweep

For the BC125AT, appending `search` to the `band scope` command performs a
slower sweep that polls the `PWR` command while the scanner runs a custom
search between the preset limits:

```text
> band scope air search
```

The adapter programs range 1 using `CSP`/`CSG`, starts scanning, and records a
frequency/RSSI pair for each step. This method makes only a single pass across
the band and ignores the sweep-count parameter, so it is best suited for quick
checks rather than long captures.

### Band Scope Streaming

Band scope status can be streamed using the `CSC` command. When activated the
scanner outputs lines of the form `CSC,<RSSI>,<FRQ>,<SQL>` for each hit. The
controller now processes data in **sweeps**. Each sweep gathers
`band_scope_width` records (falling back to 1024 if that width is unknown). The
CLI's `band scope` command takes a preset name followed by an optional sweep
count and mode; providing a number runs that many sweeps. Before streaming, the
total record count is calculated as `band_scope_width * sweeps`. After the final
record the command `CSC,OFF` is issued and the final `CSC,OK` response is read.
In **list** mode (the default) every `(frequency, RSSI)` pair collected during
the sweeps is printed. In **hits** mode the mean RSSI is computed and only
frequencies more than 20% above that mean are displayed. After all readings a
summary line describes the sweep parameters:

```text
145.0000, 0.000
146.5200, 0.450
147.0400, 0.610
center=146.000 min=145.000 max=147.000 span=2M step=0.5M mod=FM
```

The related `band sweep` command streams the raw values directly. Each line
printed contains the frequency in megahertz and the normalized RSSI level:

```text
<freq_mhz>, <rssi/1023.0>
```

For example: `162.5500, 0.450`. This format is consistent in both human and
machine modes and is convenient for logging or further processing. Use the
optional mode argument to control output: `list` displays all values while
`hits` shows only entries 20% above the mean RSSI level:

```text
> band scope <preset> [sweeps] [list|hits]
> band scope <preset> cc search
> band scope <preset> cc log
```

The `cc search` subcommand performs a Close Call search within the chosen
band and prints any hit frequencies after the search ends. Press **Enter** or
`q` at any time to terminate the search and restore the scanner's previous
settings. The `cc log` variant starts continuous logging of hits until
interrupted.

### Close Call Logging

The utility function `record_close_calls` allows continuous logging of Close Call
hits to an SQLite database. Use the CLI command `band scope <preset> cc log` or
the legacy commands `log close calls` / `log close calls lockout` and provide a
band name such as `air` or `frs`. Each hit is saved with timestamp, frequency,
tone (if available) and RSSI level. When the `lockout` variant is used the
frequency is also added to the scanner's temporary lockout list via the `LOF`
command.

The logger normally runs indefinitely. To capture a limited number of hits or
stop after a set time, pass ``max_records`` or ``max_time`` to
``record_close_calls``:

```python
from utilities.scanner.close_call_logger import record_close_calls
record_close_calls(adapter, ser, "air", max_time=10)
```

### Using Multiple Scanners

The controller can maintain more than one active connection. The CLI now
supports a small set of connection management commands:

- `list` – show all open connections with the active one marked by `*`.
- `scan` – list detected scanners.
- `connect <id>` – connect to the scanner with the given ID (see `scan`).
- `use <id>` – make the specified connection active for subsequent commands.
- `close <id>` – disconnect and remove a connection from the list.

The older `switch` command is still accepted for scripts that relied on it, but
it closes the current connection before opening a new one. Using the new
commands keeps other scanners online and allows quick switching between them.

In the GUI, selecting a port while already connected spawns an additional window
so multiple scanners can be controlled side by side.

Below is a short example showing band-scope streaming from two scanners:

```text
$ python main.py
> scan
  1. /dev/ttyUSB0 — BCD325P2
  2. /dev/ttyUSB1 — BC125AT
> connect 1
Connected to /dev/ttyUSB0 [ID 1]
> connect 2
Connected to /dev/ttyUSB1 [ID 2]
> list
[1]* /dev/ttyUSB0
[2]  /dev/ttyUSB1
> use 1
Using connection 1
> band scope 20 hits
(hits for scanner 1)
center=...
> use 2
Using connection 2
> band scope 20 hits
(hits for scanner 2)
center=...
```

## Extending the System

To support a new scanner model:

1. Create a new adapter class in the `adapters/` directory.
2. Implement initialization, command processing, and cleanup logic.
3. Register the adapter in the model detection code.

Example adapter skeleton:

```python
class NewScannerAdapter(BaseAdapter):
    def __init__(self, port: str):
        self.port = port
        self.connection = None

    def initialize(self) -> None:
        """Establish connection with the scanner."""
        # Initialize serial connection

    def process_command(self, command: str, *args) -> None:
        """Convert generic commands to scanner-specific commands."""
        if command == "SET_VOLUME":
            ...  # send volume command
        elif command == "SET_SQUELCH":
            ...  # send squelch command

    def read_response(self) -> str:
        """Read and interpret scanner responses."""
        # Read from serial connection

    def cleanup(self) -> None:
        """Close the connection and clean up resources."""
        # Close connection
```

## Development Workflow

Install development tools and pre-commit hooks:

```bash
pip install -r requirements-dev.txt
pre-commit install
```

### Code Style and Quality

Formatting and linting are enforced with **Black** and **Flake8**. Run them before committing:

```bash
black .
flake8
```

### Maintenance Scripts

Useful scripts are located in `tools/` and `dev_tools/`:

```bash
python tools/clear_pycache.py
python -m dev_tools.analyze_unused_files
```

### Running Tests

1. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows use .venv\Scripts\activate
```

2. Install development dependencies:

```bash
pip install -r requirements-dev.txt
```

3. Run the test suite:

```bash
pytest
```

4. Optionally run lint checks using the following commands:

```bash
black . --check
flake8
isort . --check
```

## Debugging Communication

Enable verbose logging to troubleshoot serial issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

You can also monitor serial traffic:

```bash
python -m scanner_gui.main --monitor-serial
```

## Common Issues and Troubleshooting

| Issue                       | Possible Solution                                  |
| --------------------------- | -------------------------------------------------- |
| Scanner not detected        | Verify cables and serial drivers                   |
| Commands not working        | Check firmware and command syntax                  |
| GUI elements not responding | Restart the application and ensure PyQt is updated |

## Contributing

1. Fork the repository.
2. Create a branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
