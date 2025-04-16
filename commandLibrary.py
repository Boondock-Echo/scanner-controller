"""
Command Library for Scanner Controller.

Provides a unified interface to different scanner adapters.
"""

from adapters.uniden.bc125at_adapter import BC125ATAdapter
from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter


def get_scanner_interface(model):
    """
    Get the appropriate scanner interface adapter based on model.

    Return the appropriate adapter class based on scanner model.
    """
    if model.upper() == "BC125AT":
        return BC125ATAdapter
    elif model.upper() == "BCD325P2":
        return BCD325P2Adapter
    else:
        raise ValueError(f"Unsupported scanner model: {model}")
