"""
Scanner GUI Command Library
"""

# Update imports to use new module paths
from adapters.uniden.bc125at_adapter import BC125ATAdapter  # Changed from adapter_scanner.adapter_bc125at
from adapters.uniden.bcd325p2_adapter import BCD325P2Adapter  # Changed from adapter_scanner.adapter_bcd325p2


def getScannerInterface(model):
    model = model.upper()
    if model == "BC125AT":
        return BC125ATAdapter()
    elif model == "BCD325P2":
        return BCD325P2Adapter()
    else:
        raise ValueError(f"Unsupported scanner model: {model}")

def readVolume(ser, model):
    return getScannerInterface(model).readVolume(ser)

def writeVolume(ser, model, value):
    return getScannerInterface(model).writeVolume(ser, value)

def readSquelch(ser, model):
    return getScannerInterface(model).readSquelch(ser)

def writeSquelch(ser, model, value):
    return getScannerInterface(model).writeSquelch(ser, value)

def readFrequency(ser, model):
    return getScannerInterface(model).readFrequency(ser)

def writeFrequency(ser, model, value):
    return getScannerInterface(model).writeFrequency(ser, value)

def readRSSI(ser, model):
    return getScannerInterface(model).readRSSI(ser)

def readSMeter(ser, model):
    return getScannerInterface(model).readSMeter(ser)

def readModel(ser, model):
    return getScannerInterface(model).readModel(ser)

def readSWVer(ser, model):
    return getScannerInterface(model).readSWVer(ser)