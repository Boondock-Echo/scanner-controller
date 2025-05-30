# Project Structure Guide

This document outlines the recommended directory structure for the Scanner Controller project and explains the purpose of each directory.

## Root Directory

The root directory should be kept clean and contain only essential files:

- `README.md` - Project documentation
- `LICENSE` - License information
- `run_scanner_gui.py` - Main entry point for the GUI application
- `setup.py` - Package installation script
- `requirements.txt` - Production dependencies
- `requirements-dev.txt` - Development dependencies
- `.gitignore` - Git ignore file
- `.pre-commit-config.yaml` - Pre-commit hooks configuration

## Core Directories

### `/scanner_gui`

Contains the GUI application code:

```
scanner_gui/
├── gui/             # GUI components
├── main.py          # Entry point
├── commandLibrary.py # Command interface
└── scannerUtils.py  # Utility functions
```

### `/adapters`

Contains scanner model-specific adapter implementations:

```
adapters/
├── uniden/         # Uniden scanner adapters
│   ├── bc125at.py
│   ├── bcd325p2.py
│   └── sds_adapter.py
├── aor/            # AOR scanner adapters
└── base_adapter.py # Base adapter class
```

### `/command_libraries`

Contains model-specific command definitions:

```
command_libraries/
└── uniden/
    └── bcd325p2/
        ├── system_commands.py
        ├── channel_commands.py
        └── scan_commands.py
```

### `/utilities`

Contains utility modules used across the project:

```
utilities/
├── core/           # Core utilities used by multiple components
├── tools/          # Utility scripts
├── commands/       # Command processing utilities
└── research/       # Experimental/research code
```

## Supporting Directories

### `/docs`

Project documentation:

```
docs/
├── project_structure.md  # This document
├── api/                  # API documentation
└── user_guide/           # User guides
```

### `/tests`

Test code:

```
tests/
├── unit/           # Unit tests
└── integration/    # Integration tests
```

### `/icons`

GUI icons and visual resources:

```
icons/
├── rotary-knob.svg
├── arrow-left.svg
└── arrow-right.svg
```

### `/dev_tools`

Development tools and scripts:

```
dev_tools/
├── analyze_unused_files.py
├── build_dependency_graph.py
└── cleanup_legacy.py
```

### `/logs`

Log files directory (git-ignored):

```
logs/
├── scanner_controller.log
└── .gitignore
```

## Guidelines for Adding New Files

1. **New Scanner Adapters**: Place in `/adapters/[manufacturer]/`
2. **New GUI Components**: Place in `/scanner_gui/gui/`
3. **New Utility Functions**: Place in `/utilities/core/` or appropriate subdirectory
4. **Documentation**: Place in `/docs/`
5. **Scripts**: Place in `/dev_tools/` or `/utilities/tools/`

## Imports Best Practices

1. Use absolute imports where possible
2. Group imports in this order:
   - Standard library imports
   - Third-party imports
   - Local application imports
3. Imports should be alphabetized within each group
4. Avoid circular dependencies
