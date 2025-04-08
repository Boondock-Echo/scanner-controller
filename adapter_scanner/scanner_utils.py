"""
LEGACY SCANNER UTILITIES - REDIRECTS TO NEW LOCATION
This file is kept for backward compatibility and redirects to utilities/scanner_utils.py

DEPRECATION NOTICE: This module will be removed in version 2.0.0 (estimated Q3 2023).
All code should import directly from utilities.scanner_utils instead.
"""

import warnings
import inspect
import os
import sys

warnings.warn(
    "Using adapter_scanner.scanner_utils is deprecated. "
    "Please use utilities.scanner_utils instead. "
    "This redirect will be removed in version 2.0.0.",
    DeprecationWarning, 
    stacklevel=2
)

# Import directly from utilities.scanner_utils, but don't create a circular reference
import utilities.scanner_utils as utils

# Re-export the functions
clear_serial_buffer = utils.clear_serial_buffer
read_response = utils.read_response
send_command = utils.send_command
find_all_scanner_ports = utils.find_all_scanner_ports
wait_for_data = utils.wait_for_data

# Utility function to help identify where this legacy module is still being used
def _log_legacy_usage():
    """Log where this legacy module is being used to assist with migration"""
    frame = inspect.currentframe().f_back.f_back
    caller_file = frame.f_code.co_filename
    caller_line = frame.f_lineno
    
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)
    
    with open(os.path.join(log_dir, "legacy_usage.log"), "a") as f:
        f.write(f"{caller_file}:{caller_line} imported adapter_scanner.scanner_utils\n")

# Only log in non-production environments
if "PRODUCTION" not in os.environ:
    _log_legacy_usage()