import time
import logging
import serial
from serial.tools import list_ports
from adapter_scanner.scanner_utils import clear_serial_buffer

# Configure logging
logging.basicConfig(
    filename="scanner_tool.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

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