"""
Debug utility for volume controls.

This script tests volume and squelch settings and reports the responses
to determine the valid range and response format for a connected scanner.
"""

import argparse
import logging
import sys
import time
from pathlib import Path

import serial  # noqa: E402

# Add parent directory to path so we can import our modules
sys.path.append(str(Path(__file__).resolve().parent.parent))


from scanner_gui.scanner_utils import read_response, send_command  # noqa: E402

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()],
)


def test_volume_range(port, model, steps=10):
    """Test setting volume across a range of values."""
    print(f"\n=== Testing volume range on {model} at {port} ===")

    try:
        with serial.Serial(port, 115200, timeout=1.0) as ser:
            # First check current volume
            print("\nChecking current volume...")
            send_command(ser, "VOL")
            response = read_response(ser)
            print(f"Initial volume: {response}")

            # Then test incremental values
            print("\nTesting volume levels:")

            for i in range(steps + 1):
                vol = i * (100 // steps)
                print(f"\nSetting volume to {vol}%")

                # Try the main VOL command
                cmd = f"VOL,{vol}"
                send_command(ser, cmd)
                time.sleep(0.5)  # Give time to adjust
                response = read_response(ser)
                print(f"Command: {cmd} -> Response: {response!r}")

                # Check what setting was applied
                send_command(ser, "VOL")
                response = read_response(ser)
                print(f"Current volume: {response}")

                time.sleep(0.5)  # Give time between tests

    except Exception as e:
        print(f"Error: {e}")


def test_squelch_range(port, model, steps=10):
    """Test setting squelch across a range of values."""
    print(f"\n=== Testing squelch range on {model} at {port} ===")

    try:
        with serial.Serial(port, 115200, timeout=1.0) as ser:
            # First check current squelch
            print("\nChecking current squelch...")
            send_command(ser, "SQL")
            response = read_response(ser)
            print(f"Initial squelch: {response}")

            # Then test incremental values
            print("\nTesting squelch levels:")

            for i in range(steps + 1):
                sql = i * (100 // steps)
                print(f"\nSetting squelch to {sql}%")

                # Try the main SQL command
                cmd = f"SQL,{sql}"
                send_command(ser, cmd)
                time.sleep(0.5)  # Give time to adjust
                response = read_response(ser)
                print(f"Command: {cmd} -> Response: {response!r}")

                # Check what setting was applied
                send_command(ser, "SQL")
                response = read_response(ser)
                print(f"Current squelch: {response}")

                time.sleep(0.5)  # Give time between tests

    except Exception as e:
        print(f"Error: {e}")


def main():
    """
    Parse arguments and run tests.

    This function sets up the command-line interface for the script,
    allowing the user to specify the serial port, model, number of steps,
    and the type of test to perform.
    """
    parser = argparse.ArgumentParser(
        description="Debug volume and squelch controls"
    )
    parser.add_argument(
        '--port', required=True, help='Serial port (e.g., COM3)'
    )
    parser.add_argument('--model', default="Unknown", help='Scanner model')
    parser.add_argument(
        '--steps', type=int, default=10, help='Number of test steps'
    )
    parser.add_argument(
        '--test',
        choices=['volume', 'squelch', 'both'],
        default='both',
        help='What to test',
    )

    args = parser.parse_args()

    if args.test in ['volume', 'both']:
        test_volume_range(args.port, args.model, args.steps)

    if args.test in ['squelch', 'both']:
        test_squelch_range(args.port, args.model, args.steps)


if __name__ == "__main__":
    main()
