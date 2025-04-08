from serial.tools import list_ports
import serial
import time
import logging

# Scanner Utilities Module
# This module provides common functions for scanner communication.

def clear_serial_buffer(ser):
    """
    Clears any accumulated data in the serial buffer before sending commands.
    """
    try:
        time.sleep(0.2)  # Allow any ongoing transmission to complete
        while ser.in_waiting:
            ser.read(ser.in_waiting)  # Flush buffer
        logging.debug("Serial buffer cleared.")
    except Exception as e:
        logging.error(f"Error clearing serial buffer: {e}")

def read_response(ser, timeout=1.0):
    """
    Reads bytes from the serial port until a carriage return (\r) is encountered
    or the timeout expires.
    """
    response_bytes = bytearray()
    start_time = time.time()
    
    try:
        while time.time() - start_time < timeout:
            if ser.in_waiting:
                byte = ser.read(1)
                if byte in b'\r\n':  # Stop reading at CR or LF
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
    if not ser.is_open:
        logging.error("Cannot send command - serial port is not open")
        return ""
        
    try:
        clear_serial_buffer(ser)
        full_cmd = cmd.strip() + "\r"
        logging.debug(f"Sending command: {cmd}")
        
        # Convert to uppercase and encode as bytes
        cmd_bytes = full_cmd.upper().encode("utf-8")
        ser.write(cmd_bytes)
        
        # Wait a moment for the command to be processed
        time.sleep(0.1)
        
        # Read the response
        return read_response(ser)
    except Exception as e:
        logging.error(f"Error sending command {cmd}: {e}")
        return ""

def find_all_scanner_ports(baudrate=115200, timeout=0.5, max_retries=2, skip_ports=None):
    """
    Scans all COM ports and returns a list of tuples (port_name, model_code)
    where model_code matches one of the SCANNER_MODELS keys.
    
    Args:
        baudrate (int): Baud rate to use when checking ports
        timeout (float): Timeout for serial operations
        max_retries (int): Number of times to retry scanning if no scanners found
        skip_ports (list): Optional list of port names to skip (already in use)
    """
    if skip_ports is None:
        skip_ports = []
        
    detected = []
    retries = 0
    while retries < max_retries:
        ports = list_ports.comports()
        for port in ports:
            # Skip ports that are already known to be in use
            if port.device in skip_ports:
                logging.debug(f"Skipping {port.device} (marked as in use)")
                continue
                
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