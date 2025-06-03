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

## Supported Scanner Models

The following scanner models are supported through the `commandLibrary`:

- **BC125AT**: Uniden handheld scanner
- **BCD325P2**: Uniden handheld digital scanner

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

<<<<<<< HEAD
The project follows a modular organization to separate concerns and support extensibility:

```
scanner-controller/
│
├── scanner_gui/                  # Main application package
│   ├── gui/                      # GUI components
│   │   ├── audioControls.py      # Audio controls (volume, squelch)
│   │   ├── controlKeys.py        # Control keys (Hold, Scan, etc.)
│   │   ├── displayGroup.py       # LCD display simulation
│   │   ├── keypad.py             # Numeric keypad
│   │   ├── rotaryKnob.py         # Rotary knob simulation
│   │   ├── signalMeters.py       # Signal meters (RSSI, SQL)
│   │   ├── scanner_gui.py        # Main GUI implementation
│   │   ├── style.qss             # Stylesheet for the GUI
│   │   └── __init__.py
│   ├── commandLibrary.py         # Scanner command interface
│   ├── scannerUtils.py           # Utility functions for serial communication
│   ├── main.py                   # Entry point for the application
│   └── __init__.py
│
├── adapters/                     # Scanner model-specific adapters
│   ├── uniden/                   # Uniden scanner adapters
│   │   ├── bc125at.py            # BC125AT adapter implementation
│   │   ├── bcd325p2.py           # BCD325P2 adapter implementation
│   │   └── sds_adapter.py        # SDS100/SDS200 adapter implementation
│   ├── aor/                      # AOR scanner adapters
│   │   └── dv1.py                # AR-DV1 adapter implementation
│   └── __init__.py
│
├── icons/                        # SVG icons for the GUI
│   ├── rotary-knob.svg           # Rotary knob icon
│   ├── arrow-left.svg            # Left arrow navigation icon
│   └── arrow-right.svg           # Right arrow navigation icon
│
├── dev_tools/                    # Utility scripts for development
│   ├── analyze_unused_files.py   # Find unused Python files
│   ├── analyze_unused_imports.py # Detect unused imports
│   ├── build_dependency_graph.py # Build module dependency graph
│   └── cleanup_legacy.py         # Identify legacy module imports
│
├── scripts/                      # Helper scripts
│   └── clear_pycache.py          # Script to clear __pycache__ directories
│
├── tests/                        # Unit and integration tests
│   ├── test_adapters/            # Tests for scanner adapters
│   └── test_gui/                 # Tests for GUI components
│
├── docs/                         # Documentation
│   └── api/                      # API documentation
│
├── requirements.txt              # Project dependencies
├── requirements-dev.txt          # Development dependencies
├── setup.py                      # Package installation script
├── LICENSE                       # License information
└── README.md                     # Project documentation
```
=======
```
scanner-controller/
│
├── scanner_gui/
│   ├── gui/
│   │   ├── audio_controls.py       # Audio controls (volume, squelch)
│   │   ├── control_keys.py         # Control keys (Hold, Scan, etc.)
│   │   ├── display_group.py        # LCD display simulation
│   │   ├── keypad.py               # Numeric keypad
│   │   ├── rotary_knob.py          # Rotary knob simulation
│   │   ├── scanner_gui.py          # Main GUI implementation
│   │   ├── signal_meters.py        # Signal meters (RSSI, SQL)
│   │   ├── style.qss               # Stylesheet for the GUI
│   │   └── __init__.py
│   ├── icons/
│   │   ├── rotary-knob.svg
│   │   ├── arrow-left.svg
│   │   └── arrow-right.svg
│   ├── controller.py
│   ├── main.py                     # Entry point for the application
│   ├── scanner_utils.py            # Utility functions for serial communication
│   └── __init__.py
│
├── adapters/                       # Scanner model-specific adapters
│   ├── base_adapter.py
│   ├── uniden/
│   │   ├── bc125at_adapter.py      # BC125AT adapter implementation
│   │   ├── bcd325p2_adapter.py     # BCD325P2 adapter implementation
│   │   ├── uniden_base_adapter.py  # Base class for Uniden adapters
│   │   ├── common/
│   │   │   ├── core.py
│   │   │   ├── programming.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── __pycache__/
│
├── utilities/                      # Utility scripts for development
│   ├── command_library.py
│   ├── command_loop.py
│   ├── command_parser.py
│   ├── command_registry.py
│   ├── core.py
│   ├── help_topics.py
│   ├── help_utils.py
│   ├── log_utils.py
│   ├── readline_setup.py
│   ├── scanner_factory.py
│   ├── scanner_manager.py
│   ├── scanner_utils.py
│   ├── scanner_utils_uniden.py
│   ├── serial_utils.py
│   ├── shared_utils.py
│   ├── timeout_utils.py
│   ├── validators.py
│   ├── tools/
│   │   ├── analyze_unused_files.py
│   │   ├── analyze_unused_imports.py
│   │   ├── build_dependency_graph.py
│   │   ├── clear_pycache.py
│   │   └── log_trim.py
│   ├── research/
│   │   ├── commands.txt
│   │   ├── commands_progress.txt
│   │   └── uniden_command_finder.py
│   └── __init__.py
│
├── command_libraries/              # Command libraries for scanner models
│   ├── base_command.py
│   ├── uniden/
│   │   ├── bc125at_commands.py
│   │   ├── bcd325p2_commands.py
│   │   ├── uniden_tone_lut.py
│   │   └── __init__.py
│   └── __init__.py
│
├── tools/                          # Miscellaneous tools
│   ├── debug_volume_control.py
│   ├── scanner_diagnostics.py
│   └── volume_range_test.py
│
├── tests/
│   └── test_example.py
│
├── docs/
│   ├── project_structure.md
│   └── manuals/
│       ├── AR-DV1_COMMAND_LIST.pdf
│       ├── BC125AT_Protocol.pdf
│       ├── BCD325P2_Remote_Protocol_ver_1_02.pdf
│       └── SDS100om.pdf
│
├── main.py
├── run_scanner_gui.py
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── setup.cfg
├── setup_instructions.md
└── LICENSE
```

