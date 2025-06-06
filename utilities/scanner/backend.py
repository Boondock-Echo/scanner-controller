import logging
import time

import serial
from serial.tools import list_ports


def clear_serial_buffer(ser):
    """Clear accumulated data in the serial buffer."""
    try:
        time.sleep(0.2)
        while ser.in_waiting:
            ser.read(ser.in_waiting)
        logging.debug("Serial buffer cleared.")
    except Exception as e:
        logging.error(f"Error clearing serial buffer: {e}")


def wait_for_data(ser, max_wait=0.3):
    """Wait for data to arrive on the serial port."""
    start_time = time.time()
    while time.time() - start_time < max_wait:
        if ser.in_waiting > 0:
            return True
        time.sleep(0.01)
    return False


def read_response(ser, timeout=1.0):
    """Read a response from the scanner."""
    start_time = time.time()
    response = b""
    while True:
        if time.time() - start_time > timeout:
            break
        if ser.in_waiting > 0:
            new_data = ser.read(ser.in_waiting)
            response += new_data
            if response.endswith(b"\r\n") or response.endswith(b"\r"):
                break
        else:
            time.sleep(0.01)
    response_str = response.decode("ascii", errors="replace").strip()
    logging.debug(f"Received: {response_str}")
    return response_str


def send_command(ser, command):
    """Send a command to the scanner and return the response."""
    clear_serial_buffer(ser)
    if isinstance(command, str):
        command = command.encode("ascii")
    if not command.endswith(b"\r"):
        command += b"\r"
    logging.debug(f"Sending: {command}")
    ser.write(command)
    return read_response(ser)


def find_all_scanner_ports(baudrate=115200, timeout=0.5, max_retries=2, skip_ports=None):
    """Scan available serial ports for connected scanners."""
    if skip_ports is None:
        skip_ports = []
    detected = []
    retries = 0
    while retries < max_retries:
        ports = list_ports.comports()
        logging.info(f"Available ports: {len(ports)}")
        for port_info in ports:
            logging.info(f"Available port: {port_info.device} - {port_info.description}")
        for port_info in ports:
            port = port_info.device
            if port in skip_ports:
                logging.info(f"Skipping port: {port} (in skip list)")
                continue
            logging.info(f"Trying port: {port} ({port_info.description})")
            try:
                with serial.Serial(port, baudrate, timeout=timeout, write_timeout=0.5) as ser:
                    time.sleep(0.1)
                    logging.info(f"Sending MDL to {port}")
                    ser.write(b"MDL\r")
                    wait_for_data(ser, max_wait=0.3)
                    model_response = read_response(ser)
                    logging.info(f"Response from {port}: {model_response}")
                    if model_response.startswith("MDL,"):
                        model_code = model_response.split(",")[1].strip()
                        detected.append((port, model_code))
                        continue
                    ser.reset_input_buffer()
                    time.sleep(0.1)
                    logging.info(f"Sending WI to {port}")
                    ser.write(b"WI\r\n")
                    wait_for_data(ser, max_wait=0.3)
                    wi_response = read_response(ser)
                    logging.info(f"Response from {port}: {wi_response}")
                    if "AR-DV1" in wi_response:
                        detected.append((port, "AOR-DV1"))
            except Exception as e:
                logging.warning(f"Error testing port {port}: {e}")
        if detected:
            return detected
        retries += 1
        logging.info("No scanners found. Retrying in 3 seconds...")
        time.sleep(3)
    logging.error("No scanners found after maximum retries.")
    return []
