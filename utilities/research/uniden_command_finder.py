"""
Module to find and test commands on the Uniden BCD325P2 scanner.

This module provides utilities for communicating with and testing commands on
the Uniden BCD325P2 scanner.

It includes functions for finding the scanner's COM port, sending commands, and
logging results.
"""

import itertools
import string
import time

import serial
from serial.tools import list_ports


def find_scanner_port(baudrate=115200, timeout=0.5):
    """
    Poll all available COM ports, send the "MDL" command.

    Return the port name if the response is "MDL,BCD325P2".
    If not found, waits 5 seconds and retries.
    """
    while True:
        ports = list_ports.comports()
        for port in ports:
            try:
                with serial.Serial(
                    port.device, baudrate, timeout=timeout
                ) as ser:
                    # Clear any pending data
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    time.sleep(0.2)  # Allow time for the port to settle
                    ser.write("MDL\r\n".encode("utf-8"))
                    response = read_response(ser)
                    if response == "MDL,BCD325P2":
                        print(f"Scanner found on port {port.device}")
                        return port.device
            except Exception as e:
                print(f"Error on port {port.device}: {e}")
        print(
            (
                "Scanner not found. Please plug in and turn on the scanner. "
                "Retrying in 5 seconds..."
            )
        )
        time.sleep(5)


def read_response(ser, timeout=0.5):
    """
    Read a response from the serial port until a CR or LF is encountered.

    Read bytes from the serial port until a CR or LF is encountered
    or the timeout expires.
    """
    response_bytes = bytearray()
    start_time = time.time()
    while True:
        if ser.in_waiting:
            byte = ser.read(1)
            if byte in b"\r\n":
                break
            response_bytes.extend(byte)
        if time.time() - start_time > timeout:
            break
    return response_bytes.decode("utf-8", errors="ignore").strip()


def send_command(ser, cmd):
    """
    Send a command to the scanner and return the response..

    Sends a command (with CR/LF termination) to the scanner and
    returns the response using read_response().
    """
    full_cmd = cmd + "\r\n"
    try:
        ser.write(full_cmd.encode("utf-8"))
    except Exception as e:
        print(f"Error sending command {cmd}: {e}")
        return ""
    return read_response(ser)


def test_all_commands(ser):
    """
    Test all three-letter commands (AAA to ZZZ) on the scanner.

    Iterates over all three-letter combinations (AAA to ZZZ, skipping "PRG"
    and "POF", include other functions as they cause failures or multi-line
    received messages lag behind transmissions.), sends each command to the
    scanner, logs each result to a progress file as we go, and returns the list
    of results.
    """
    results = []
    letters = string.ascii_uppercase
    total = 26**3 - 4  # subtracting "PRG", "POF", "MNU", "STS"
    count = 0
    progress_filename = "commands_progress.txt"
    with open(progress_filename, "w") as f:
        for combo in itertools.product(letters, repeat=3):
            cmd = "".join(combo)
            if cmd in ("PRG", "POF", "MNU", "STS"):
                continue
            count += 1
            try:
                response = send_command(ser, cmd)
                if response.startswith(f"{cmd}:"):
                    print(
                        f"Mismatch detected for {cmd}. Received: {response}."
                        "Retrying..."
                    )
                    ser.reset_input_buffer()
                    ser.reset_output_buffer()
                    time.sleep(0.2)
                    return

            except Exception as e:
                response = f"Exception: {e}"
                f.write(f"{cmd}: {response}\n")
                f.flush()
                results.append((cmd, response))
                raise
            results.append((cmd, response))
            f.write(f"{cmd}: {response}\n")
            if count % 100 == 0:
                print(f"Tested {count}/{total} commands")
            f.flush()  # ensure immediate writing to file
    print(f"Progress written to {progress_filename}")
    return results


def sort_results(results):
    """
    Sorts the command results based on the response.

    Sorts the results so that commands with a response ending in ",NG" appear
    first, followed by other responses (alphabetically by command).
    """
    valid = []
    invalid = []
    others = []
    for cmd, response in results:
        if response.endswith(",NG"):
            valid.append((cmd, response))
        elif response.endswith(",ERR"):
            invalid.append((cmd, response))
        else:
            others.append((cmd, response))
    valid.sort(key=lambda x: x[0])
    invalid.sort(key=lambda x: x[0])
    others.sort(key=lambda x: x[0])
    # Place valid commands at the top
    sorted_results = valid + others + invalid
    return sorted_results


def write_results_to_file(sorted_results, filename="commands.txt"):
    """
    Write the sorted command results to a file.

    Writes the sorted command results to a file.
    Each line in the file is formatted as "COMMAND: RESPONSE".
    """
    with open(filename, "w") as f:
        for cmd, response in sorted_results:
            f.write(f"{cmd}: {response}\n")
    print(f"Sorted results written to {filename}")


def main():
    """
    Find the scanner, test commands, and save results.

    This function searches for the Uniden BCD325P2 scanner, tests all
    three-letter commands, sorts the results, and writes them to a file.
    """
    baudrate = 115200  # Updated baud rate
    print("Searching for Uniden BCD325P2 scanner...")
    port = find_scanner_port(baudrate=baudrate, timeout=0.5)

    try:
        ser = serial.Serial(port, baudrate, timeout=0.5)
        ser.reset_input_buffer()
        ser.reset_output_buffer()
    except Exception as e:
        print(f"Error opening scanner port {port}: {e}")
        return

    print(
        "Starting command test over all 3-letter combinations (excluding PRG "
        "and POF)..."
    )
    results = []
    try:
        results = test_all_commands(ser)
    except Exception as e:
        print(f"An error occurred during command testing: {e}")
        # Continue to sort and write the progress that we have so far

    print("Sorting results...")
    sorted_results = sort_results(results)
    write_results_to_file(sorted_results, "commands.txt")

    ser.close()


if __name__ == "__main__":
    main()
