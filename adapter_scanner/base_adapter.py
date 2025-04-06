
class BaseScannerAdapter:
    def readVolume(self, ser):
        from adapter_scanner.scanner_utils import send_command
        return "Not Supported"

    def writeVolume(self, ser, value):
        from adapter_scanner.scanner_utils import send_command
        return "Not Supported"

    def readSquelch(self, ser):
        from adapter_scanner.scanner_utils import send_command
        return "Not Supported"

    def writeSquelch(self, ser, value):
        from adapter_scanner.scanner_utils import send_command
        return "Not Supported"

    def readFrequency(self, ser):
        from adapter_scanner.scanner_utils import send_command
        return "Not Supported"

    def writeFrequency(self, ser, value):
        from adapter_scanner.scanner_utils import send_command
        return "Not Supported"

    def readRSSI(self, ser):
        from adapter_scanner.scanner_utils import send_command
        return "Not Supported"

    def readSMeter(self, ser): return "Not Supported"

    def readModel(self, ser):
        return "Not Supported"

    def readSWVer(self, ser):
        return "Not Supported"