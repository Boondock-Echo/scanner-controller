"""
Test volume ranges for different scanners.

This tool tests volume commands with different range values to determine
what your specific scanner model supports.
"""

import argparse
import logging
import time

import serial

from scanner_gui.scanner_utils import read_response, send_command

logging.basicConfig(
    level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s'
)


def test_volume_command(port, baudrate=115200):
    """
    Test volume commands with various ranges.

    This function tries setting volume to different values to determine
    what range your scanner supports.
    """
    print(f"\nTesting volume command range on {port}...")

    try:
        with serial.Serial(port, baudrate, timeout=1.0) as ser:
            # First check current volume
            send_command(ser, "VOL")
            response = read_response(ser)
            print(f"Current volume setting: {response}")

            # Test various ranges
            ranges = [
                (0, 15),  # Most common for Uniden scanners
                (0, 31),
                (0, 63),
                (0, 100),
                (0, 255),
            ]

            for vol_min, vol_max in ranges:
                print(f"\nTesting range: {vol_min}-{vol_max}")

                # Try setting to min
                send_command(ser, f"VOL,{vol_min}")
                time.sleep(0.5)
                send_command(ser, "VOL")
                response = read_response(ser)
                print(f"Set to min ({vol_min}): {response}")

                # Try setting to max
                send_command(ser, f"VOL,{vol_max}")
                time.sleep(0.5)
                send_command(ser, "VOL")
                response = read_response(ser)
                print(f"Set to max ({vol_max}): {response}")

                # Try setting to mid-point
                mid = (vol_min + vol_max) // 2
                send_command(ser, f"VOL,{mid}")
                time.sleep(0.5)
                send_command(ser, "VOL")
                response = read_response(ser)
                print(f"Set to mid ({mid}): {response}")

                print("\n---")

            # Restore to a reasonable volume
            send_command(ser, "VOL,10")
            time.sleep(0.5)
            send_command(ser, "VOL")
            response = read_response(ser)
            print(f"Restored to 10: {response}")

    except Exception as e:
        print(f"Error: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Test scanner volume range support"
    )
    parser.add_argument('port', help='Serial port (e.g., COM3)')
    parser.add_argument(
        '--baudrate', type=int, default=115200, help='Baud rate'
    )

    args = parser.parse_args()
    test_volume_command(args.port, args.baudrate)


if __name__ == "__main__":
    main()
