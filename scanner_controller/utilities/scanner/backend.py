"""Backend helpers for scanner communication."""

import glob
import logging
import time

import serial
from serial.tools import list_ports

try:  # Optional dependency for HID scanners
    import hid  # type: ignore
except Exception:  # pragma: no cover - handled gracefully
    hid = None

from scanner_controller.utilities.core.serial_utils import (
    read_response,
    wait_for_data,
)


def find_all_scanner_ports(
    baudrate=115200, timeout=0.5, max_retries=2, skip_ports=None
):
    """Scan available ports for connected scanners.

    In addition to traditional serial ports this function probes for SDR
    receivers and returns pseudo-port identifiers such as ``rtlsdr:0`` or
    ``rx888:0``. These identifiers can be passed directly to
    :func:`ConnectionManager.open_connection`.
    """
    if skip_ports is None:
        skip_ports = []
    detected = []
    retries = 0
    while retries < max_retries:
        # list_ports.comports() returns an iterable that can be exhausted after
        # a single pass on some platforms (e.g. Linux).  Convert it to a list so
        # we can iterate over the available ports multiple times within this
        # loop without losing data.
        ports = list(list_ports.comports())
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
    # Attempt HID device scan if available
    if hid is not None:
        logging.info("Checking for HID scanner devices")
        for hid_path in glob.glob("/dev/usb/hiddev*"):
            try:
                dev = hid.device()
                dev.open_path(hid_path.encode())
                time.sleep(0.1)
                logging.info(f"Sending MDL to {hid_path}")
                dev.write(b"MDL\r")
                data = dev.read(64, timeout=int(timeout * 1000))
                response = bytes(data).decode(errors="ignore")
                logging.info(f"Response from {hid_path}: {response}")
                if response.startswith("MDL,"):
                    model_code = response.split(",")[1].strip()
                    detected.append((hid_path, model_code))
                dev.close()
            except Exception as e:  # pragma: no cover - best effort
                logging.warning(f"Error testing HID device {hid_path}: {e}")
        if detected:
            return detected
    # Attempt SDR device scans if available
    try:  # pragma: no cover - optional dependency
        from SoapySDR import Device  # type: ignore

        logging.info("Checking for SDR devices via SoapySDR")
        for idx, dev_info in enumerate(Device.enumerate()):
            driver = dev_info.get("driver", "sdr")
            friendly = driver.upper()
            detected.append((f"{driver}:{idx}", friendly))
    except Exception as e:  # pragma: no cover - best effort
        logging.info(f"SoapySDR enumeration unavailable: {e}")

    try:  # pragma: no cover - optional dependency
        from rtlsdr import RtlSdr  # type: ignore

        logging.info("Checking for SDR devices via pyrtlsdr")
        for idx, _ in enumerate(RtlSdr.get_devices()):
            detected.append((f"rtlsdr:{idx}", "RTLSDR"))
    except Exception as e2:  # pragma: no cover - best effort
        logging.info(f"pyrtlsdr enumeration unavailable: {e2}")

    if detected:
        return detected
    return []