## Installation # Project documentation
>>>>>>> origin/main

This structure separates the core application logic from hardware-specific adapters and provides tools for development and testing. The modular design allows for easy extension with new scanner models and GUI components.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Boondock-Echo/scanner-controller.git
cd scanner-controller
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure the required scanner models are connected via serial ports.

## Usage

1. Run the application:

## Usage

For CLI

```bash
python main.py
```

For GUI

```bash
python -m scanner_gui.main
```

2. Use the GUI to interact with your scanner:

- Select the scanner port from the dropdown and click "Connect".
- Use the sliders, buttons, and keypad to control the scanner.
- View real-time updates on the display and signal meters.

### Adding New Scanner Models

## Extending the System

To add support for a new scanner model:

### Adding New Scanner Models

1. **Create a new adapter class** in the appropriate manufacturer folder under `adapters/`
2. **Implement the required methods**::

- `initialize()`: Set up the connection with the scanner
- `process_command(command, *args)`: Process generic commandsr folder under `adapters/`
- `read_response()`: Read and interpret scanner responses
- `cleanup()`: Handle proper disconnectionth the scanner
- `process_command(command, *args)`: Process generic commands
  Example adapter structure:ad and interpret scanner responses
- `cleanup()`: Handle proper disconnection

<<<<<<< HEAD
`````python
=======
````python
>>>>>>> origin/main
class NewScannerAdapter:e:
 def __init__(self, port):
     self.port = port
     self.connection = None
 def __init__(self, port):
 def initialize(self):
     """Establish connection with the scanner"""
     # Initialize serial connection
 def initialize(self):
 def process_command(self, command, *args):er"""
     """Convert generic commands to scanner-specific commands"""
     if command == "SET_VOLUME":
         # Convert to scanner-specific volume command
     elif command == "SET_SQUELCH": scanner-specific commands"""
         # Convert to scanner-specific squelch command
     # etc.Convert to scanner-specific volume command
     elif command == "SET_SQUELCH":
 def read_response(self):nner-specific squelch command
     """Read and interpret scanner responses"""
     # Read from serial connection
     # Interpret the response
     """Read and interpret scanner responses"""
 def cleanup(self):rial connection
     """Clean up resources"""
     # Close the connection
``` def cleanup(self):
     """Clean up resources"""
