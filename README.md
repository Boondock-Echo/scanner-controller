# Scanner Controller

This project provides a cross-platform graphical user interface (GUI) for controlling various radio scanner models through a unified interface. Built with PyQt6, it enables users to interact with different scanner hardware using a consistent set of controls regardless of the manufacturer's native interface.

## What This Program Does

Scanner Controller bridges the gap between different scanner models by:

1. **Providing a universal interface** for controlling scanners from different manufacturers
2. **Abstracting hardware differences** through model-specific adapters
3. **Enabling remote control** of scanners via a computer interface
4. **Enhancing the user experience** with visual feedback and intuitive controls
5. **Standardizing commands** across different scanner models

The application dynamically detects connected scanner models and loads the appropriate command adapter, making it easy to switch between different scanner hardware.

## Features

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

````
┌───────────┐     ┌─────────┐     ┌──────────┐
│ GUI / CLI │ <-- │ Scanner │ <-- │ Scanner  │
│ Interface │ --> │ Adapter │ --> │ Hardware │
└───────────┘     └─────────┘     └──────────┘
                     ↑ |
                     | ↓
                  ┌─────────┐
                  │ Command │
                  │ Library │
                  └─────────┘


      ```

1. **GUI/CLI Layer**: User interface components that capture user input
2. **Scanner Adapters**: Model-specific implementations that convert generic commands to hardware-specific protocols
3. **Command Library**: Translates UI actions into scanner-specific commands


This separation allows new scanner models to be added without modifying the user interface.

## Project Structure

The project is organized as follows:

````

scanner-controller/
│
├── scanner_gui/
│ ├── gui/
│ │ ├── audioControls.py # Audio controls (volume, squelch)
│ │ ├── controlKeys.py # Control keys (Hold, Scan, etc.)
│ │ ├── displayGroup.py # LCD display simulation
│ │ ├── keypad.py # Numeric keypad
│ │ ├── rotaryKnob.py # Rotary knob simulation
│ │ ├── signalMeters.py # Signal meters (RSSI, SQL)
│ │ ├── scanner_gui.py # Main GUI implementation
│ │ ├── style.qss # Stylesheet for the GUI
│ │ └── **init**.py
│ ├── commandLibrary.py # Scanner command interface
│ ├── scannerUtils.py # Utility functions for serial communication
│ ├── main.py # Entry point for the application
│ └── **init**.py
│
├── adapters/ # Scanner model-specific adapters
│ ├── uniden/ # Uniden scanner adapters
│ │ ├── bc125at.py # BC125AT adapter implementation
│ │ ├── bcd325p2.py # BCD325P2 adapter implementation
│ │ └── sds_adapter.py # SDS100/SDS200 adapter implementation
│ ├── aor/ # AOR scanner adapters
│ │ └── dv1.py # AR-DV1 adapter implementation
│ └── **init**.py
│
├── icons/ # SVG icons for the GUI
│ ├── rotary-knob.svg
│ ├── arrow-left.svg
│ └── arrow-right.svg
│
├── utilities/ # Utility scripts for development
│ ├── analyze_unused_files.py # Find completely unused Python files
│ ├── analyze_unused_imports.py # Detect unused imports in Python files
│ ├── build_dependency_graph.py # Build module dependency graph
│ └── cleanup_legacy.py # Identify usages of legacy module imports
├── scripts/ # Helper scriptsr adapters to new structure
│ └── clear_pycache.py # Script to clear **pycache** directories
│
├── requirements.txt # Project dependencies
├── requirements-dev.txt # Development dependenciese\_\_ directories
└── README.md # Project documentation

```requirements.txt # Project dependencies
├── requirements-dev.txt           # Development dependencies
## Installation                    # Project documentation
```

1. Clone the repository:

## Installation

````bash
git clone https://github.com/yourusername/scanner-controller.git
cd scanner-controller
```bash
git clone https://github.com/yourusername/scanner-controller.git
2. Install dependencies:
````

```bash
pip install -r requirements.txt
```

```bash
3. Ensure the required scanner models are connected via serial ports.
```

## Usage

3. Ensure the required scanner models are connected via serial ports.
1. Run the application:

## Usage

```bash
python -m scanner_gui.main
```

````bash
2. Use the GUI to interact with your scanner:
- Select the scanner port from the dropdown and click "Connect".
- Use the sliders, buttons, and keypad to control the scanner.
- View real-time updates on the display and signal meters.
- Select the scanner port from the dropdown and click "Connect".
## Extending the Systemuttons, and keypad to control the scanner.
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
```python
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
````

````python
def detect_scanner_model(port):the `commandLibrary.py` file:
    # Add your model detection logic
    if some_condition:
        return NewScannerAdapter(port)
``` # Add your model detection logic
    if some_condition:
### Adding New GUI Componentster(port)
````

To add a new GUI component:

### Adding New GUI Components

1. Create a new file in the `gui/` directory
2. Define a class that extends `QWidget` or another appropriate Qt class
3. Implement the UI and functionality
4. Connect signals and slots to handle events
5. Update `scanner_gui.py` to integrate the new componentpriate Qt class
6. Implement the UI and functionality

## Development Workflowslots to handle events

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

```bash
### Code Style and Quality
```

This project uses:

### Code Style and Quality

- Black for code formatting
- Flake8 for code linting with several plugins

The configurations ensure these tools work together without conflicts:

- Flake8 for code linting with several plugins
- Black formats code with a line length of 88 characters
- Flake8 is configured to be compatible with Black's formatting decisions

### Fixing Code Style Issuesline length of 88 characters

- Flake8 is configured to be compatible with Black's formatting decisions
  When pre-commit shows errors:

### Fixing Code Style Issues

1. **Black** (formatter) will automatically fix formatting issues when possible
2. **Flake8** (linter) will report issues but won't fix them automatically

To fix issues:formatter) will automatically fix formatting issues when possible 2. **Flake8** (linter) will report issues but won't fix them automatically

````bash
# First, run Black to auto-format all files
black .
```bash
# Then run Flake8 to see remaining issueses
flake8.

# Fix the remaining issues manually, then commit again
```ke8

Common Flake8 issues include:nually, then commit again
````

- Missing docstrings (D1xx errors)
- Import ordering (I1xx errors)
- Unused imports or variables (F4xx errors)
- Complexity issues (C9xx errors))
- Import ordering (I1xx errors)

### Maintenance Scriptsiables (F4xx errors)

- Complexity issues (C9xx errors)
  To clear all `__pycache__` directories:

### Maintenance Scripts

```bash
python scripts/clear_pycache.pyctories:
```

```bash
To analyze unused files or imports, or to build a dependency graph:
```

````bash
python -m dev_tools.analyze_unused_fileso build a dependency graph:
python -m dev_tools.analyze_unused_imports
python -m dev_tools.build_dependency_graph
```hon dev_tools/analyze_unused_files.py
python dev_tools/analyze_unused_imports.py
To identify legacy code patterns or migrate adapter code:endency_graph.py
````

````bash
python -m dev_tools.cleanup_legacy --report-file legacy_report.txt## Debugging Communication
python -m dev_tools.migrate_legacy_adapters --dry-run
```To debug scanner communication issues:

## Debugging Communication logging:

To debug scanner communication issues:python
   import logging
1. Enable verbose logging:EBUG)
````

````python
import logging
logging.basicConfig(level=logging.DEBUG)
```   ```bash

2. Use the built-in serial monitoring:   ```

```bash3. Check the log file (created in the app's directory) for communication traces.
python -m scanner_gui.main --monitor-serial
````

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
