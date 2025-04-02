import scanner_library
from scanner_library.bcd325p2CommandLibrary import commands
from scanner_library.bc125atCommandLibrary import commands

import time

class BaseScannerAdapter:
    def readVolume(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def writeVolume(self, ser, value):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readSquelch(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def writeSquelch(self, ser, value):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readFrequency(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def writeFrequency(self, ser, value):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readRSSI(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readSMeter(self, ser): return "Not Supported"

    def readModel(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"

    def readSWVer(self, ser):
        from scanner_adapters.scanner_utils import send_command
        return "Not Supported"