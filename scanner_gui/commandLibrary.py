"""
commandLibrary.py.

This module provides an interface for interacting with different scanner models.
It includes functions to read and write various scanner parameters such as
volume, squelch, frequency, RSSI, and more.
"""

# commandLibrary.py

from adapter_scanner.adapter_bc125at import BC125ATAdapter
from adapter_scanner.adapter_bcd325p2 import BCD325P2Adapter


def getScannerInterface(model):
    """
    Return the appropriate scanner adapter interface based on the model.

    Args:
        model (str): The model of the scanner (e.g., "BC125AT", "BCD325P2").

    Returns:
        object: An instance of the corresponding scanner adapter.

    Raises:
        ValueError: If the model is unsupported.
    """
    model = model.upper()
    if model == "BC125AT":
        return BC125ATAdapter()
    elif model == "BCD325P2":
        return BCD325P2Adapter()
    else:
        raise ValueError(f"Unsupported scanner model: {model}")


def readVolume(ser, model):
    """
    Read the volume level from the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.

    Returns:
        int: The current volume level of the scanner.
    """
    return getScannerInterface(model).readVolume(ser)


def writeVolume(ser, model, value):
    """
    Set the volume level on the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.
        value (int): The desired volume level to set.

    Returns:
        None
    """
    return getScannerInterface(model).writeVolume(ser, value)


def readSquelch(ser, model):
    """
    Read the squelch level from the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.

    Returns:
        int: The current squelch level of the scanner.
    """
    return getScannerInterface(model).readSquelch(ser)


def writeSquelch(ser, model, value):
    """
    Set the squelch level on the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.
        value (int): The desired squelch level to set.

    Returns:
        None
    """
    return getScannerInterface(model).writeSquelch(ser, value)


def readFrequency(ser, model):
    """
    Read the frequency from the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.

    Returns:
        float: The current frequency of the scanner.
    """
    return getScannerInterface(model).readFrequency(ser)


def writeFrequency(ser, model, value):
    """
    Set the frequency on the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.
        value (float): The desired frequency to set.

    Returns:
        None
    """
    return getScannerInterface(model).writeFrequency(ser, value)


def readRSSI(ser, model):
    """
    Read the RSSI (Received Signal Strength Indicator) from the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.

    Returns:
        int: The current RSSI value of the scanner.
    """
    return getScannerInterface(model).readRSSI(ser)


def readSMeter(ser, model):
    """
    Read the S-Meter value from the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.

    Returns:
        int: The current S-Meter value of the scanner.
    """
    return getScannerInterface(model).readSMeter(ser)


def readModel(ser, model):
    """
    Read the model information from the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.

    Returns:
        str: The model information of the scanner.
    """
    return getScannerInterface(model).readModel(ser)


def readSWVer(ser, model):
    """
    Read the software version from the scanner.

    Args:
        ser: The serial connection to the scanner.
        model (str): The model of the scanner.

    Returns:
        str: The software version of the scanner.
    """
    return getScannerInterface(model).readSWVer(ser)