3. **Register the adapter** in the `commandLibrary.py` file:
````python
def detect_scanner_model(port):the `commandLibrary.py` file:
    # Add your model detection logic
    if some_condition:
        return NewScannerAdapter(port)
``` # Add your model detection logic
    if some_condition:
### Adding New GUI Componentster(port)
`````

To add a new GUI component:

### Adding New GUI Components

1. Create a new file in the `gui/` directory
2. Define a class that extends `QWidget` or another appropriate Qt class
3. Implement the UI and functionality
4. Connect signals and slots to handle events
5. Update `scanner_gui.py` to integrate the new componentpriate Qt class
6. Implement the UI and functionality

## Development Workflow to handle events

5. Update `scanner_gui.py` to integrate the new component

### Setting Up the Development Environment

## Development Workflow

1. Install development dependencies:

### Setting Up the Development Environment

```bash
pip install -r requirements-dev.txt
```

```bash
2. Install pre-commit hooks:ts-dev.txt
```

```bash
pre-commit install hooks:
```

### Code Style and Quality

This project uses:

- Black for code formatting
- Flake8 for code linting with several plugins

The configurations ensure these tools work together without conflicts:

- Flake8 is configured to be compatible with Black's formatting decisions

### Fixing Code Style Issues

1. **Black** (formatter) will automatically fix formatting issues when possible
2. **Flake8** (linter) will report issues but won't fix them automatically

To fix issues:formatter) will automatically fix formatting issues when possible 2. **Flake8** (linter) will report issues but won't fix them automatically

````bash
# First, run Black to auto-format all files
black .
```bash
# Then run Flake8 to see remaining issueses
```bash
flake8.
````

# Fix the remaining issues manually, then commit again

````

### Common Issues

- Missing docstrings (D1xx errors)
- Import ordering (I1xx errors)
- Unused imports or variables (F4xx errors)
- Complexity issues (C9xx errors))
- Import ordering (I1xx errors)

### Maintenance Scripts Labels (F4xx errors)

- Complexity issues (C9xx errors)

### Maintenance Scripts

```bash
python scripts/clear_pycache.pyctories:
````

```bash
To analyze unused files or imports, or to build a dependency graph:
```

```bash
python -m dev_tools.analyze_unused_file
```

to build a dependency graph:

```bash
python -m dev_tools.analyze_unused_imports
python -m dev_tools.build_dependency_graph
python dev_tools/analyze_unused_files.py
python dev_tools/analyze_unused_imports.py
```

To identify legacy code patterns or migrate adapter code:endency_graph.py

````bash
python -m dev_tools.cleanup_legacy --report-file legacy_report.txt## Debugging Communication
python -m dev_tools.migrate_legacy_adapters --dry-run
```To debug scanner communication issues:

## Debugging Communication logging:

To debug scanner communication issues:python
   import logging
1. Enable verbose logging:EBUG)
```python
import logging
logging.basicConfig(level=logging.DEBUG)
````

2. Use the built-in serial monitoring:
   Check the log file (created in the app's directory) for communication traces.

```bash3.
python -m scanner_gui.main --monitor-serial
```

3. Check the log file (created in the app's directory) for communication traces.

## Common Issues and Troubleshooting

| Issue | Possible Solution || GUI elements not responding | Restart the application; check Python and PyQt6 versions |
| --------------------------- | ---------------------------------------------------------------------------------------- |ication errors | Verify cable connections; try a different USB port |
| Scanner not detected | Make sure serial drivers are installed and the port is not in use by another application || Slow response time | Adjust the serial timeout settings in scannerUtils.py |
| Commands not working | Check if your scanner firmware is up to date |
| GUI elements not responding | Restart the application; check Python and PyQt6 versions |## Contributing
| Serial communication errors | Verify cable connections; try a different USB port |
| Slow response time | Adjust the serial timeout settings in scannerUtils.py |ps:

## Contributing1. Fork the repository.

a new branch for your feature or bugfix.
Contributions are welcome! Please follow these steps:3. Submit a pull request with a detailed description of your changes.

1. Fork the repository.## License

This project is licensed under the MIT License. See the `LICENSE` file for details.## License3. Submit a pull request with a detailed description of your changes.2. Create a new branch for your feature or bugfix.
This project is licensed under the MIT License. See the `LICENSE` file for details.
