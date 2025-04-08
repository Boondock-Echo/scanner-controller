from abc import ABC, abstractmethod

class BaseScannerAdapter(ABC):
    """
    Abstract base class for all scanner adapters regardless of manufacturer.
    All scanner adapters must implement these methods.
    """
    
    def __init__(self, machine_mode=False):
        """
        Initialize the adapter
        Args:
            machine_mode: If True, returns machine-parseable output where possible
        """
        self.machine_mode = machine_mode
    
    def feedback(self, success, message):
        """Format feedback based on machine mode setting"""
        if self.machine_mode:
            return f"{'OK' if success else 'ERR'}|{message}"
        return message
    
    # Serial communication
    @abstractmethod
    def send_command(self, ser, cmd):
        """Send a raw command to the scanner"""
        pass
    
    # Basic operations
    @abstractmethod
    def readVolume(self, ser):
        """Read the current volume level"""
        pass
        
    @abstractmethod
    def writeVolume(self, ser, value):
        """Set the volume level (0.0-1.0)"""
        pass
    
    @abstractmethod
    def readSquelch(self, ser):
        """Read the current squelch level"""
        pass
        
    @abstractmethod
    def writeSquelch(self, ser, value):
        """Set the squelch level (0.0-1.0)"""
        pass
    
    # Common operations with default implementations
    def getHelp(self, command):
        """Get help for a specific command"""
        return f"No help available for {command}"
    
    def readModel(self, ser):
        """Read the scanner model"""
        return "Generic Scanner"
    
    def readSWVer(self, ser):
        """Read the scanner firmware version"""
        return "Unknown Version"
    
    def readRSSI(self, ser):
        """Read the current signal strength"""
        return "RSSI not supported"
    
    def readSMeter(self, ser):
        """Read the S-meter value"""
        return "S-meter not supported"
    
    # Optional operations
    def readFrequency(self, ser):
        """Read the current frequency"""
        return "Frequency reading not supported"
    
    def writeFrequency(self, ser, freq):
        """Set the frequency"""
        return "Frequency writing not supported"
    
    def readBatteryVoltage(self, ser):
        """Read the battery voltage"""
        return "Battery voltage reading not supported"
    
    def readWindowVoltage(self, ser):
        """Read the window voltage"""
        return "Window voltage reading not supported"
    
    def readStatus(self, ser):
        """Read the scanner status"""
        return "Status reading not supported"
    
    def sendKey(self, ser, keySeq):
        """Simulate key presses on the scanner"""
        return "Key simulation not supported"
    
    def enter_quick_frequency_hold(self, ser, freq_mhz):
        """Enter frequency hold mode"""
        return "Frequency hold not supported"
    
    def dumpMemoryToFile(self, ser, filename="memorydump.txt", 
                        start=0x00000000, end=0x0000FFFF, step=16):
        """Dump scanner memory to a file"""
        return "Memory dump not supported"
    
    def readGlobalLockout(self, ser):
        """Read global lockout list"""
        return "Global lockout reading not supported"
    
    def readChannelInfo(self, ser, index):
        """Read channel information"""
        return "Channel info reading not supported"
    
    def writeChannelInfo(self, ser, index, name, freq_khz, mod, 
                        ctcss, delay, lockout, priority):
        """Write channel information"""
        return "Channel info writing not supported"
    
    def enterProgrammingMode(self, ser):
        """Enter programming mode"""
        return "Programming mode not supported"
    
    def exitProgrammingMode(self, ser):
        """Exit programming mode"""
        return "Programming mode not supported"
