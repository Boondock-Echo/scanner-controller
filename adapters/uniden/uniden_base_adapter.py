import logging
import time

from adapters.base_adapter import BaseScannerAdapter


class UnidenScannerAdapter(BaseScannerAdapter):
    """
    Base adapter for Uniden scanners with common Uniden-specific functionality.
    """

    def __init__(self, machine_mode=False, commands=None):
        super().__init__(machine_mode)
        self.commands = commands or {}
        self.in_program_mode = False

    def send_command(self, ser, command, timeout=1.0, retries=1):
        """
        Send a command to the scanner and get the response
        """
        if not command.endswith("\r"):
            command += "\r"

        for attempt in range(retries):
            try:
                # Clear buffers
                ser.reset_input_buffer()
                ser.reset_output_buffer()

                # Send command
                ser.write(command.encode())

                # Wait for response
                start_time = time.time()
                while time.time() - start_time < timeout:
                    if ser.in_waiting > 0:
                        # Read response
                        response = ser.read(ser.in_waiting).decode(
                            "utf-8", errors="ignore"
                        )
                        if response.strip():
                            return response.strip()
                    time.sleep(0.05)

                logging.warning(
                    f"Command timed out: {command.strip()} (attempt {attempt+1})"
                )
            except Exception as e:
                logging.error(f"Error sending command: {str(e)}")
                if attempt == retries - 1:
                    raise

        return "NO_RESPONSE"

    def enterProgrammingMode(self, ser):
        """
        Enter programming mode for Uniden scanners
        """
        if self.in_program_mode:
            return "Already in programming mode"

        try:
            response = self.send_command(ser, "PRG")
            if "OK" in response:
                self.in_program_mode = True
                return "Entered programming mode"
            return f"Failed to enter programming mode: {response}"
        except Exception as e:
            return f"Error entering programming mode: {e}"

    def exitProgrammingMode(self, ser):
        """
        Exit programming mode for Uniden scanners
        """
        if not self.in_program_mode:
            return "Not in programming mode"

        try:
            response = self.send_command(ser, "EPG")
            if "OK" in response:
                self.in_program_mode = False
                return "Exited programming mode"
            return f"Failed to exit programming mode: {response}"
        except Exception as e:
            return f"Error exiting programming mode: {e}"

    def readModel(self, ser):
        """
        Read the scanner model for Uniden scanners
        """
        try:
            return self.send_command(ser, self.commands["MDL"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"Error reading model: {e}")

    def readSWVer(self, ser):
        """
        Read the scanner firmware version for Uniden scanners
        """
        try:
            return self.send_command(ser, self.commands["VER"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"Error reading firmware version: {e}")

    def readVolume(self, ser):
        """
        Read the volume setting for Uniden scanners
        """
        try:
            response = self.send_command(ser, self.commands["VOL"].buildCommand())
            if "," in response:
                _, value = response.split(",", 1)
                return int(value)
            return 0
        except Exception as e:
            return self.feedback(False, f"Error reading volume: {e}")

    def writeVolume(self, ser, value):
        """
        Set the volume for Uniden scanners
        """
        try:
            response = self.send_command(ser, self.commands["VOL"].buildCommand(value))
            return "OK" in response
        except Exception as e:
            return self.feedback(False, f"Error setting volume: {e}")

    def readSquelch(self, ser):
        """
        Read the squelch setting for Uniden scanners
        """
        try:
            response = self.send_command(ser, self.commands["SQL"].buildCommand())
            if "," in response:
                _, value = response.split(",", 1)
                return int(value)
            return 0
        except Exception as e:
            return self.feedback(False, f"Error reading squelch: {e}")

    def writeSquelch(self, ser, value):
        """
        Set the squelch for Uniden scanners
        """
        try:
            response = self.send_command(ser, self.commands["SQL"].buildCommand(value))
            return "OK" in response
        except Exception as e:
            return self.feedback(False, f"Error setting squelch: {e}")
