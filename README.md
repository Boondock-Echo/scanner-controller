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

The repository organizes application code, utilities and tests in dedicated directories:

```text
scanner-controller/
├── scanner_gui/          # PyQt6 GUI application
├── adapters/             # Hardware adapters for supported scanners
├── command_libraries/    # Command definitions per model
├── utilities/            # Shared utilities and tools
├── tools/                # Miscellaneous helper scripts
├── docs/                 # Additional documentation
├── tests/                # Unit tests
├── pyproject.toml        # Build and packaging configuration
├── requirements.txt      # Application dependencies
└── requirements-dev.txt  # Development dependencies
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Boondock-Echo/scanner-controller.git
cd scanner-controller
```

2. Install the project using the `pyproject.toml`:

```bash
# install locally with pip
pip install .

# or install in an isolated environment
pipx install .
```

3. Ensure the required scanner models are connected via serial ports.

## Usage

### Command-line interface

```bash
python main.py
```

### Graphical interface

```bash
python -m scanner_gui.main
```

## Extending the System

To add support for a new scanner model, create a new adapter in `adapters/<manufacturer>/` and implement the required methods. New GUI components can be added under `scanner_gui/gui/` and integrated into the main window.

## Development Workflow

1. Install development dependencies:

```bash
pip install -r requirements-dev.txt
pre-commit install
```

2. Run tests with `pytest`.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
