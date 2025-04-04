import time
import logging
import serial
import serial.tools
from scanner_library.bcd325p2CommandLibrary import commands
from scanner_adapters.base_adapter import BaseScannerAdapter
import scanner_library.bc125atCommandLibrary
from utilities.logUtils import trim_log_file
from serial.tools import list_ports
from scanner_adapters.scanner_utils import clear_serial_buffer

# Configure logging
logging.basicConfig(
    filename="scanner_tool.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

def trim_log_file(log_file, max_size=1024 * 1024):
    """
    Trims the log file to ensure it does not exceed max_size bytes.
    Keeps only the last max_size bytes of the file.
    """
    try:
        with open(log_file, "rb") as f:
            f.seek(0, 2)  # Move to the end of the file
            size = f.tell()
            if size <= max_size:
                return
            f.seek(-max_size, 2)  # Move to the last max_size bytes
            data = f.read()
        with open(log_file, "wb") as f:
            f.write(data)
        logging.info(f"Trimmed log file {log_file} to {max_size} bytes.")
    except Exception as e:
        logging.error(f"Error trimming log file {log_file}: {e}")


def read_response(ser, timeout=1.0):
    """
    Reads bytes from the serial port until a carriage return (\r or \n) is encountered.
    """
    response_bytes = bytearray()
    try:
        while True:
            byte = ser.read(1)
            if not byte:
                break  # timeout reached
            if byte in b'\r\n':
                break
            response_bytes.extend(byte)
        response = response_bytes.decode("utf-8", errors="ignore").strip()
        logging.debug(f"Received response: {response}")
        return response
    except Exception as e:
        logging.error(f"Error reading response: {e}")
        return ""

def send_command(ser, cmd):
    """
    Clears the buffer and sends a command (with CR termination) to the scanner.
    """
    clear_serial_buffer(ser)
    full_cmd = cmd.strip() + "\r"
    try:
        ser.write(full_cmd.encode("utf-8"))
        logging.info(f"Sent command: {cmd}")
    except Exception as e:
        logging.error(f"Error sending command {cmd}: {e}")
        return ""
    return read_response(ser)

def wait_for_data(ser, max_wait=0.3):
    """
    Waits up to max_wait seconds for incoming data on the serial port.
    Returns True if data is available, otherwise False.
    """
    start = time.time()
    while time.time() - start < max_wait:
        if ser.in_waiting:
            return True
        time.sleep(0.01)
    return False

"""
def find_all_scanner_ports(baudrate=115200, timeout=0.5, max_retries=2):
    
    #Scans all COM ports and returns a list of tuples (port_name, model_code).
    
    from serial.tools import list_ports
    detected = []
    retries = 0
    while retries < max_retries:
        ports = list_ports.comports()
        for port in ports:
            try:
                with serial.Serial(port.device, baudrate, timeout=timeout) as ser:
                    ser.write(b"MDL\r")
                    response = read_response(ser)
                    if response.startswith("MDL"):
                        detected.append((port.device, response.split(",")[1].strip()))
            except Exception:
                continue
        retries += 1
    return detected
"""
def find_all_scanner_ports(baudrate=115200, timeout=0.5, max_retries=2):
    """
    Scans all COM ports and returns a list of tuples (port_name, model_code)
    where model_code matches one of the SCANNER_MODELS keys.
    """
    detected = []
    retries = 0
    while retries < max_retries:
        ports = list_ports.comports()
        for port in ports:
            logging.info(f"Trying port: {port.device} ({port.description})")
            try:
                with serial.Serial(port.device, baudrate, timeout=timeout) as ser:
                    ser.reset_input_buffer()
                    time.sleep(0.1)  # allow scanner to wake up
                    logging.info(f"Sending MDL to {port.device}")
                    ser.write(b"MDL\r")
                    wait_for_data(ser, max_wait=0.3)
                    model_response = read_response(ser)
                    logging.info(f"Response from {port.device}: {model_response}")
                    if model_response.startswith("MDL,"):
                        model_code = model_response.split(",")[1].strip()
                        detected.append((port.device, model_code))
                        continue

                    ser.reset_input_buffer()
                    time.sleep(0.1)
                    logging.info(f"Sending WI to {port.device}")
                    ser.write(b"WI\r\n")
                    wait_for_data(ser, max_wait=0.3)
                    wi_response = read_response(ser)
                    logging.info(f"Response from {port.device}: {wi_response}")
                    if "AR-DV1" in wi_response:
                        detected.append((port.device, "AOR-DV1"))
            except Exception as e:
                logging.warning(f"Error checking port {port.device}: {e}")
        if detected:
            return detected
        retries += 1
        logging.info("No scanners found. Retrying in 3 seconds...")
        time.sleep(3)
    logging.error("No scanners found after maximum retries.")
    return []

def wait_for_data(ser, max_wait=0.3):
    """
    Waits up to max_wait seconds for incoming data on the serial port.
    Returns True if data is available, otherwise False.
    """
    start = time.time()
    while time.time() - start < max_wait:
        if ser.in_waiting:
            return True
        time.sleep(0.01)
    return False



class BC125ATAdapter(BaseScannerAdapter):
    def __init__(self, machineMode=False):
        self.machineMode = machineMode

    def feedback(self, success, message):
        if self.machineMode:
            return "OK" if success else "ERROR"
        return message

    def getHelp(self, command):
        try:
            return scanner_library.bc125atCommandLibrary.getHelp(command)
        except Exception as e:
            return self.feedback(False, f"❌\t[getHelp Error] {e}")

    def dumpMemoryToFile(self, ser, filename="memorydump.txt", start=0x00000000, end=0x0000FFFF, step=16):
        import sys

        def hex32(i): return f"{i:08X}"

        def update_progress(current, total):
            percent = int(100 * current / total)
            if percent > update_progress.last_shown:
                update_progress.last_shown = percent
                bar = "#" * (percent // 2)
                sys.stdout.write(f"\rProgress: [{bar:<50}] {percent}%")
                sys.stdout.flush()
        update_progress.last_shown = -1

        try:
            send_command(ser, "PRG")
            total_steps = ((end - start) // step) + 1
            valid_count, invalid_streak = 0, 0
            MAX_INVALID = 4096
            with open(filename, "w") as f:
                for i in range(total_steps):
                    addr = start + i * step
                    cmd = f"MRD,{hex32(addr)}"
                    response = send_command(ser, cmd)
                    if response.startswith("MRD,"):
                        f.write(response + "\n")
                        valid_count += 1
                        invalid_streak = 0
                    elif "ERR" in response or "NG" in response:
                        invalid_streak += 1
                    else:
                        f.write(f"❌ # Unexpected: {response}\n")
                        invalid_streak += 1
                    if invalid_streak >= MAX_INVALID:
                        return self.feedback(False, f"❌ \nAborted early — {MAX_INVALID} invalids.")
                    update_progress(i, total_steps)
            send_command(ser, "EPG")
            return self.feedback(True, f"{valid_count} MRD entries written to {filename}")
        except Exception as e:
            try: send_command(ser, "EPG")
            except: pass
            return self.feedback(False, f"[Memory Dump Error] {e}")

    def enter_quick_frequency_hold(self, ser, freq_mhz):
        try:
            send_command(ser, "PRG")
            time.sleep(0.2)
            send_command(ser, "EPG")
            time.sleep(0.2)
            send_command(ser, "KEY,S,P")
            time.sleep(0.1)
            send_command(ser, "KEY,S,P")
            time.sleep(0.1)
            send_command(ser, "KEY,H,P")
            time.sleep(0.1)
            freq_str = f"{freq_mhz:.3f}"
            for char in freq_str:
                if char in "0123456789.":
                    send_command(ser, f"KEY,{char},P")
                    time.sleep(0.05)
            send_command(ser, "KEY,H,P")
            time.sleep(0.3)
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                actual_freq = int(parts[2]) / 10000.0
                if abs(actual_freq - freq_mhz) < 0.005:
                    return self.feedback(True, f"✅ Frequency {freq_str} MHz entered and confirmed via PWR ({actual_freq:.5f} MHz)")
                else:
                    return self.feedback(False, f"⚠️ Entered {freq_str} MHz, but PWR returned {actual_freq:.5f} MHz")
            return self.feedback(False, f"❌ PWR returned unexpected: {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [enter_quick_frequency_hold Error] {e}")

    def writeKeyBeep(self, ser, level=99, lock=0):
        try:
            send_command(ser, "PRG")
            cmd = commands["KBP"]
            response = send_command(ser, cmd.buildCommand(f"{level},{lock}"))
            send_command(ser, "EPG")
            return self.feedback(True, f"✅ Set key beep to {level}, lock to {lock} → {response}")
        except Exception as e:
            return self.feedback(False, f"[writeKeyBeep Error] {e}")

    def readVolume(self, ser):
        try:
            response = send_command(ser, commands["VOL"].buildCommand())
            _, value = response.split(",", 1)
            volume = float(int(value.strip()) / 15.0)
            return self.feedback(True, f"✅ Volume level: {volume:.2f}")
        except Exception as e:
            return self.feedback(False, f"❌ [readVolume Error] {e}")

    def writeVolume(self, ser, value):
        try:
            if not (0.0 <= value <= 1.0):
                return self.feedback(False, "⚠️ Volume must be between 0.0 and 1.0")
            scaled = int(round(value * 15))
            response = send_command(ser, commands["VOL"].buildCommand(scaled))
            return self.feedback("OK" in response, f"✅ Volume set to {value:.2f} → {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [writeVolume Error] {e}")

    def readSquelch(self, ser):
        try:
            response = send_command(ser, commands["SQL"].buildCommand())
            _, value = response.split(",", 1)
            squelch = float(int(value.strip()) / 15.0)
            return self.feedback(True, f"✅ Squelch level: {squelch:.2f}")
        except Exception as e:
            return self.feedback(False, f"❌ [readSquelch Error] {e}")

    def writeSquelch(self, ser, value):
        try:
            if not (0.0 <= value <= 1.0):
                return self.feedback(False, "❌ Squelch must be between 0.0 and 1.0")
            scaled = int(round(value * 15))
            send_command(ser, "PRG")
            response = send_command(ser, commands["SQL"].buildCommand(scaled))
            send_command(ser, "EPG")
            return self.feedback("OK" in response, f"✅Squelch set to {value:.2f} → {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [writeSquelch Error] {e}")

    def readFrequency(self, ser):
        try:
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                freq_mhz = (int(parts[2]) * 100) / 1_000_000
                return self.feedback(True, f"✅ Frequency: {round(freq_mhz, 5)} MHz")
            return self.feedback(False, f"❌ Unexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [readFrequency Error] {e}")

    def writeFrequency(self, ser, freq_mhz):
        try:
            send_command(ser, "PRG")
            send_command(ser, "EPG")
            time.sleep(0.1)
            for _ in range(2):
                send_command(ser, "KEY,S")
                time.sleep(0.2)
                send_command(ser, "KEY,H")
            freq_str = f"{float(freq_mhz):.3f}"
            for char in freq_str:
                if char in "0123456789.":
                    send_command(ser, f"KEY,{char}")
                    time.sleep(0.1)
            send_command(ser, "KEY,E")
            return self.feedback(True, f"✅ Frequency {freq_str} MHz entered via keypress")
        except Exception as e:
            return self.feedback(False, f"❌ [writeFrequency Error] {e}")

    def readRSSI(self, ser):
        try:
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                rssi = round(int(parts[1]) / 1023.0, 3)
                return self.feedback(True, f"✅ RSSI: {rssi}")
            return self.feedback(False, f"❌ Unexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [readRSSI Error] {e}")

    def sendKey(self, ser, keySeq):
        if not keySeq:
            return self.feedback(False, "❌ No key(s) provided.")

        responses = []
        for char in keySeq:
            if char not in "0123456789<>^.EMFHSLP":
                responses.append(f"{char} → skipped (invalid key)")
                continue
            try:
                response = send_command(ser, f"KEY,{char},P")
                responses.append(f"✅ {char} → {response}")
            except Exception as e:
                responses.append(f"❌ {char} → ERROR: {e}")
        return "\n".join(responses)

    def readModel(self, ser):
        try:
            model = send_command(ser, commands["MDL"].buildCommand())
            return self.feedback(True, f"✅ Model: {model}")
        except Exception as e:
            return self.feedback(False, f"❌ [readModel Error] {e}")

    def readSWVer(self, ser):
        try:
            version = send_command(ser, commands["VER"].buildCommand())
            return self.feedback(True, f"✅ Software Version: {version}")
        except Exception as e:
            return self.feedback(False, f"❌ [readSWVer Error] {e}")

    def readSMeter(self, ser):
        return self.feedback(False, "❌ SMeter not supported")