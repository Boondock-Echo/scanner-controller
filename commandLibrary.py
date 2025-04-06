# commandLibrary.py

from adapter_scanner.adapter_bc125at import BC125ATAdapter
from adapter_scanner.adapter_bcd325p2 import BCD325P2Adapter
from adapter_scanner.adapter_sds100 import SDS100Adapter
from adapter_scanner.adapter_ardv1 import AORDV1Adapter


def getScannerInterface(model):
    model = model.upper()
    if model == "BC125AT":
        return BC125ATAdapter()
    elif model == "BCD325P2":
        return BCD325P2Adapter()
    elif model == "SDS100" or model == "SDS200":
        return SDS100Adapter()
    elif model == "AOR-DV1":
        return AORDV1Adapter()
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