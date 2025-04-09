#!/usr/bin/env python3
"""
Serial Port Tester for Scanner Controller

This script tests direct serial communication with the scanner to verify
that commands are properly sent and received.

Usage:
    python serial_test.py [port_name]
"""

import logging
import sys
import time

import serial
from serial.tools import list_ports

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("logs/serial_test.log"), logging.StreamHandler()],
)


def scan_for_scanners():
    """Scan for scanners on all COM ports"""
    print("Scanning for scanners...")

    for port in list_ports.comports():
        print(f"Testing {port.device} ({port.description})...")

        try:
            with serial.Serial(port.device, 115200, timeout=1) as ser:
                # Clear any pending data
                ser.reset_input_buffer()
                time.sleep(0.2)

                # Send MDL command
                print(f"  Sending MDL to {port.device}...")
                ser.write(b"MDL\r")
                time.sleep(0.2)

                # Read response
                response = ser.read(ser.in_waiting or 1)
                response_str = response.decode("ascii", errors="replace")
                print(f"  Response: {response_str}")

                if "MDL" in response_str:
                    print(f"✓ Scanner found on {port.device}!")
                    return port.device
        except Exception as e:
            print(f"  Error: {e}")

    print("No scanners found.")
    return None


def send_command(port, command):
    """Send a command to the scanner and display the response"""
    try:
        with serial.Serial(port, 115200, timeout=1) as ser:
            # Clear buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            time.sleep(0.2)

            # Send command
            print(f"Sending: {command}")
            ser.write(f"{command}\r".encode("ascii"))

            # Wait for response
            time.sleep(0.3)

            # Read response
            response = ser.read(ser.in_waiting or 1)
            response_str = response.decode("ascii", errors="replace")
            print(f"Response: {response_str}")

            return response_str
    except Exception as e:
        print(f"Error: {e}")
        return None


def main():
    # Get port from command line or scan
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        port = scan_for_scanners()

    if not port:
        print("Please specify a COM port (e.g., COM1)")
        return

    print(f"\nTesting communication with scanner on {port}")
    print("=" * 50)

    # Test basic commands
    send_command(port, "MDL")
    time.sleep(0.5)

    # Test sending a key command
    send_command(port, "KEY,1")
    time.sleep(0.5)

    # Test reading display
    send_command(port, "STS")

    print("\nTest complete!")


if __name__ == "__main__":
    main()
