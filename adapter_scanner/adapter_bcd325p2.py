"""
LEGACY ADAPTER - REDIRECTS TO NEW LOCATION
This file is kept for backward compatibility and redirects to adapters/uniden/bcd325p2_adapter.py
"""

import warnings
warnings.warn(
    "Using adapter_scanner.adapter_bcd325p2 is deprecated. "
    "Please use adapters.uniden.bcd325p2_adapter instead.",
    DeprecationWarning, 
    stacklevel=2
)

from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter