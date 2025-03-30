# Scanner Controller

This project provides a graphical user interface (GUI) for controlling various scanner models. The GUI is built using PyQt6 and supports multiple scanner models through modular adapters.

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

- **BC125AT**
- **BCD325P2**
- **SDS100** / **SDS200**
- **AOR-DV1**

The code should work for pretty much any Uniden scanner and is abstracted enough to allow
easy porting to other manufacturers as well.

AR-DV1 development is paused while the device in in the shop for repairs.

## Project Structure

The project is organized as follows:

```
scanner-controller/
│
├── scanner_gui/
│   ├── gui/
│   │   ├── audioControls.py       # Audio controls (volume, squelch)
│   │   ├── controlKeys.py         # Control keys (Hold, Scan, etc.)
│   │   ├── displayGroup.py        # LCD display simulation
│   │   ├── keypad.py              # Numeric keypad
│   │   ├── rotaryKnob.py          # Rotary knob simulation
│   │   ├── signalMeters.py        # Signal meters (RSSI, SQL)
│   │   ├── scannerGui.py          # Main GUI implementation
│   │   ├── style.qss              # Stylesheet for the GUI
│   │   └── __init__.py
│   ├── commandLibrary.py          # Scanner command interface
│   ├── scannerUtils.py            # Utility functions for serial communication
│   ├── main.py                    # Entry point for the application
│   └── __init__.py
│
├── oldgui/                        # Legacy GUI implementation
│   ├── scannerGui.py
│   └── scannerGuiOld.py.bak
│
├── icons/                         # SVG icons for the GUI
│   ├── rotary-knob.svg
│   ├── arrow-left.svg
│   └── arrow-right.svg
│
└── README.md                      # Project documentation
```

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/scanner-controller.git
   cd scanner-controller
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure the required scanner models are connected via serial ports.

## Usage

1. Run the application:
   ```bash
   python -m scanner_gui.main
   ```

2. Use the GUI to interact with your scanner:
   - Select the scanner port from the dropdown and click "Connect".
   - Use the sliders, buttons, and keypad to control the scanner.
   - View real-time updates on the display and signal meters.

## Development Notes

### Modular GUI Components

The GUI is modularized into separate components for better maintainability:
- **`audioControls.py`**: Handles volume and squelch sliders.
- **`controlKeys.py`**: Implements vertical control buttons.
- **`displayGroup.py`**: Simulates the scanner's LCD display.
- **`keypad.py`**: Provides a numeric keypad for input.
- **`rotaryKnob.py`**: Simulates a rotary knob with left/right buttons.
- **`signalMeters.py`**: Displays RSSI and squelch levels.

### Scanner Adapters

The `commandLibrary.py` dynamically loads the appropriate adapter for the connected scanner model. Each adapter implements model-specific commands.

### Styling

The GUI styling is defined in `style.qss`, ensuring a consistent look and feel across all components.

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Submit a pull request with a detailed description of your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
