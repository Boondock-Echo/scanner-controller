"""
Scanner Diagnostics Tool.

This tool helps diagnose issues with scanner communication by testing various
commands and displaying available adapter methods.
"""

import argparse
import logging
import time

import serial
from serial.tools import list_ports

from scanner_gui.controller import ScannerController
from utilities.core.serial_utils import read_response, send_command, wait_for_data

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger("diagnostic")


def test_direct_commands(port, commands):
    """Test sending commands directly to the scanner."""
    print(f"\n=== Testing direct commands on {port} ===")

    try:
        with serial.Serial(port, 115200, timeout=1.0) as ser:
            for cmd in commands:
                print(f"\nSending: {cmd}")
                ser.reset_input_buffer()
                send_command(ser, cmd)
                wait_for_data(ser)
                response = read_response(ser)
                print(f"Response: {response}")
                time.sleep(0.5)  # Give scanner time to process

    except Exception as e:
        print(f"Error testing commands: {e}")


def list_adapter_methods(port, model):
    """List all methods available on the adapter."""
    print(f"\n=== Listing adapter methods for {model} on {port} ===")

    try:
        controller = ScannerController()
        if controller.connect(port=port, model=model):
            if controller.adapter:
                methods = [
                    m for m in dir(controller.adapter) if not m.startswith('_')
                ]
                print("Available adapter methods:")
                for method in sorted(methods):
                    print(f"  - {method}")
            else:
                print(f"No adapter found for {model}")
        else:
            print(f"Failed to connect to {model} on {port}")
    except Exception as e:
        print(f"Error listing methods: {e}")


def main():
    """
    Parse arguments and run diagnostics.

    This function handles command-line arguments for port selection,
    model selection, and scanning for available ports. It also runs
    diagnostics based on the provided parameters.
    """
    parser = argparse.ArgumentParser(
        description="Scanner communication diagnostics tool"
    )
    parser.add_argument('--port', help='Serial port to use (e.g., COM3)')
    parser.add_argument('--model', help='Scanner model (e.g., BCD325P2)')
    parser.add_argument(
        '--scan', action='store_true', help='Scan for available ports'
    )
    args = parser.parse_args()

    if args.scan:
        print("=== Scanning for available ports ===")
        ports = list(list_ports.comports())
        for port in ports:
            print(f"{port.device}: {port.description}")
        return

    if not args.port:
        print("Error: You must specify a port with --port")
        return

    # Common test commands for scanners
    test_commands = [
        "MDL",  # Model query
        "VER",  # Version query
        "VOL",  # Volume query
        "SQL",  # Squelch query
        "VOL,50",  # Set volume to 50%
        "SQL,50",  # Set squelch to 50%
        "PWR",  # Power/RSSI query
        "STS",  # Status query
    ]

    # Test direct commands
    test_direct_commands(args.port, test_commands)

    # If model is provided, list adapter methods
    if args.model:
        list_adapter_methods(args.port, args.model)


if __name__ == "__main__":
    main()
