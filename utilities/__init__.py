# This makes the utilities directory a proper Python package
# Import commonly used utilities for easy access

# From core/shared_utils.py
try:
    from utilities.core.shared_utils import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.shared_utils import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import shared_utils")

# From core/command_library.py
try:
    from utilities.core.command_library import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.command_library import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import command_library")

# From core/scanner_utils.py
try:
    from utilities.core.scanner_utils import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.scanner_utils import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import scanner_utils")

# From core/serial_utils.py
try:
    from utilities.core.serial_utils import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.serial_utils import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import serial_utils")

# From core/log_trim.py
try:
    from utilities.core.log_trim import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.log_trim import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import log_trim")

# From commands/uniden_command_finder.py
try:
    from utilities.commands.uniden_command_finder import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.uniden_command_finder import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import uniden_command_finder")

# From commands/command_registry.py
try:
    from utilities.core.command_registry import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.core.command_registry import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import command_registry")

# From tools/discover_qsh_format.py
try:
    from utilities.tools.discover_qsh_format import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.discover_qsh_format import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import discover_qsh_format")

# From tools/run_full_qsh_discovery.py
try:
    from utilities.tools.run_full_qsh_discovery import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.run_full_qsh_discovery import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import run_full_qsh_discovery")

# From tools/readline_setup.py
try:
    from utilities.tools.readline_setup import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.readline_setup import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import readline_setup")

# From tools/log_utils.py
try:
    from utilities.tools.log_utils import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.log_utils import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import log_utils")

# From tools/validators.py
try:
    from utilities.tools.validators import *
except (ImportError, ModuleNotFoundError):
    # Fallback to original location if not yet moved
    try:
        from utilities.validators import *
    except (ImportError, ModuleNotFoundError):
        print(f"Warning: Could not import validators")

