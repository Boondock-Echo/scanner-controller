"""
This module provides utilities for interacting with Uniden scanners.

It includes commands for reading and writing settings, handling serial
communication, and
performing memory dumps.
"""

# Standard library imports
import logging
import time

import serial

import library_scanner

# Third-party imports
from adapter_scanner.base_adapter import BaseScannerAdapter
from adapter_scanner.scanner_utils import (
    clear_serial_buffer,
    read_response,
    send_command,
)
from library_scanner.bc125at_command_library import (
    Commands,  # Assuming this is the correct location
)


class UnidenAdapter(BaseScannerAdapter):
    """
    Adapter class to interact with Uniden scanners.

    Provides methods for sending commands, reading responses, and
    managing scanner settings.
    """

    def __init__(self, machine_mode=False):
        """
        Initialize the UnidenAdapter instance.

        Args:
            machine_mode (bool): If True, enables machine-readable feedback.
        """
        self.machine_mode = machine_mode

    def feedback(self, success, message):
        """
        Provide feedback based on the success of an operation.

        Args:
            success (bool): Indicates if the operation was successful.
            message (str): The message to return if not in machine mode.

        Returns:
            str: "OK" or "ERROR" if in machine mode, otherwise the provided
            message.
        """
        if self.machine_mode:
            return "OK" if success else "ERROR"
        return message

    def get_help(self, command):
        """
        Retrieve and display help information for a specified command.

        Args:
            command (str): The command for which help information is requested.

        Returns:
            str: Help information for the command or an error message if
            unavailable.
        """
        try:
            return library_scanner.bc125at_command_library.getHelp(command)
        except Exception as e:
            return self.feedback(False, f"❌\t[get_help Error] {e}")

    def dump_memory_to_file(
        self,
        ser,
        filename="memorydump.txt",
        start=0x00000000,
        end=0x0000FFFF,
        step=16,
    ):
        """
        Dump the memory of the scanner to a file.

        Args:
            ser (serial.Serial): The serial connection to the scanner.
            filename (str): The name of the file to save the memory dump.
            start (int): The starting memory address.
            end (int): The ending memory address.
            step (int): The step size for memory reads.

        Returns:
            str: Feedback message indicating success or failure.
        """
        import sys

        def hex32(i):
            return f"{i:08X}"

        def update_progress(current, total):
            percent = int(100 * current / total)
            if percent > update_progress.last_shown:
                update_progress.last_shown = percent
                bar = "#" * (percent // 2)
                sys.stdout.write(f"\rProgress: [{bar:<50}] {percent}%")
                sys.stdout.flush()

        update_progress.last_shown = -1

        try:
            send_command(ser, "PRG")
            total_steps = ((end - start) // step) + 1
            valid_count, invalid_streak = 0, 0
            MAX_INVALID = 4096
            with open(filename, "w") as f:
                for i in range(total_steps):
                    addr = start + i * step
                    cmd = f"MRD,{hex32(addr)}"
                    response = send_command(ser, cmd)
                    if response.startswith("MRD,"):
                        f.write(response + "\n")
                        valid_count += 1
                        invalid_streak = 0
                    elif "ERR" in response or "NG" in response:
                        invalid_streak += 1
                    else:
                        f.write(f"❌ # Unexpected: {response}\n")
                        invalid_streak += 1
                    if invalid_streak >= MAX_INVALID:
                        return self.feedback(
                            False,
                            f"❌ \nAborted early — {MAX_INVALID} " "invalids.",
                        )
                    update_progress(i, total_steps)
            send_command(ser, "EPG")
            return self.feedback(
                True, f"{valid_count} MRD entries written to {filename}"
            )
        except Exception as e:
            try:
                send_command(ser, "EPG")
            except Exception:
                pass
            return self.feedback(False, f"[Memory Dump Error] {e}")

    def clear_serial_buffer(ser):
        """
        Clear accumulated data in the serial buffer before sending commands.

        Clears any leftover data from previous commands to ensure the scanner
        is ready for new commands. This prevents interference from old data.
        """
        try:
            time.sleep(0.2)
            while ser.in_waiting:
                ser.read(ser.in_waiting)
            logging.debug("Serial buffer cleared.")
        except Exception as e:
            logging.error(f"Error clearing serial buffer: {e}")

    def read_response(ser, timeout=1.0):
        r"""
        Read bytes from the serial port until a carriage return is encountered.

        This method processes incoming data from the serial port and stops
        reading when a carriage return character is detected.
        """
        response_bytes = bytearray()
        try:
            while True:
                byte = ser.read(1)
                if not byte:
                    break  # timeout reached
                if byte in b"\r\n":
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
        Clear the buffer and send a command (with CR termination).

        Command is sent to the scanner and the response is read.
        The command is terminated with a carriage return (CR) character.

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
        Wait up to max_wait seconds for incoming data on the serial port.

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
        Scan all COM ports and returns a list of tuples.

        Each tuple contains the port name and model code of the detected
        scanner. (port_name, model_code).
        """
        from serial.tools import list_ports

        detected = []
        retries = 0
        while retries < max_retries:
            ports = list_ports.comports()
            for port in ports:
                try:
                    with serial.Serial(
                        port.device, baudrate, timeout=timeout
                    ) as ser:
                        ser.write(b"MDL\r")
                        response = read_response(ser)
                        if response.startswith("MDL"):
                            model_code = response.split(",")[1].strip()
                            detected.append((port.device, model_code))
                except Exception:
                    continue
            retries += 1
        return detected

    def enter_quick_frequency_hold(ser, freq_mhz):
        """
        Enter quick frequency hold mode on the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.
            freq_mhz (float): The frequency in MHz to hold.

        Returns:
            None
        """

        def write_key_beep(self, ser, level=99, lock=0):
            try:
                send_command(ser, "PRG")
                cmd = Commands["KBP"]
                response = send_command(
                    ser, cmd.buildCommand(f"{level},{lock}")
                )
                send_command(ser, "EPG")
                return self.feedback(
                    True,
                    f"✅ Set key beep to {level}, lock to {lock} →"
                    f"{response}",
                )
            except Exception as e:
                return self.feedback(False, f"[writeKeyBeep Error] {e}")

    def read_volume(self, ser):
        """
        Read the current volume level from the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.

        Returns:
            str: Feedback message indicating the volume level or an error
            message.
        """
        try:
            response = send_command(ser, Commands["VOL"].buildCommand())
            _, value = response.split(",", 1)
            volume = float(int(value.strip()) / 15.0)
            return self.feedback(True, f"✅ Volume level: {volume:.2f}")
        except Exception as e:
            return self.feedback(False, f"❌ [readVolume Error] {e}")

    def write_volume(self, ser, value):
        """
        Set the volume level on the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.
            value (float): The desired volume level, between 0.0 and 1.0.

        Returns:
            str: Feedback message indicating success or failure.
        """
        try:
            if not (0.0 <= value <= 1.0):
                return self.feedback(
                    False, "⚠️ Volume must be between 0.0 " "and 1.0"
                )
            scaled = int(round(value * 15))
            response = send_command(ser, Commands["VOL"].buildCommand(scaled))
            return self.feedback(
                "OK" in response, f"✅ Volume set to {value:.2f} → {response}"
            )
        except Exception as e:
            return self.feedback(False, f"❌ [writeVolume Error] {e}")

    def read_squelch(self, ser):
        """
        Read the current squelch level from the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.

        Returns:
            str: Feedback message indicating the squelch level or an error "
            "message.
        """
        try:
            response = send_command(ser, Commands["SQL"].buildCommand())
            _, value = response.split(",", 1)
            squelch = float(int(value.strip()) / 15.0)
            return self.feedback(True, f"✅ Squelch level: {squelch:.2f}")
        except Exception as e:
            return self.feedback(False, f"❌ [readSquelch Error] {e}")

    def write_squelch(self, ser, value):
        """
        Set the squelch level on the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.
            value (float): The desired squelch level, between 0.0 and 1.0.

        Returns:
            str: Feedback message indicating success or failure.
        """
        try:
            if not (0.0 <= value <= 1.0):
                return self.feedback(
                    False, "❌ Squelch must be between 0.0 " "and 1.0"
                )
            scaled = int(round(value * 15))
            send_command(ser, "PRG")
            response = send_command(ser, Commands["SQL"].buildCommand(scaled))
            send_command(ser, "EPG")
            return self.feedback(
                "OK" in response, f"✅Squelch set to {value:.2f} → {response}"
            )
        except Exception as e:
            return self.feedback(False, f"❌ [writeSquelch Error] {e}")

    def read_frequency(self, ser):
        """
        Read the current frequency from the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.

        Returns:
            str: Feedback message indicating the frequency in MHz or an error
            message.
        """
        try:
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                freq_mhz = (int(parts[2]) * 100) / 1_000_000
                return self.feedback(
                    True, "✅ Frequency:" f" {round(freq_mhz, 5)} MHz"
                )
            return self.feedback(False, f"❌ Unexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [readFrequency Error] {e}")

    def write_frequency(self, ser, freq_mhz):
        """
        Set the scanner to a specific frequency.

        Args:
            ser (serial.Serial): The serial connection to the scanner.
            freq_mhz (float): The desired frequency in MHz.

        Returns:
            str: Feedback message indicating success or failure.
        """
        try:
            send_command(ser, "PRG")
            send_command(ser, "EPG")
            time.sleep(0.1)
            for _ in range(2):
                send_command(ser, "KEY,S")
                time.sleep(0.2)
                send_command(ser, "KEY,H")
            freq_str = f"{float(freq_mhz):.3f}"
            for char in freq_str:
                if char in "0123456789.":
                    send_command(ser, f"KEY,{char}")
                    time.sleep(0.1)
            send_command(ser, "KEY,E")
            return self.feedback(
                True, f"✅ Frequency {freq_str} MHz entered via keypress"
            )
        except Exception as e:
            return self.feedback(False, f"❌ [writeFrequency Error] {e}")

    def read_rssi(self, ser):
        """
        Read the Received Signal Strength Indicator (RSSI) from the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.

        Returns:
            str: Feedback message indicating the RSSI value or an error message.
        """
        try:
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                rssi = round(int(parts[1]) / 1023.0, 3)
                return self.feedback(True, f"✅ RSSI: {rssi}")
            return self.feedback(False, f"❌ Unexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [readRSSI Error] {e}")

    def send_key(self, ser, key_seq):
        """
        Send a sequence of keypresses to the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.
            key_seq (str): A string representing the sequence of keys to send.

        Returns:
            str: Feedback message indicating the result of each keypress.
        """
        if not key_seq:
            return self.feedback(False, "❌ No key(s) provided.")

        responses = []
        for char in key_seq:
            if char not in "0123456789<>^.EMFHSLP":
                responses.append(f"{char} → skipped (invalid key)")
                continue
            try:
                response = send_command(ser, f"KEY,{char},P")
                responses.append(f"✅ {char} → {response}")
            except Exception as e:
                responses.append(f"❌ {char} → ERROR: {e}")
        return "\n".join(responses)

    def read_model(self, ser):
        """
        Read the model information from the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.

        Returns:
            str: Feedback message indicating the model information or an error
            message.
        """
        try:
            model = send_command(ser, Commands["MDL"].buildCommand())
            return self.feedback(True, f"✅ Model: {model}")
        except Exception as e:
            return self.feedback(False, f"❌ [readModel Error] {e}")

    def read_sw_ver(self, ser):
        """
        Read the software version of the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.

        Returns:
            str: Feedback message indicating the software version or an error
            message.
        """
        try:
            version = send_command(ser, Commands["VER"].buildCommand())
            return self.feedback(True, f"✅ Software Version: {version}")
        except Exception as e:
            return self.feedback(False, f"❌ [readSWVer Error] {e}")

    def read_s_meter(self, ser):
        """
        Attempt to read the S-meter value from the scanner.

        Args:
            ser (serial.Serial): The serial connection to the scanner.

        Returns:
            str: Feedback message indicating that the S-meter is not supported.
        """
        return self.feedback(False, "❌ SMeter not supported")
