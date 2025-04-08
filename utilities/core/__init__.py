# Core utilities package
import os
import sys

# Ensure that the parent directory is in the Python path
script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# This will provide access to the same functionality through
# utilities.core as through utilities directly
try:
    from utilities.shared_utils import scanner_command, clear_serial_buffer
except ImportError:
    # Fallback if the file has already been moved
    import sys
    print("Warning: Could not import from utilities.shared_utils")
    print("If you've already moved files, update this import path")
    print(f"Python path: {sys.path}")
