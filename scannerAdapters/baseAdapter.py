# scanner_adapters/baseAdapter.py

class BaseScannerAdapter:
    def readVolume(self, ser): return "Not Supported"
    def writeVolume(self, ser, value): return "Not Supported"

    def readSquelch(self, ser): return "Not Supported"
    def writeSquelch(self, ser, value): return "Not Supported"

    def readFrequency(self, ser): return "Not Supported"
    def writeFrequency(self, ser, value): return "Not Supported"

    def readRSSI(self, ser): return "Not Supported"
    def readSMeter(self, ser): return "Not Supported"

    def readModel(self, ser): return "Not Supported"
    def readSWVer(self, ser): return "Not Supported"
