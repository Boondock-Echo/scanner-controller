"""
BC125AT Scanner Adapter Module.

This module provides an adapter for the Uniden BC125AT scanner model, allowing
control and communication with the device through serial commands.
"""

import sys
import time

from adapters.uniden.uniden_base_adapter import UnidenScannerAdapter
from command_libraries.uniden.bc125at_commands import commands
from utilities.scanner_utils import send_command


def hex32(value):
    """Convert an integer to a 32-bit hexadecimal string."""
    return f"{value:08X}"


def update_progress(current, total):
    """Display a progress bar for long-running operations."""
    percent = int(100 * current / total)
    bar = "#" * (percent // 2)
    sys.stdout.write(f"\rProgress: [{bar:<50}] {percent}%")
    sys.stdout.flush()
    if current == total:
        sys.stdout.write("\n")
        sys.stdout.flush()


class BC125ATAdapter(UnidenScannerAdapter):
    """Adapter for the BC125AT scanner."""

    def __init__(self, machine_mode=False):
        """Initialize the BC125AT adapter.

        Args:
            machine_mode: Whether to use machine-readable output format.
        """
        super().__init__(machine_mode, commands)
        # Add machine_mode attribute for compatibility with tests and other
        self.machine_mode_id = "BC125AT"

    def feedback(self, success, message):
        """Format feedback based on machine_mode setting.

        Args:
            success: Whether the operation was successful.
            message: The feedback message.

        Returns:
            str: Formatted feedback message.
        """
        if self.machine_mode:
            return "OK" if success else "ERROR"
        return message

    def getHelp(self, command):
        """Get help for a specific BC125AT command.

        Args:
            command: The command to get help for.

        Returns:
            str: Help text for the command.
        """
        try:
            cmd = self.commands.get(command.upper())
            if cmd and cmd.help:
                return cmd.help
            return f"No help available for {command}"
        except Exception as e:
            return self.feedback(False, f"Error retrieving help: {e}")

    def readRSSI(self, ser):
        """Read the signal strength from the BC125AT.

        Args:
            ser: Serial connection to the scanner.

        Returns:
            float or str: RSSI value as float or error message.
        """
        try:
            response = self.send_command(ser, self.commands["PWR"].buildCommand())
            parts = response.split(",")
            if len(parts) == 3:
                return round(int(parts[1]) / 1023.0, 3)
            return self.feedback(False, f"Unexpected PWR response: {response}")
        except Exception as e:
            return self.feedback(False, f"Error reading RSSI: {e}")

    def readBatteryVoltage(self, ser):
        """Read the battery voltage from the BC125AT.

        Args:
            ser: Serial connection to the scanner.

        Returns:
            float or str: Battery voltage or error message.
        """
        try:
            response = self.send_command(ser, self.commands["BAV"].buildCommand())
            _, val = response.split(",")
            voltage = (3.2 * int(val) * 2) / 1023
            return round(voltage, 3)
        except Exception as e:
            return self.feedback(False, f"Error reading battery voltage: {e}")

    def readWindowVoltage(self, ser):
        """Read the window voltage from the BC125AT.

        Args:
            ser: Serial connection to the scanner.

        Returns:
            str: Window voltage response or error message.
        """
        try:
            return self.send_command(ser, self.commands["WIN"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"Error reading window voltage: {e}")

    def readStatus(self, ser):
        """Read the scanner status from the BC125AT.

        Args:
            ser: Serial connection to the scanner.

        Returns:
            str: Status response or error message.
        """
        try:
            return self.send_command(ser, self.commands["STS"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"Error reading status: {e}")

    def readSMeter(self, ser):
        """S-meter (not supported on BC125AT).

        Args:
            ser: Serial connection to the scanner.

        Returns:
            str: Error message indicating feature not supported.
        """
        return self.feedback(False, "S-Meter not supported on BC125AT")

    def readFrequency(self, ser):
        """Read the current frequency from the BC125AT.

        Args:
            ser: Serial connection to the scanner.

        Returns:
            str: Frequency information or error message.
        """
        try:
            response = self.send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                freq_mhz = (int(parts[2]) * 100) / 1_000_000
                return self.feedback(True, f"Frequency: {freq_mhz} MHz")
            return self.feedback(False, f"Unexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"Error reading frequency: {e}")

    def writeFrequency(self, ser, freq):
        """Set frequency (not directly supported on BC125AT).

        Args:
            ser: Serial connection to the scanner.
            freq: Frequency to set.

        Returns:
            str: Error message indicating feature not supported.
        """
        return self.feedback(False, "Frequency input not supported via direct command.")

    def sendKey(self, ser, keySeq):
        """Simulate key presses on the BC125AT.

        Args:
            ser: Serial connection to the scanner.
            keySeq: Sequence of keys to press.

        Returns:
            str: Combined response from all key presses.
        """
        if not keySeq:
            return self.feedback(False, "No key(s) provided.")

        responses = []
        for char in keySeq:
            if char not in "0123456789<>^.EMFHSLP":
                responses.append(f"{char} → skipped (invalid key)")
                continue
            try:
                response = self.send_command(ser, f"KEY,{char},P")
                responses.append(f"{char} → {response}")
            except Exception as e:
                responses.append(f"{char} → ERROR: {e}")
        return "\n".join(responses)

    def dumpMemoryToFile(
        self, ser, filename="memorydump.txt", start=0x00010000, end=0x0001FFFF, step=16
    ):
        """Dump scanner memory to a file.

        Args:
            ser: Serial connection to the scanner.
            filename: Output filename.
            start: Starting memory address.
            end: Ending memory address.
            step: Memory chunk size.

        Returns:
            str: Status message after dump attempt.
        """
        try:
            self.enterProgrammingMode(ser)
            total_steps = ((end - start) // step) + 1
            valid_count, invalid_streak = 0, 0
            MAX_INVALID = 4096
            with open(filename, "w") as f:
                for i in range(total_steps):
                    addr = start + i * step
                    cmd = f"MRD,{hex32(addr)}"
                    response = self.send_command(ser, cmd)
                    if response.startswith("MRD,"):
                        f.write(response + "\n")
                        valid_count += 1
                        invalid_streak = 0
                    elif "ERR" in response or "NG" in response:
                        invalid_streak += 1
                    else:
                        f.write(f"# Unexpected: {response}\n")
                        invalid_streak += 1
                    if invalid_streak >= MAX_INVALID:
                        return self.feedback(
                            False, f"Aborted early — {MAX_INVALID} invalids."
                        )
                    update_progress(i, total_steps)
            self.exitProgrammingMode(ser)
            return self.feedback(
                True, f"{valid_count} MRD entries written to {filename}"
            )
        except Exception as e:
            try:
                self.exitProgrammingMode(ser)
            except Exception:  # Specified exception type
                pass
            return self.feedback(False, f"Memory Dump Error: {e}")

    def readGlobalLockout(self, ser):
        """Read global lockout frequencies.

        Args:
            ser: Serial connection to the scanner.

        Returns:
            str: Lockout frequency data or error message.
        """
        try:
            self.enterProgrammingMode(ser)
            results = []
            while True:
                response = self.send_command(ser, self.commands["GLF"].buildCommand())
                if response.strip() == "GLF,-1":
                    break
                results.append(response.strip())
            self.exitProgrammingMode(ser)
            return "\n".join(results)
        except Exception as e:
            return self.feedback(False, f"Error reading global lockout: {e}")

    def readChannelInfo(self, ser, index):
        """Read channel information.

        Args:
            ser: Serial connection to the scanner.
            index: Channel index.

        Returns:
            str: Channel information or error message.
        """
        try:
            self.enterProgrammingMode(ser)
            response = self.send_command(ser, f"CIN,{index}")
            self.exitProgrammingMode(ser)
            return response
        except Exception as e:
            return self.feedback(False, f"Error reading channel info: {e}")

    def writeChannelInfo(
        self, ser, index, name, freq_khz, mod, ctcss, delay, lockout, priority
    ):
        """Write channel information.

        Args:
            ser: Serial connection to the scanner.
            index: Channel index.
            name: Channel name.
            freq_khz: Frequency in kHz.
            mod: Modulation type.
            ctcss: CTCSS tone.
            delay: Delay setting.
            lockout: Lockout status.
            priority: Priority status.

        Returns:
            str: Status message after write attempt.
        """
        try:
            self.enterProgrammingMode(ser)
            parts = [
                str(index),
                name[:16],
                str(freq_khz),
                mod.upper(),
                str(ctcss),
                str(delay),
                str(lockout),
                str(priority),
                "0",  # ATT
                "0",  # ALT
                "0",  # ALTL
                "",
                "",
                "",
                "",  # RSV
                "0",  # AUDIO_TYPE
                "0",  # P25NAC
                "0",  # NUMBER_TAG
                "OFF",  # ALT_COLOR
                "0",  # ALT_PATTERN
                "0",  # VOL_OFFSET
            ]
            response = self.send_command(ser, f"CIN,{','.join(parts)}")
            self.exitProgrammingMode(ser)
            return self.feedback(
                "OK" in response, f"Channel {index} written → {response}"
            )
        except Exception as e:
            return self.feedback(False, f"Error writing channel info: {e}")

    def enter_quick_frequency_hold(self, ser, freq_mhz):
        """Enter a frequency in quick hold mode.

        Args:
            ser: Serial connection to the scanner.
            freq_mhz: Frequency in MHz.

        Returns:
            str: Status message after frequency entry.
        """
        try:
            send_command(ser, "PRG")
            time.sleep(0.2)
            send_command(ser, "EPG")
            time.sleep(0.2)
            send_command(ser, "KEY,S,P")
            time.sleep(0.1)
            send_command(ser, "KEY,S,P")
            time.sleep(0.1)
            send_command(ser, "KEY,H,P")
            time.sleep(0.1)
            freq_str = f"{freq_mhz:.3f}"
            for char in freq_str:
                if char in "0123456789.":
                    send_command(ser, f"KEY,{char},P")
                    time.sleep(0.05)
            send_command(ser, "KEY,H,P")
            time.sleep(0.3)
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                actual_freq = int(parts[2]) / 10000.0
                if abs(actual_freq - freq_mhz) < 0.005:
                    return self.feedback(
                        True,
                        f"✅ Frequency {freq_str} MHz entered and confirmed via PWR "
                        f"({actual_freq:.5f} MHz)",
                    )
                else:
                    return self.feedback(
                        False,
                        f"⚠️ Entered {freq_str} MHz, but PWR returned "
                        f"{actual_freq:.5f} MHz",
                    )
            return self.feedback(False, f"❌ PWR returned unexpected: {response}")
        except Exception as e:
            return self.feedback(False, f"❌ [enter_quick_frequency_hold Error] {e}")
