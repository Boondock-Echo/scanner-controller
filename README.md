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

4. Ensure the required scanner models are connected via serial ports.

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

### Band Sweep Command

The CLI also provides a `band sweep` command to scan a range of frequencies and
collect RSSI readings:

```bash
band sweep <center> <span> <step>
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

### Custom Search Stream

For Uniden models that support the `CSC` command (e.g. BCD325P2), the CLI
exposes a `custom search` command which streams search results directly from the
scanner:

```bash
custom search [max_results]
```

`max_results` controls how many `CSC` lines are collected before the command
stops.  If omitted, the default is 50 samples.

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
