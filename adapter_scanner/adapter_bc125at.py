"""
LEGACY ADAPTER - REDIRECTS TO NEW LOCATION
This file is kept for backward compatibility and redirects to adapters/uniden/bc125at_adapter.py
"""

import warnings
warnings.warn(
    "Using adapter_scanner.adapter_bc125at is deprecated. "
    "Please use adapters.uniden.bc125at_adapter instead.",
    DeprecationWarning, 
    stacklevel=2
)

from adapters.uniden.bc125at_adapter import BC125ATAdapter