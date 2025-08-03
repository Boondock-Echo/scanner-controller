"""Backend helpers for scanner communication."""

import logging
import time

import serial
from serial.tools import list_ports

from utilities.core.serial_utils import read_response, wait_for_data


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
            logging.info(
                f"Available port: {port_info.device} - {port_info.description}"
            )
        for port_info in ports:
            port = port_info.device
            if port in skip_ports:
                logging.info(f"Skipping port: {port} (in skip list)")
                continue
            logging.info(f"Trying port: {port} ({port_info.description})")
            try:
                with serial.Serial(
                    port, baudrate, timeout=timeout, write_timeout=0.5
                ) as ser:
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
