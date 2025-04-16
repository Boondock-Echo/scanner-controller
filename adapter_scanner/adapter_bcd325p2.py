"""
This module provides an adapter for the Uniden BCD325P2 scanner.

It includes methods for interacting with the scanner, such as reading and
writing settings, handling commands, and managing memory dumps.
"""

from adapter_scanner.base_adapter import BaseScannerAdapter
from library_scanner.commands.commands_uniden_bcd325p2 import commands
from utilities.scanner_utils import send_command


def hex32(value):
    """Convert an integer to a 32-bit hexadecimal string with '0x' prefix."""
    return f"0x{value & 0xFFFFFFFF:08x}"


def update_progress(current, total):
    """Display a progress bar for long-running operations."""
    percent = min(100, int(current * 100 / total))
    bar_length = 30
    filled_length = int(bar_length * current // total)
    bar = "█" * filled_length + "░" * (bar_length - filled_length)
    print(f"\rProgress: |{bar}| {percent}% Complete", end="", flush=True)
    if current == total:
        print()


class BCD325P2Adapter(BaseScannerAdapter):
    """
    Adapter class for the Uniden BCD325P2 scanner.

    This class provides methods to interact with the scanner, including
    reading and writing settings, handling commands, and managing memory dumps.
    """

    def __init__(self, machineMode=False):
        """
        Initialize the BCD325P2Adapter.

        :param machineMode: If True, enables machine-readable feedback mode.
        """
        self.machineMode = machineMode

    def feedback(self, success, message):
        """
        Provide feedback based on the success of an operation.

        :param success: A boolean indicating if the operation was successful.
        :param message: A string containing the feedback message.
        :return: "OK" or "ERROR" if machineMode is enabled, otherwise the
        message.
        """
        if self.machineMode:
            return "OK" if success else "ERROR"
        return message

    def getHelp(self, command):
        """
        Retrieve help information for a specific scanner command.

        :param command: The command for which help information is requested.
        :return: A string containing the help information or an error message.
        """
        from library_scanner.commands.commands_uniden_bcd325p2 import commands

        try:
            return commands.getHelp(command)
        except Exception as e:
            return self.feedback(False, f"⚠️ [getHelp Error] {e}")

    def enterProgrammingMode(self, ser):
        """
        Enter programming mode on the scanner.

        :param ser: The serial connection to the scanner.
        :return: The response from the scanner after entering programming mode.
        """
        return send_command(ser, commands["PRG"].buildCommand())

    def exitProgrammingMode(self, ser):
        """
        Exit programming mode on the scanner.

        :param ser: The serial connection to the scanner.
        :return: The response from the scanner after exiting programming mode.
        """
        return send_command(ser, commands["EPG"].buildCommand())

    def readVolume(self, ser):
        """
        Read the current volume level from the scanner.

        :param ser: The serial connection to the scanner.
        :return: The volume level as a float between 0.0 and 1.0, or an error
        message.
        """
        try:
            response = send_command(ser, commands["VOL"].buildCommand())
            _, val = response.split(",")
            return int(val) / 15.0
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readVolume Error] {e}")

    def writeVolume(self, ser, value):
        """
        Set the volume level on the scanner.

        :param ser: The serial connection to the scanner.
        :param value: A float between 0.0 and 1.0 representing the desired
        volume level.
        :return: Feedback message indicating success or failure.
        """
        try:
            level = max(0, min(15, int(round(value * 15))))
            response = send_command(ser, commands["VOL"].buildCommand(level))
            return self.feedback(
                "OK" in response, f"✅\tVolume set to {level} → {response}"
            )
        except Exception as e:
            return self.feedback(False, f"⚠️\t[writeVolume Error] {e}")

    def readSquelch(self, ser):
        """
        Read the current squelch level from the scanner.

        :param ser: The serial connection to the scanner.
        :return: Feedback message with the squelch level or an error message.
        """
        try:
            response = send_command(ser, commands["SQL"].buildCommand())
            _, val = response.split(",")
            scaledSquelch = round(int(val) / 15.0, 2)
            return self.feedback(True, f"✅\tSquelch: {scaledSquelch}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readSquelch Error] {e}")

    def writeSquelch(self, ser, value):
        """
        Set the squelch level on the scanner.

        :param ser: The serial connection to the scanner.
        :param value: A float between 0.0 and 1.0 representing the desired
        squelch
            level.
        :return: Feedback message indicating success or failure.
        """
        try:
            level = max(0, min(15, int(round(value * 15))))
            response = send_command(ser, commands["SQL"].buildCommand(level))
            return self.feedback(
                "OK" in response, f"✅\tSquelch set to {level} → {response}"
            )
        except Exception as e:
            return self.feedback(False, f"⚠️\t[writeSquelch Error] {e}")

    def readModel(self, ser):
        """
        Read the model information from the scanner.

        :param ser: The serial connection to the scanner.
        :return: The model information as a string or an error message.
        """
        try:
            return send_command(ser, commands["MDL"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readModel Error] {e}")

    def readSWVer(self, ser):
        """
        Read the software version of the scanner.

        :param ser: The serial connection to the scanner.
        :return: The software version as a string or an error message.
        """
        try:
            return send_command(ser, commands["VER"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readSWVer Error] {e}")

    def readRSSI(self, ser):
        """
        Read the Received Signal Strength Indicator (RSSI) from the scanner.

        :param ser: The serial connection to the scanner.
        :return: The RSSI value as a float between 0.0 and 1.0, or an error
        message.
        """
        try:
            response = send_command(ser, commands["PWR"].buildCommand())
            parts = response.split(",")
            if len(parts) == 3:
                return round(int(parts[1]) / 1023.0, 3)
            return self.feedback(
                False, f"⚠️\tUnexpected PWR response:" f" {response}"
            )
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readRSSI Error] {e}")

    def readBatteryVoltage(self, ser):
        """
        Read the battery voltage from the scanner.

        :param ser: The serial connection to the scanner.
        :return: The battery voltage as a float or an error message.
        """
        try:
            response = send_command(ser, commands["BAV"].buildCommand())
            _, val = response.split(",")
            voltage = (3.2 * int(val) * 2) / 1023
            return round(voltage, 3)
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readBatteryVoltage Error] {e}")

    def readWindowVoltage(self, ser):
        """
        Read the window voltage from the scanner.

        :param ser: The serial connection to the scanner.
        :return: The window voltage as a string or an error message.
        """
        try:
            return send_command(ser, commands["WIN"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readWindowVoltage Error] {e}")

    def readStatus(self, ser):
        """
        Read the status information from the scanner.

        :param ser: The serial connection to the scanner.
        :return: The status information as a string or an error message.
        """
        try:
            return send_command(ser, commands["STS"].buildCommand())
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readStatus Error] {e}")

    def readSMeter(self, ser):
        """
        Read the S-Meter value from the scanner.

        :param ser: The serial connection to the scanner.
        :return: A feedback message indicating that the S-Meter is not
        supported.
        """
        return self.feedback(False, "⚠️\tSMeter not supported on BCD325P2")

    def readFrequency(self, ser):
        """
        Read the current frequency from the scanner.

        :param ser: The serial connection to the scanner.
        :return: Feedback message with the frequency in MHz or an error
        message.
        """
        try:
            response = send_command(ser, "PWR")
            parts = response.strip().split(",")
            if len(parts) == 3 and parts[0] == "PWR":
                freq_mhz = (int(parts[2]) * 100) / 1_000_000
                # return round(freq_mhz, 5)
                return self.feedback(False, f"✅\tFrequency: {freq_mhz} MHz")
            return self.feedback(False, f"⚠️\tUnexpected response: {response}")
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readFrequency Error] {e}")

    def writeFrequency(self, ser, freq):
        """
        Attempt to set the frequency on the scanner.

        :param ser: The serial connection to the scanner.
        :param freq: The desired frequency in MHz.
        :return: Feedback message indicating that this operation is not
        supported.
        """
        return self.feedback(
            False, "⚠️\tFrequency input not supported via direct command."
        )

    def sendKey(self, ser, keySeq):
        """
        Send a sequence of key presses to the scanner.

        :param ser: The serial connection to the scanner.
        :param keySeq: A string containing the sequence of keys to send.
        :return: A string summarizing the responses for each key press.
        """
        if not keySeq:
            return self.feedback(False, "⚠️\tNo key(s) provided.")

        responses = []
        for char in keySeq:
            if char not in "0123456789<>^.EMFHSLP":
                responses.append(f"{char} → skipped (invalid key)")
                continue
            try:
                response = send_command(ser, f"KEY,{char},P")
                responses.append(f"{char} → {response}")
            except Exception as e:
                responses.append(f"⚠️\t{char} → ERROR: {e}")
        return "\n".join(responses)

    def writeKeyBeep(self, ser, level=99, lock=0, safe=0):
        """
        Set the key beep settings on the scanner.

        :param ser: The serial connection to the scanner.
        :param level: The beep level (default is 99).
        :param lock: The lock setting (default is 0).
        :param safe: The safe setting (default is 0).
        :return: Feedback message indicating success or failure.
        """
        try:
            self.enterProgrammingMode(ser)
            payload = f"{level},{lock},{safe}"
            response = send_command(ser, f"KBP,{payload}")
            self.exitProgrammingMode(ser)
            return self.feedback(
                "OK" in response, "✅\tKey beep set →" f"{response}"
            )
        except Exception as e:
            return self.feedback(False, f"⚠️\t[writeKeyBeep Error] {e}")

    def dumpMemoryToFile(
        self,
        ser,
        filename="memorydump.txt",
        start=0x00010000,
        end=0x0001FFFF,
        step=16,
    ):
        """
        Dump the memory of the scanner to a file.

        :param ser: The serial connection to the scanner.
        :param filename: The name of the file to save the memory dump.
        :param start: The starting memory address for the dump.
        :param end: The ending memory address for the dump.
        :param step: The step size for reading memory.
        :return: Feedback message indicating success or failure.
        """
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
                        f.write(f"⚠️\t# Unexpected: {response}\n")
                        invalid_streak += 1
                    if invalid_streak >= MAX_INVALID:
                        return self.feedback(
                            False,
                            f"⚠️\t\nAborted early — {MAX_INVALID} invalids.",
                        )
                    update_progress(i, total_steps)
            send_command(ser, "EPG")
            return self.feedback(
                True, f"✅\t{valid_count} MRD entries written to {filename}"
            )
        except Exception as e:
            try:
                send_command(ser, "EPG")
            except Exception:
                pass
            return self.feedback(False, f"⚠️\t[Memory Dump Error] {e}")

    def enter_quick_frequency_hold(self, ser, freq_mhz):
        """
        Enter quick frequency hold mode on the scanner.

        :param ser: The serial connection to the scanner.
        :param freq_mhz: The desired frequency in MHz to hold.
        :return: Feedback message indicating success or failure.
        """
        # example: QSH,00893000,,FMB,0,0,,0,1011111111111111,0,,1,0,0
        # example: QSH,00893000
        try:
            freq_str = f"{float(freq_mhz):08.5f}"
            freqHectoHertz = round(int(freq_mhz * 1_000_000 / 100))
            command = f"QSH,{freqHectoHertz}"
            response = send_command(ser, command)
            if response.startswith("QSH,OK"):
                return self.feedback(
                    True, "Entered frequency hold at" f"{freq_str} MHz"
                )
            return self.feedback(
                False, f"⚠️\tFailed to enter frequency hold: {response}"
            )
        except Exception as e:
            return self.feedback(
                False, f"⚠️\t[enter_quick_frequency_hold Error] {e}"
            )

    def readGlobalLockout(self, ser):
        """
        Read the global lockout frequencies from the scanner.

        :param ser: The serial connection to the scanner.
        :return: A string containing the global lockout frequencies or an error
        message.
        """
        try:
            self.enterProgrammingMode(ser)
            results = []
            while True:
                response = send_command(ser, commands["GLF"].buildCommand())
                if response.strip() == "GLF,-1":
                    break
                results.append(response.strip())
            self.exitProgrammingMode(ser)
            return "\n".join(results)
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readGlobalLockout Error] {e}")

    def readChannelInfo(self, ser, index):
        """
        Read information about a specific channel from the scanner.

        :param ser: The serial connection to the scanner.
        :param index: The index of the channel to read.
        :return: The channel information as a string or an error message.
        """
        try:
            self.enterProgrammingMode(ser)
            response = send_command(ser, f"CIN,{index}")
            self.exitProgrammingMode(ser)
            return response
        except Exception as e:
            return self.feedback(False, f"⚠️\t[readChannelInfo Error] {e}")

    def writeChannelInfo(
        self, ser, index, name, freq_khz, mod, ctcss, delay, lockout, priority
    ):
        """
        Write information to a specific channel on the scanner.

        :param ser: The serial connection to the scanner.
        :param index: The index of the channel to write.
        :param name: The name of the channel (max 16 characters).
        :param freq_khz: The frequency in kHz.
        :param mod: The modulation type (e.g., AM, FM).
        :param ctcss: The CTCSS tone frequency.
        :param delay: The delay time in seconds.
        :param lockout: Lockout status (0 for unlocked, 1 for locked).
        :param priority: Priority status (0 for normal, 1 for priority).
        :return: Feedback message indicating success or failure.
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
            response = send_command(ser, f"CIN,{','.join(parts)}")
            self.exitProgrammingMode(ser)
            return self.feedback(
                "OK" in response, f"✅\tChannel {index} written → {response}"
            )
        except Exception as e:
            return self.feedback(False, f"⚠️\t[writeChannelInfo Error] {e}")

    def send_command(self, ser, cmd):
        """Wrap the send_command function to maintain consistency."""
        return send_command(ser, cmd)


"""
class BC325P2Adapter(BaseScannerAdapter):
"""
