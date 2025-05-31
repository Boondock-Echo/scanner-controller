# Scanner Controller

A Python-based application for controlling and interacting with radio scanners from various manufacturers.

## Overview

This project provides a comprehensive toolkit for controlling radio scanners via serial interfaces. It offers both a command-line interface and a graphical user interface for interacting with supported scanner models.

## Features

- Serial communication with scanner devices
- Support for multiple scanner models (Uniden BC125AT, BCD325P2)
- Command-line interface for direct control
- GUI interface with visualization of scanner status
- Extensible adapter architecture for adding new scanner models

## Directory Structure

- `adapters/` - Scanner-specific adapters that implement the communication protocol
- `command_libraries/` - Command definitions for different scanner models
- `scanner_gui/` - PyQt6-based graphical user interface
- `utilities/` - Shared utility modules for serial communication, logging, etc.
- `tests/` - Test suite

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/scanner-controller.git
cd scanner-controller

# Set up a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# For development
pip install -r requirements-dev.txt
```

## Usage

### Command Line Interface

```bash
python main.py
```

### Graphical Interface

```bash
python run_scanner_gui.py
```

## Supported Devices

- Uniden BC125AT
- Uniden BCD325P2
- Additional models can be added through the adapter system

## Development

This project uses pre-commit hooks to ensure code quality:

```bash
# Install pre-commit hooks
pre-commit install
```

## License

See the [LICENSE](LICENSE) file for details.
