# 📻 Scanner Control Interface

A modular, cross-platform Python tool to control Uniden and AOR scanners via serial connection. Supports both command-line and graphical interfaces with extensible command libraries per model.

## 🧰 Features

- Auto-detects connected scanners (BC125AT, BCD325P2, SDS100, AOR-DV1)
- Interactive CLI with command completion and context-sensitive help
- Tkinter GUI for quick control (volume, squelch, frequency)
- Dynamic command registry with per-model command adapters
- Serial port abstraction and input validation
- Memory dump and programmable keypress simulation
- Easily extensible to other scanner models

## 📁 Project Structure

```text
scanner-control/
│
├── main.py                      # Entry point for CLI tool
├── scannerGUI.py                # GUI interface using tkinter
├── commandRegistry.py           # Dispatch table of supported commands
├── commandLibrary.py            # High-level wrapper for shared commands
├── readlineSetup.py             # Tab completion support for CLI
├── scannerUtils.py              # Utilities for serial communication
│
├── requirements.txt             # Python dependencies
│
├── scannerAdapters/
│   ├── baseAdapter.py           # Base class for all scanner adapters
│   ├── bc125atAdapter.py        # BC125AT-specific implementation
│   └── [otherModelAdapter].py   # Placeholder for additional models
│
├── scannerLibrary/
│   ├── bc125atCommandLibrary.py # Command definitions and help for BC125AT
│   └── [otherModelCommands].py  # Placeholder for additional models
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run CLI Interface**
   ```bash
   python main.py
   ```

3. **Run GUI Interface**
   ```bash
   python scannerGUI.py
   ```

4. **Command Examples**
   - `read volume`
   - `write volume 0.8`
   - `read frequency`
   - `dump memory`
   - `send key 123MHZ`

## 🧩 Adding Support for New Scanners

1. Create a new adapter in `scannerAdapters/`
2. Add model detection in `main.py`
3. Implement model-specific command logic
4. Add optional command library in `scannerLibrary/`

## 🛠 Dependencies

- `pyserial` for serial communication
- `pyreadline3` for Windows readline/tab-completion (optional)

## 🪪 License

This project is licensed under the **MIT License**:

```
MIT License

Copyright (c) 2025 Mark J. Hughes,
Boondock Technologies, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the “Software”), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND.
```

Please attribute this work when used in derivative projects.
