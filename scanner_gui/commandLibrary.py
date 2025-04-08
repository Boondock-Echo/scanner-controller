import logging
import time
from .scanner_utils import send_command, read_response

# Define a base scanner interface class
class ScannerInterface:
    def __init__(self, model_name):
        self.model_name = model_name
        logging.info(f"Initializing interface for {model_name}")
    
    def readStatus(self, ser):
        """Read the current status from the scanner"""
        try:
            return send_command(ser, "STS")
        except Exception as e:
            logging.error(f"Error reading status: {e}")
            return "STS,000000,Error,,,,,,,,,,,,,0,0,0,0,0,0,0,0,0"
    
    def readRSSI(self, ser):
        """Read the current signal strength (0.0-1.0)"""
        try:
            rssi_raw = send_command(ser, "LVL")
            if rssi_raw.startswith("LVL,"):
                level = float(rssi_raw.split(",")[1])
                return min(1.0, max(0.0, level / 100.0))
            return 0.0
        except Exception as e:
            logging.error(f"Error reading RSSI: {e}")
            return 0.0
    
    def sendKey(self, ser, key):
        """Send a key command to the scanner"""
        if not ser.is_open:
            logging.error("Cannot send key - serial port is not open")
            return ""
            
        # Map keys to their proper identifiers
        key_map = {
            "0": "0", "1": "1", "2": "2", "3": "3", 
            "4": "4", "5": "5", "6": "6", "7": "7",
            "8": "8", "9": "9", ".": ".", "^": "V",
            "<": "<", ">": ">", "E": "E", "M": "M",
            "F": "F", "H": "H", "S": "S"
        }
        
        key_id = key_map.get(key, key)
        # Format the full command with the key press action ('P')
        cmd = f"KEY,{key_id},P"
        return send_command(ser, cmd)
    
    def writeVolume(self, ser, level):
        """Set volume level (0.0-1.0)"""
        try:
            vol = int(max(0, min(15, level * 15)))
            return send_command(ser, f"VOL,{vol}")
        except Exception as e:
            logging.error(f"Error setting volume: {e}")
            return ""
    
    def writeSquelch(self, ser, level):
        """Set squelch level (0.0-1.0)"""
        try:
            sql = int(max(0, min(15, level * 15)))
            return send_command(ser, f"SQL,{sql}")
        except Exception as e:
            logging.error(f"Error setting squelch: {e}")
            return ""

# Dictionary mapping model codes to their respective interface classes
SCANNER_MODELS = {
    "BC125AT": ScannerInterface,
    "BC346XT": ScannerInterface,
    "BCD325P2": ScannerInterface,
    "BCD396T": ScannerInterface,
    "BCT15X": ScannerInterface,
    "AOR-DV1": ScannerInterface,
    # Add more models as needed
}

def getScannerInterface(model_code):
    """
    Factory function to get the appropriate interface for a scanner model
    
    Args:
        model_code (str): The model identifier from the scanner
        
    Returns:
        ScannerInterface: An instance of the appropriate interface class
    """
    interface_class = SCANNER_MODELS.get(model_code, ScannerInterface)
    return interface_class(model_code)
